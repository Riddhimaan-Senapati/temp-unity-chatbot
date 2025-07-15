import logging
import os
import sys

# Add the parent directory to Python path for local development
# This is needed when running directly with: python slack_scripts/slack_bot.py
# Docker containers handle this with PYTHONPATH environment variable
if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

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

from utils.slackbot_helper import (
    reconstruct_history_from_slack,
    create_optimized_query,
    create_multimodal_message,
    generate_ai_response,
    get_text_from_message,
)

# Load Environment Variables
load_dotenv()

# Initialize Logging with more detailed format for ECS
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Ensure logs go to stdout for ECS
    ]
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("=== Unity Slack Bot Starting ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info("Checking environment variables...")

# Slack App Initialization
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Add middleware to log all incoming events for debugging
@app.middleware
def log_all_events(body, next):
    logger.info(f"=== INCOMING EVENT ===")
    logger.info(f"Event type: {body.get('event', {}).get('type', 'unknown')}")
    logger.info(f"Event body keys: {list(body.keys())}")
    if 'event' in body:
        event = body['event']
        logger.info(f"Event details: channel={event.get('channel')}, user={event.get('user')}, text='{event.get('text', '')[:100]}'")
    logger.info(f"=== END EVENT LOG ===")
    next()

# LangChain Initializations
try:
    # initialize bedrock client
    bedrock_client = initialize_bedrock_client()
    # IMPORTANT: Ensure this initializes a multimodal model, e.g., Claude 3 Sonnet
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





#  Shared Logic for Processing User Messages
def process_user_message_with_slack_history(
    client, channel_id, thread_ts_key, current_user_text_raw, files=None
):
    if not llm or not retriever:
        logger.error("LLM or Retriever not initialized. Cannot process message.")
        return "Sorry, the AI service is currently unavailable. Please check the logs or contact an administrator."

    logger.info(
        f"Processing user message for thread {thread_ts_key}. Raw input: '{current_user_text_raw}', Files: {len(files) if files else 0}"
    )

    # Reconstruct conversation history using shared helper
    current_thread_history = reconstruct_history_from_slack(
        client, channel_id, thread_ts_key, bot_user_id, bot_id_from_auth
    )

    # Clean user text and determine query
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

    try:
        # Create optimized query using shared helper
        optimized_query = create_optimized_query(llm, current_thread_history, query_prompt_text)
        logger.info(f"Generated optimized query for thread {thread_ts_key}: '{optimized_query}'")

        # Retrieve context from knowledge base
        context, relevant_docs = retrieve_context(
            retriever=retriever, prompt=optimized_query
        )
        logger.debug(
            f"Retrieved context for thread {thread_ts_key} (first 100 chars): {str(context)[:100]}"
        )

        # Create multimodal message using shared helper
        current_turn_human_message = create_multimodal_message(cleaned_current_user_text, context, files)

        # The final history for the main LLM is the history up to the last turn, plus the new multimodal message
        final_history_for_main_llm = current_thread_history[:-1] + [current_turn_human_message]

        logger.info(
            f"Sending to main LLM for thread {thread_ts_key}. Final history length: {len(final_history_for_main_llm)} messages."
        )
        logger.debug(
            f"Final history for main LLM (thread {thread_ts_key}): {final_history_for_main_llm}"
        )

        # Generate AI response using shared helper
        full_response = generate_ai_response(llm, final_history_for_main_llm)
        logger.info(f"LLM response for thread {thread_ts_key}: Generated successfully")
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
