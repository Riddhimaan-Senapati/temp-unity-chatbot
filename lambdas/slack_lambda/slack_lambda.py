# filename: slack_lambda/slack_lambda.py

import logging
import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# Import your existing helper functions
from utils.chatbot_helper import (
    initialize_bedrock_client,
    initialize_knowledge_base_retriever,
    initialize_llm,
    retrieve_context,
)
from utils.slackbot_helper import (
    reconstruct_history_from_slack,
    create_optimized_query,
    create_multimodal_message,
    generate_ai_response,
)

# Load Environment Variables for local testing if needed
load_dotenv()

# --- Logging Setup for Lambda ---
# Bolt's Lambda handler configures logging, but we can set a format.
SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- App Initialization for Lambda ---
# process_before_response=True is CRITICAL for FaaS environments like Lambda.
# It makes Bolt acknowledge requests from Slack within 3 seconds.
app = App(
    process_before_response=True,
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)

# --- Global Clients for Lambda Lifecycle ---
# These are initialized once per "cold start" of the Lambda container and reused.
bedrock_client = None
llm = None
retriever = None


def initialize_clients():
    """Initializes AWS and LangChain clients if they haven't been already."""
    global bedrock_client, llm, retriever
    if bedrock_client is None:
        try:
            logger.info(
                "Cold start: Initializing Bedrock client, LLM, and retriever..."
            )
            bedrock_client = initialize_bedrock_client()
            llm = initialize_llm(client=bedrock_client)
            retriever = initialize_knowledge_base_retriever()
            logger.info("Initialization complete.")
        except Exception as e:
            logger.critical(
                f"FATAL: Could not initialize Bedrock/LangChain clients: {e}",
                exc_info=True,
            )
            raise e  # Fail loudly so the Lambda execution shows an error


def process_and_respond(body, say, client, context, logger):
    """
    This function contains the long-running logic (RAG and LLM calls).
    It's called by the lazy listener after the initial ack() has been sent.
    """
    logger.info("Lazy function 'process_and_respond' started.")

    initialize_clients()
    if not llm or not retriever:
        say("The AI components are not available. Please contact an administrator.")
        return

    event = body.get("event", {})
    user_text_raw = event.get("text", "")
    channel_id = event.get("channel")
    thread_ts_for_history = event.get("thread_ts", event.get("ts"))
    files = event.get("files", [])
    bot_user_id = context.get("bot_user_id")

    if not bot_user_id:
        say("An internal error occurred (E01: could not identify bot).")
        return

    try:
        # Reconstruct conversation history
        current_thread_history = reconstruct_history_from_slack(
            client, channel_id, thread_ts_for_history, bot_user_id
        )

        # Clean user text and determine query
        cleaned_user_text = user_text_raw.replace(f"<@{bot_user_id}>", "").strip()
        query_prompt_text = cleaned_user_text or (
            "Describe the attached image(s)." if files else "help"
        )

        # Create optimized query using shared helper
        optimized_query = create_optimized_query(
            llm, current_thread_history, query_prompt_text
        )

        # Retrieve context from knowledge base
        context, _ = retrieve_context(retriever=retriever, prompt=optimized_query)

        # Create multimodal message using shared helper
        current_turn_human_message = create_multimodal_message(
            cleaned_user_text, context, files
        )

        # The final history for the main LLM is the history up to the last turn, plus the new multimodal message
        final_history = current_thread_history[:-1] + [current_turn_human_message]

        # Generate AI response using shared helper
        full_response = generate_ai_response(llm, final_history)

        say(text=full_response, thread_ts=thread_ts_for_history)
        logger.info(
            f"Successfully sent LLM response to thread {thread_ts_for_history}."
        )

    except Exception as e:
        logger.error(f"Error in lazy processing function: {e}", exc_info=True)
        say(
            text="I'm sorry, an error occurred while processing your request.",
            thread_ts=thread_ts_for_history,
        )


# --- Event Handlers using decorator pattern with immediate ack ---


@app.event("app_mention")
def handle_app_mention_events(ack, body, say, client, context, logger):
    ack()  # Acknowledge immediately
    process_and_respond(body, say, client, context, logger)


# We need a middleware to filter out messages we don't want to process for the 'message' event.
@app.use
def filter_unwanted_messages(body, next):
    event = body.get("event", {})
    # This middleware runs for ALL events. We only want to filter 'message' events.
    if event.get("type") == "message":
        message = event
        # Get bot_user_id from the authorization data in the event body
        bot_user_id = body.get("authorizations", [{}])[0].get("user_id")

        # Conditions to ignore the message
        is_bot_message = message.get("bot_id") is not None
        is_subtype = message.get("subtype") is not None
        is_mention = bot_user_id and f"<@{bot_user_id}>" in message.get("text", "")
        is_not_dm = message.get("channel_type") != "im"

        # We only want to process DMs that are NOT mentions (as mentions are handled by app_mention)
        if is_bot_message or is_subtype or is_mention or is_not_dm:
            return  # Stop processing, don't call next()

    # For all other events (like app_mention), or for valid DMs, continue.
    next()


@app.event("message")
def handle_message_events(ack, body, say, client, context, logger):
    # The middleware above has already filtered out unwanted messages.
    # If the execution reaches here, it's a valid DM to process.
    ack()  # Acknowledge immediately
    process_and_respond(body, say, client, context, logger)


# --- Lambda Handler Entrypoint ---
def handler(event, context):
    """
    Handles incoming requests from API Gateway.
    """
    logger.info("Lambda handler invoked")
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
