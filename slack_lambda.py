import logging
import os
import base64
import requests

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

from utils.chatbot_helper import (
    initialize_bedrock_client,
    initialize_knowledge_base_retriever,
    initialize_llm,
    retrieve_context,
)

from utils.prompts import (
    question_system_prompt,
    slack_system_prompt_with_followups as slack_system_prompt,
)

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# process_before_response must be True when running on FaaS
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True
)

# LangChain Initializations - Initialize lazily to avoid Lambda cold start issues
bedrock_client = None
llm = None
retriever = None
bot_user_id = None
bot_id_from_auth = None

def initialize_services():
    global bedrock_client, llm, retriever, bot_user_id, bot_id_from_auth
    
    if llm is None or retriever is None:
        try:
            bedrock_client = initialize_bedrock_client()
            llm = initialize_llm(client=bedrock_client)
            retriever = initialize_knowledge_base_retriever()
            logger.info("Bedrock client, LLM, and Retriever initialized successfully.")
        except Exception as e:
            logger.error(
                f"Error initializing AWS services or LangChain components: {e}", exc_info=True
            )
            raise e
    
    if bot_user_id is None:
        try:
            auth_test = app.client.auth_test()
            bot_user_id = auth_test["user_id"]
            bot_id_from_auth = auth_test.get("bot_id")
            logger.info(f"Bot User ID: {bot_user_id}, Bot ID from auth: {bot_id_from_auth}")
        except Exception as e:
            logger.error(
                f"Error fetching bot_user_id: {e}. Mention parsing and self-message filtering might be affected.",
                exc_info=True,
            )
            raise e

# Function to Reconstruct Conversation History from Slack
def reconstruct_history_from_slack(client, channel_id, thread_ts):
    if not bot_user_id:
        logger.error("Cannot reconstruct history: bot_user_id is not set.")
        return [SystemMessage(content=slack_system_prompt)]

    history = [SystemMessage(content=slack_system_prompt)]
    try:
        result = client.conversations_replies(
            channel=channel_id, ts=thread_ts, limit=200
        )
        messages = result.get("messages", [])
        logger.info(
            f"Fetched {len(messages)} messages from Slack for thread {thread_ts}."
        )

        for msg in sorted(messages, key=lambda x: float(x["ts"])):
            msg_text = msg.get("text", "")
            msg_user = msg.get("user")
            msg_bot_id = msg.get("bot_id")

            if msg_bot_id == bot_id_from_auth or msg_user == bot_user_id:
                if msg_text:
                    history.append(AIMessage(content=msg_text))
            elif msg_user:
                # A HumanMessage can contain a list of content parts (text and images).
                message_content_parts = []

                # Part 1: Add the text content
                cleaned_text = msg_text
                if msg["ts"] == thread_ts:  # If it's the root message
                    cleaned_text = msg_text.replace(f"<@{bot_user_id}>", "").strip()

                if cleaned_text:
                    message_content_parts.append({"type": "text", "text": cleaned_text})

                # Part 2: Check for and add image content
                if msg.get("files"):
                    for file in msg.get("files", []):
                        if file.get("mimetype") in [
                            "image/jpeg",
                            "image/png",
                            "image/gif",
                            "image/webp",
                        ]:
                            logger.info(
                                f"Found image file in historical message {msg['ts']}: {file.get('name')}"
                            )
                            url_private = file.get("url_private")
                            if url_private:
                                try:
                                    # Add a timeout to the request (e.g., 10 seconds)
                                    timeout_seconds = 10
                                    response = requests.get(
                                        url_private,
                                        headers={
                                            "Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"
                                        },
                                        timeout=timeout_seconds,
                                    )
                                    logger.info(
                                        f"Image download status: {response.status_code}, size: {len(response.content)} bytes."
                                    )
                                    response.raise_for_status()  # This will raise an error for 4xx/5xx responses
                                    base64_image = base64.b64encode(
                                        response.content
                                    ).decode("utf-8")

                                    message_content_parts.append(
                                        {
                                            "type": "image",
                                            "source": {
                                                "type": "base64",
                                                "media_type": file.get("mimetype"),
                                                "data": base64_image,
                                            },
                                        }
                                    )
                                    logger.info(
                                        f"Successfully processed historical image: {file.get('name')}"
                                    )
                                except Exception as img_e:
                                    logger.error(
                                        f"Failed to download/process historical image {file.get('name')}: {img_e}",
                                        exc_info=True,
                                    )

                if message_content_parts:
                    history.append(HumanMessage(content=message_content_parts))

        logger.info(
            f"Reconstructed history for thread {thread_ts} with {len(history) - 1} turns."
        )
    except Exception as e:
        logger.error(
            f"Error reconstructing history from Slack for thread {thread_ts}: {e}",
            exc_info=True,
        )
        return [SystemMessage(content=slack_system_prompt)]
    return history


#  Shared Logic for Processing User Messages
def process_user_message_with_slack_history(
    client, channel_id, thread_ts_key, current_user_text_raw, files=None
):
    # Initialize services if not already done
    try:
        initialize_services()
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        return "Sorry, the AI service is currently unavailable. Please check the logs or contact an administrator."
    
    # Initialize services if not already done
    try:
        initialize_services()
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        return "Sorry, the AI service is currently unavailable. Please check the logs or contact an administrator."
    
    if not llm or not retriever:
        logger.error("LLM or Retriever not initialized. Cannot process message.")
        return "Sorry, the AI service is currently unavailable. Please check the logs or contact an administrator."

    logger.info(
        f"Processing user message for thread {thread_ts_key}. Raw input: '{current_user_text_raw}', Files: {len(files) if files else 0}"
    )

    current_thread_history = reconstruct_history_from_slack(
        client, channel_id, thread_ts_key
    )

    # Helper to extract text from multimodal messages for text-only processing
    def get_text_from_message(message):
        if isinstance(message.content, str):
            return message.content
        if isinstance(message.content, list):
            return " ".join(
                [part["text"] for part in message.content if part["type"] == "text"]
            )
        return ""

    # For query optimization, use a text-only representation of the history.
    text_only_history = [SystemMessage(content=question_system_prompt)]
    if len(current_thread_history) > 1:  # If there's more than the system prompt
        for msg in current_thread_history[1:]:  # Skip system prompt
            text_only_history.append(
                HumanMessage(content=get_text_from_message(msg))
                if isinstance(msg, HumanMessage)
                else msg
            )

    cleaned_current_user_text = (
        current_user_text_raw.replace(f"<@{bot_user_id}>", "").strip()
        if bot_user_id
        else current_user_text_raw.strip()
    )

    # Determine prompt for query optimization
    query_prompt_text = cleaned_current_user_text
    if not cleaned_current_user_text and not files:
        logger.warning(
            f"User message for thread {thread_ts_key} was empty. Using 'help' as query."
        )
        query_prompt_text = "help"
    elif not cleaned_current_user_text and files:
        query_prompt_text = (
            "Describe the attached image(s) in the context of our documentation."
        )

    # Construct messages for the query optimization LLM call
    messages_for_query_optimization_llm = text_only_history[
        :-1
    ]  # History up to before the current turn
    messages_for_query_optimization_llm.append(
        HumanMessage(
            content=f'Based on the conversation history (if any), generate an optimized search query for the following user question: "{query_prompt_text}"'
        )
    )

    logger.debug(
        f"Messages for query optimization LLM (thread {thread_ts_key}): {messages_for_query_optimization_llm}"
    )

    try:
        # Get the optimized query from the LLM based on text
        query_response = llm.invoke(messages_for_query_optimization_llm)
        optimized_query = query_response.content.strip()
        logger.info(
            f"Generated optimized query for thread {thread_ts_key}: '{optimized_query}'"
        )
        if not optimized_query:
            optimized_query = query_prompt_text

        # Retrieve context from knowledge base
        context, relevant_docs = retrieve_context(
            retriever=retriever, prompt=optimized_query
        )
        logger.debug(
            f"Retrieved context for thread {thread_ts_key} (first 100 chars): {str(context)[:100]}"
        )

        # Construct the multimodal message for the current user's turn
        current_turn_content_parts = []
        if cleaned_current_user_text:
            # The augmented prompt combines RAG context with the user's text
            augmented_text_prompt = (
                f"Context:\n{context}\n\nQuestion: {cleaned_current_user_text}"
            )
            current_turn_content_parts.append(
                {"type": "text", "text": augmented_text_prompt}
            )
        else:  # If there was no text, we still want to provide the RAG context
            augmented_text_prompt_for_image = f"Context:\n{context}\n\nUser question regarding the following image(s): Describe the image(s) and relate them to the provided context if possible."
            current_turn_content_parts.append(
                {"type": "text", "text": augmented_text_prompt_for_image}
            )

        # Process and add images from the current message
        if files:
            for file in files:
                if file.get("mimetype") in [
                    "image/jpeg",
                    "image/png",
                    "image/gif",
                    "image/webp",
                ]:
                    logger.info(
                        f"Processing image attached to current message: {file.get('name')}"
                    )
                    url_private = file.get("url_private")
                    if url_private:
                        try:
                            # Add a timeout to the request (e.g., 10 seconds)
                            timeout_seconds = 10
                            response = requests.get(
                                url_private,
                                headers={
                                    "Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"
                                },
                                timeout=timeout_seconds,
                            )
                            logger.info(
                                f"Image download status: {response.status_code}, size: {len(response.content)} bytes."
                            )
                            response.raise_for_status()  # This will raise an error for 4xx/5xx responses
                            base64_image = base64.b64encode(response.content).decode(
                                "utf-8"
                            )
                            current_turn_content_parts.append(
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": file.get("mimetype"),
                                        "data": base64_image,
                                    },
                                }
                            )
                            logger.info(
                                f"Successfully processed and encoded attached image: {file.get('name')}"
                            )
                        except Exception as img_e:
                            logger.error(
                                f"Failed to download or process attached image {file.get('name')}: {img_e}",
                                exc_info=True,
                            )

        # The last message to be added to the history is a multimodal HumanMessage
        current_turn_human_message = HumanMessage(content=current_turn_content_parts)

        # The final history for the main LLM is the history up to the last turn, plus the new multimodal message
        final_history_for_main_llm = current_thread_history[:-1] + [
            current_turn_human_message
        ]

        logger.info(
            f"Sending to main LLM for thread {thread_ts_key}. Final history length: {len(final_history_for_main_llm)} messages."
        )
        logger.debug(
            f"Final history for main LLM (thread {thread_ts_key}): {final_history_for_main_llm}"
        )

        ai_response = llm.invoke(final_history_for_main_llm)
        ai_message_content = (
            ai_response.content if hasattr(ai_response, "content") else str(ai_response)
        )
        disclaimer = "\n\n* *Generative AI is experimental. Please verify answers using official documentation.*"
        full_response = ai_message_content + disclaimer
        logger.info(f"LLM response for thread {thread_ts_key}: '{ai_message_content}'")
        return full_response
    except Exception as e:
        logger.error(
            f"Error during LLM invocation for thread {thread_ts_key}: {e}",
            exc_info=True,
        )
        return f"Sorry, I encountered an error trying to generate a response: {e}"


#  Event Listener for App Mentions (New Conversations OR Mentions in existing threads)
@app.event("app_mention")
def handle_app_mention_events(body, say, client):
    event = body["event"]
    user_text_raw = event["text"]
    user_id = event["user"]
    channel_id = event["channel"]
    files = event.get("files", [])  # Get list of files from the event

    thread_ts_for_history = event.get("thread_ts", event["ts"])
    current_message_ts = event["ts"]

    logger.info(
        f"APP_MENTION event triggered. User: {user_id}, Channel: {channel_id}, "
        f"Message TS: {current_message_ts}, Thread TS for history: {thread_ts_for_history}. "
        f"Raw text: '{user_text_raw}', Files: {len(files)}"
    )

    prompt_for_processing = user_text_raw

    # Check if the message is empty (no text after removing mention and no files)
    if (
        bot_user_id
        and not user_text_raw.replace(f"<@{bot_user_id}>", "").strip()
        and not files
    ):
        logger.info(
            f"App mention for thread {thread_ts_for_history} was empty. Sending generic help."
        )
        say(
            text="Hi there! How can I help you today? Please ask me a question.",
            thread_ts=thread_ts_for_history,
        )
        return

    # Pass the 'files' list to the processing function
    response_text = process_user_message_with_slack_history(
        client, channel_id, thread_ts_for_history, prompt_for_processing, files=files
    )

    try:
        say(text=response_text, thread_ts=thread_ts_for_history)
        logger.info(
            f"Successfully sent LLM response via 'say' to thread {thread_ts_for_history}."
        )
    except Exception as e:
        logger.error(
            f"Error sending LLM response via 'say' to thread {thread_ts_for_history}: {e}",
            exc_info=True,
        )
        try:
            say(
                text="Sorry, I couldn't send my response.",
                thread_ts=thread_ts_for_history,
            )
        except Exception as e_say:
            logger.error(f"Failed to send even error response via 'say': {e_say}")


# Event Listener for Messages (Follow-ups in Threads and DMs)
@app.event("message")
def handle_message_events(body, message, say, client):
    channel_type = message.get("channel_type")
    user_id = message.get("user")
    text_raw = message.get("text", "")  # Default to empty string
    files = message.get("files", [])  # Get list of files from the event
    event_thread_ts = message.get("thread_ts")
    current_message_ts = message.get("ts")
    channel_id = message.get("channel")

    # Ignore message if it has no text and no files
    if not text_raw and not files:
        return

    if user_id == bot_user_id or message.get("subtype") in [
        "bot_message",
        "message_deleted",
        "message_changed",
        "thread_broadcast",
        "file_share",  # We handle files inside the message payload, not this subtype
        "message_replied",
        "channel_join",
        "channel_leave",
    ]:
        return

    if bot_user_id and f"<@{bot_user_id}>" in text_raw:
        logger.info(
            f"MESSAGE event (ts: {current_message_ts}) contains a bot mention. "
            f"Assuming app_mention handler will process. Skipping in message handler."
        )
        return

    thread_key_for_history = None
    prompt_for_processing = text_raw

    if channel_type == "im" and not event_thread_ts:
        thread_key_for_history = current_message_ts
        logger.info(
            f"MESSAGE event: New DM. User: {user_id}, Channel: {channel_id}, "
            f"Message TS (used as thread_key): {thread_key_for_history}. Raw text: '{text_raw}', Files: {len(files)}"
        )
    elif channel_type == "im" and event_thread_ts:
        thread_key_for_history = event_thread_ts
        logger.info(
            f"MESSAGE event: Reply in DM thread. User: {user_id}, Channel: {channel_id}, "
            f"Message TS: {current_message_ts}, Thread TS: {thread_key_for_history}. Raw text: '{text_raw}', Files: {len(files)}"
        )
    elif event_thread_ts:
        logger.info(
            f"MESSAGE event: Non-mention reply in channel/group thread {event_thread_ts}. Bot not configured to respond. Ignoring."
        )
        return
    else:
        logger.info(
            f"MESSAGE event: Non-mention, non-threaded, non-DM message from {user_id}. Bot not configured to respond. Ignoring."
        )
        return

    if not thread_key_for_history:
        logger.warning(
            f"MESSAGE event: Could not determine thread_key_for_history. User: {user_id}, Text: '{text_raw}'. Ignoring."
        )
        return

    # Pass the 'files' list to the processing function
    response_text = process_user_message_with_slack_history(
        client, channel_id, thread_key_for_history, prompt_for_processing, files=files
    )

    try:
        say(text=response_text, thread_ts=thread_key_for_history)
        logger.info(
            f"Successfully sent LLM response via 'say' to thread/DM {thread_key_for_history} from message handler."
        )
    except Exception as e:
        logger.error(
            f"Error sending LLM response via 'say' to thread/DM {thread_key_for_history} from message handler: {e}",
            exc_info=True,
        )
        try:
            say(
                text="Sorry, I couldn't send my response.",
                thread_ts=thread_key_for_history,
            )
        except Exception as e_say:
            logger.error(
                f"Failed to send even error response via 'say' from message handler: {e_say}"
            )

SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)