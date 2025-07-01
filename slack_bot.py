import logging
import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from utils.chatbot_helper import (
    initialize_bedrock_client,
    initialize_knowledge_base_retriever,
    initialize_llm,
    retrieve_context,
)

from utils.prompts import question_system_prompt, slack_system_prompt

# Load Environment Variables
load_dotenv()

# Initialize Logging
# Note: switch to logging.DEBUG if you want more information, but that mode can get verbose

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Slack App Initialization
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# LangChain Initializations
try:
    # initialize bedrock client
    bedrock_client = initialize_bedrock_client()
    # initialize LLM using bedrock client
    llm = initialize_llm(client=bedrock_client)
    # initialize Knowledge Base retriever
    retriever = initialize_knowledge_base_retriever()
    logger.info("Bedrock client, LLM, and Retriever initialized successfully.")
except Exception as e:
    logger.error(
        f"Error initializing AWS services or LangChain components: {e}", exc_info=True
    )
    llm = None
    retriever = None

# Bot User ID
bot_user_id = None
bot_id_from_auth = (
    None  # Initialize to avoid potential UnboundLocalError if auth_test fails
)
try:
    auth_test = app.client.auth_test()
    bot_user_id = auth_test["user_id"]
    bot_id_from_auth = auth_test.get("bot_id")  # Often the same as BXXXX for bot users
    logger.info(f"Bot User ID: {bot_user_id}, Bot ID from auth: {bot_id_from_auth}")
except Exception as e:
    logger.error(
        f"Error fetching bot_user_id: {e}. Mention parsing and self-message filtering might be affected.",
        exc_info=True,
    )


# Function to Reconstruct Conversation History from Slack
def reconstruct_history_from_slack(client, channel_id, thread_ts):
    if not bot_user_id:
        logger.error("Cannot reconstruct history: bot_user_id is not set.")
        return [SystemMessage(content=slack_system_prompt)]

    history = [SystemMessage(content=slack_system_prompt)]
    try:
        # limit message history to 200 messages.It is very likely this limit will be breached
        result = client.conversations_replies(
            channel=channel_id, ts=thread_ts, limit=200
        )
        messages = result.get("messages", [])
        # Log the number of messages fetched from Slack for the thread
        logger.info(
            f"Fetched {len(messages)} messages from Slack for thread {thread_ts}."
        )

        # sort by thread timestamp/id in ascending order (so older messages first)
        for msg in sorted(messages, key=lambda x: float(x["ts"])):
            msg_text = msg.get("text", "")
            msg_user = msg.get("user")
            msg_bot_id = msg.get("bot_id")

            # Decide whether the message was from the Unity Bot or users(needed for LangChain format)
            if msg_bot_id == bot_id_from_auth or msg_user == bot_user_id:
                if msg_text:
                    history.append(AIMessage(content=msg_text))
            elif msg_user:
                cleaned_text = msg_text
                if msg["ts"] == thread_ts:  # If it's the root message of the thread
                    # Log if mention is being cleaned from root message
                    if f"<@{bot_user_id}>" in msg_text:
                        logger.debug(
                            f"Cleaning bot mention from root message in thread {thread_ts}"
                        )
                    cleaned_text = msg_text.replace(f"<@{bot_user_id}>", "").strip()
                if cleaned_text:
                    history.append(HumanMessage(content=cleaned_text))
        # Log the final length of the reconstructed history list
        logger.info(
            f"Reconstructed history for thread {thread_ts} with {len(history) - 1} turns (total {len(history)} messages including system prompt)."
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
    client, channel_id, thread_ts_key, current_user_text_raw
):
    if not llm or not retriever:
        logger.error("LLM or Retriever not initialized. Cannot process message.")
        return "Sorry, the AI service is currently unavailable. Please check the logs or contact an administrator."

    # Log the raw user input for this specific interaction
    logger.info(
        f"Processing user message for thread {thread_ts_key}. Raw input: '{current_user_text_raw}'"
    )

    current_thread_history = reconstruct_history_from_slack(
        client, channel_id, thread_ts_key
    )

    # Log the full history being used for query optimization (can be verbose, use DEBUG)
    logger.debug(
        f"History for query optimization (thread {thread_ts_key}): {current_thread_history}"
    )

    # First, generate an optimized search query using conversation history
    # We want to provide the LLM with the history leading up to the current question,
    # and then the current question to optimize.
    messages_for_query_optimization_llm = [
        SystemMessage(content=question_system_prompt)
    ]

    # Add historical messages (all except the very last one if history is not just system + current)
    # The last message in current_thread_history is the current_user_text_raw (or its cleaned version)
    if (
        len(current_thread_history) > 2
    ):  # if there are actual past turns beyond system and current
        for msg_idx in range(
            1, len(current_thread_history) - 1
        ):  # from after system, up to before current
            messages_for_query_optimization_llm.append(current_thread_history[msg_idx])

    # Add the current user's raw text (the question to be optimized)
    # Ensure it's cleaned of bot mention if it's a direct ping to the bot
    cleaned_current_user_text = (
        current_user_text_raw.replace(f"<@{bot_user_id}>", "").strip()
        if bot_user_id
        else current_user_text_raw.strip()
    )
    if not cleaned_current_user_text:  # If the message was only a mention
        logger.warning(
            f"User message for thread {thread_ts_key} was empty after cleaning mention. Using 'help' as query."
        )
        cleaned_current_user_text = "help"  # Fallback

    messages_for_query_optimization_llm.append(
        HumanMessage(
            content=f'Based on the conversation history (if any), generate an optimized search query for the following user question: "{cleaned_current_user_text}"'
        )
    )

    # Log the messages being sent for query optimization
    logger.debug(
        f"Messages for query optimization LLM (thread {thread_ts_key}): {messages_for_query_optimization_llm}"
    )

    try:
        # Get the optimized query from the LLM
        query_response = llm.invoke(messages_for_query_optimization_llm)
        optimized_query = query_response.content.strip()
        # Log the optimized query received from LLM
        logger.info(
            f"Generated optimized query for thread {thread_ts_key}: '{optimized_query}'"
        )
        if not optimized_query:  # Handle empty optimized query
            logger.warning(
                f"Optimized query was empty for thread {thread_ts_key}. Using cleaned user text: '{cleaned_current_user_text}'"
            )
            optimized_query = cleaned_current_user_text

        # Retrieve context and relevant docs based on optimized query
        context, relevant_docs = retrieve_context(
            retriever=retriever, prompt=optimized_query
        )
        # Log a snippet of the retrieved context
        logger.debug(
            f"Retrieved context for thread {thread_ts_key} (first 100 chars): {str(context)[:100]}"
        )

        # Create augmented user prompt using the cleaned current user text as the "Question"
        augmented_current_user_prompt = (
            f"Context:\n{context}\n\nQuestion: {cleaned_current_user_text}"
        )
        # Log the augmented prompt being used
        logger.debug(
            f"Augmented prompt for thread {thread_ts_key}: {augmented_current_user_prompt}"
        )

        # Construct the final history for the main LLM call.
        # It should be the `current_thread_history` with its last HumanMessage (the raw user input)
        # replaced by this `augmented_current_user_prompt`.
        final_history_for_main_llm = current_thread_history[:-1] + [
            HumanMessage(content=augmented_current_user_prompt)
        ]

        # Log final history length and snippet of last message
        logger.info(
            f"Sending to main LLM for thread {thread_ts_key}. Final history length: {len(final_history_for_main_llm)} messages."
        )
        logger.debug(
            f"Final history for main LLM (thread {thread_ts_key}): {final_history_for_main_llm}"
        )

        # Get LLM response
        ai_response = llm.invoke(final_history_for_main_llm)
        ai_message_content = (
            ai_response.content if hasattr(ai_response, "content") else str(ai_response)
        )

        # Add disclaimer
        disclaimer = "\n\n* *Generative AI is experimental. Please verify answers using official documentation.*"

        full_response = ai_message_content + disclaimer

        # Log the LLM's final response content
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

    thread_ts_for_history = event.get("thread_ts", event["ts"])
    current_message_ts = event["ts"]

    # More detailed log for app_mention event
    logger.info(
        f"APP_MENTION event triggered. User: {user_id}, Channel: {channel_id}, "
        f"Message TS: {current_message_ts}, Thread TS for history: {thread_ts_for_history}. "
        f"Raw text: '{user_text_raw}'"
    )

    # The user_text_raw already contains the mention.
    # process_user_message_with_slack_history will handle cleaning it if needed for the "Question:" part.
    prompt_for_processing = user_text_raw

    if bot_user_id and not user_text_raw.replace(f"<@{bot_user_id}>", "").strip():
        logger.info(
            f"App mention for thread {thread_ts_for_history} was empty after removing mention. Sending generic help."
        )
        say(
            text="Hi there! How can I help you today? Please ask me a question.",
            thread_ts=thread_ts_for_history,
        )
        return

    response_text = process_user_message_with_slack_history(
        client, channel_id, thread_ts_for_history, prompt_for_processing
    )

    try:
        say(text=response_text, thread_ts=thread_ts_for_history)
        # Log successful response sending
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
    text_raw = message.get("text")
    event_thread_ts = message.get("thread_ts")
    current_message_ts = message.get("ts")
    channel_id = message.get("channel")

    if (
        user_id == bot_user_id
        or not text_raw
        or message.get("subtype")
        in [
            "bot_message",
            "message_deleted",
            "message_changed",
            "thread_broadcast",
            "file_share",
            "message_replied",
            "channel_join",
            "channel_leave",
        ]
    ):
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
        # More detailed log for new DM
        logger.info(
            f"MESSAGE event: New DM. User: {user_id}, Channel: {channel_id}, "
            f"Message TS (used as thread_key): {thread_key_for_history}. Raw text: '{text_raw}'"
        )
    elif channel_type == "im" and event_thread_ts:
        thread_key_for_history = event_thread_ts
        # More detailed log for DM reply
        logger.info(
            f"MESSAGE event: Reply in DM thread. User: {user_id}, Channel: {channel_id}, "
            f"Message TS: {current_message_ts}, Thread TS: {thread_key_for_history}. Raw text: '{text_raw}'"
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

    response_text = process_user_message_with_slack_history(
        client, channel_id, thread_key_for_history, prompt_for_processing
    )

    try:
        say(text=response_text, thread_ts=thread_key_for_history)
        # Log successful response sending
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


# Main Execution Block
if __name__ == "__main__":
    missing_vars = []
    required_env_vars = [
        "SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "KNOWLEDGE_BASE_ID",
    ]
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    if missing_vars:
        logger.error(
            f"Missing critical environment variables: {', '.join(missing_vars)}"
        )
        exit(1)

    if not llm or not retriever:
        logger.error(
            "LLM or Retriever failed to initialize. Bot will have limited or no AI capabilities."
        )
        # Decide if you want to exit or run with limited functionality
        # exit(1)
    if not bot_user_id:
        logger.error(
            "Could not determine Bot User ID. History reconstruction and mention parsing will fail. Exiting."
        )
        exit(1)
    else:
        logger.info(
            "All critical components seem to be configured. Attempting to start SocketModeHandler..."
        )

    try:
        SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
        logger.info("⚡️ Unity Slack Bot is running in Socket Mode!")
    except Exception as e:
        logger.critical(f"Failed to start SocketModeHandler: {e}", exc_info=True)
        exit(1)
