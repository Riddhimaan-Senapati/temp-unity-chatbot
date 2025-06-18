import logging
import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from chatbot_helper import (
    initialize_bedrock_client,
    initialize_knowledge_base_retriever,
    initialize_llm,
    question_system_prompt,
    retrieve_context,
    slack_system_prompt,
)

# Load Environment Variables
load_dotenv()

# Initialize Logging
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
        # limit message history to 200 messages.It is very unlikely this limit will be breached
        result = client.conversations_replies(
            channel=channel_id, ts=thread_ts, limit=200
        )
        messages = result.get("messages", [])

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
                if msg["ts"] == thread_ts:
                    cleaned_text = msg_text.replace(f"<@{bot_user_id}>", "").strip()
                if cleaned_text:
                    history.append(HumanMessage(content=cleaned_text))
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
    client, channel_id, thread_ts_key, current_user_text_raw
):
    if not llm or not retriever:
        logger.error("LLM or Retriever not initialized. Cannot process message.")
        return "Sorry, the AI service is currently unavailable. Please check the logs or contact an administrator."

    current_thread_history = reconstruct_history_from_slack(
        client, channel_id, thread_ts_key
    )

    # First, generate an optimized search query using conversation history
    query_messages = [
        {"role": "system", "content": question_system_prompt},
        *[
            {"role": m.type, "content": m.content} for m in current_thread_history[1:-1]
        ],  # All messages except system prompt and the last user message(will be replaced by augmented user prompt)
        {
            "role": "user",
            "content": f"Based on this conversation history, generate a search query for: {current_user_text_raw}",
        },
    ]

    try:
        # Get the optimized query from the LLM
        query_response = llm.invoke(query_messages)
        optimized_query = query_response.content.strip()
        logger.info(f"Generated optimized query: {optimized_query}")

        # Retrieve context and relevant docs based on optimized query
        context, relevant_docs = retrieve_context(
            retriever=retriever, prompt=optimized_query
        )

        # Create augmented user prompt
        augmented_current_user_prompt = (
            f"Context:\n{context}\n\nQuestion: {current_user_text_raw}"
        )

        # Replace user prompt with augmented user prompt in thread history
        current_thread_history[-1] = HumanMessage(content=augmented_current_user_prompt)

        logger.info(
            f"Sending to LLM for thread {thread_ts_key}. History length: {len(current_thread_history)} messages."
        )

        # Get LLM response
        ai_response = llm.invoke(current_thread_history)
        ai_message_content = (
            ai_response.content if hasattr(ai_response, "content") else str(ai_response)
        )
        logger.info(f"Successfully processed LLM response for thread {thread_ts_key}")
        return ai_message_content
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

    """
    IMPORTANT: Determine the correct thread_ts to use for history
    If the app_mention event itself has a thread_ts, it means this mention occurred within an existing thread.
    In this case, thread_ts_from_event is the key for the whole conversation.
    If not, event["ts"] (the timestamp of this mention) starts a new thread.
    """
    thread_ts_for_history = event.get("thread_ts", event["ts"])
    current_message_ts = event["ts"]  # Timestamp of this specific mention message

    logger.info(
        f"Received app_mention (current_message_ts: {current_message_ts}, using thread_ts_for_history: {thread_ts_for_history}) "
        f"from user {user_id} in channel {channel_id}: '{user_text_raw}'"
    )

    if (
        bot_user_id and not user_text_raw.replace(f"<@{bot_user_id}>", "").strip()
    ):  # Check if empty after removing mention
        say(
            text="Hi there! How can I help you today? Please ask me a question.",
            thread_ts=thread_ts_for_history,
        )
        return

    # Pass the correct thread_ts_for_history to get the full conversation context,
    # and the raw text of this specific mention.
    response_text = process_user_message_with_slack_history(
        client, channel_id, thread_ts_for_history, user_text_raw
    )

    try:
        # Reply in the correct thread.
        say(text=response_text, thread_ts=thread_ts_for_history)
        logger.info(f"Sent LLM response directly to thread {thread_ts_for_history}.")
    except Exception as e:
        logger.error(
            f"Error sending LLM response to thread {thread_ts_for_history}: {e}",
            exc_info=True,
        )
        try:  # Try to send an error message
            say(
                text="Sorry, I couldn't send my response.",
                thread_ts=thread_ts_for_history,
            )
        except Exception as e_say:
            logger.error(f"Failed to send even error response: {e_say}")


# Event Listener for Messages (Follow-ups in Threads and DMs)
# This handler will catch DMs. It will IGNORE messages in channels/groups unless they directly @mention the bot
# (because app_mention handler should take precedence for those).
@app.event("message")
def handle_message_events(body, message, say, client):
    channel_type = message.get("channel_type")
    user_id = message.get("user")
    text_raw = message.get("text")
    event_thread_ts = message.get(
        "thread_ts"
    )  # Timestamp of the root message of the thread, if this message is in a thread
    current_message_ts = message.get("ts")  # Timestamp of this specific message
    channel_id = message.get("channel")

    # Ignore messages from the bot itself, various subtypes, or messages without text
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

    # If this message contains a direct @mention of our bot,
    # the `app_mention` handler is preferred and should handle it.
    # This prevents double processing.
    if bot_user_id and f"<@{bot_user_id}>" in text_raw:
        logger.info(
            f"Message event (ts: {current_message_ts}) contains a bot mention. Assuming app_mention handler will process. Skipping in message handler."
        )
        return

    thread_key_for_history = None
    prompt_for_processing = text_raw  # This is passed as current_user_text_raw

    if channel_type == "im" and not event_thread_ts:
        # This is a NEW direct message (not a reply in a DM thread)
        # The history will be for a "thread" starting with this DM.
        thread_key_for_history = current_message_ts
        logger.info(
            f"Received new DM (using its ts {thread_key_for_history} as thread_key) from user {user_id}: '{text_raw}'"
        )
    elif channel_type == "im" and event_thread_ts:
        # This is a reply within an existing DM thread (and it doesn't mention the bot)
        thread_key_for_history = event_thread_ts
        logger.info(
            f"Received reply in DM thread {thread_key_for_history} from user {user_id}: '{text_raw}'"
        )
    elif (
        event_thread_ts
    ):  # It's a message in a channel/group thread, and DOES NOT mention the bot
        # Current decision: Bot does not respond to non-mention messages in channel/group threads.
        logger.info(
            f"Received non-mention reply in channel/group thread {event_thread_ts}. Bot not configured to respond. Ignoring."
        )
        return
    else:
        # Message in a channel/group, not a DM, not in a thread, and not a mention. Ignore.
        logger.info(
            f"Received non-mention, non-threaded, non-DM message from {user_id}. Bot not configured to respond. Ignoring."
        )
        return

    if not thread_key_for_history:  # Should only be true if logic above has a hole.
        logger.warning(
            "Could not determine thread_key_for_history in message handler. Ignoring message."
        )
        return

    response_text = process_user_message_with_slack_history(
        client, channel_id, thread_key_for_history, prompt_for_processing
    )

    try:
        # For new DMs, thread_key_for_history = current_message_ts. This makes the reply start a thread.
        # For replies in DM threads, thread_key_for_history = event_thread_ts.
        say(text=response_text, thread_ts=thread_key_for_history)
        logger.info(
            f"Sent LLM response directly to thread/DM {thread_key_for_history}."
        )
    except Exception as e:
        logger.error(
            f"Error sending LLM response to thread/DM {thread_key_for_history}: {e}",
            exc_info=True,
        )
        try:
            say(
                text="Sorry, I couldn't send my response.",
                thread_ts=thread_key_for_history,
            )
        except Exception as e_say:
            logger.error(f"Failed to send even error response: {e_say}")


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
