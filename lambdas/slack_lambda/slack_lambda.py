# filename: slack_lambda/slack_lambda.py

import logging
import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# Import your helper functions
from utils.chatbot_helper import (
    initialize_bedrock_client,
    initialize_knowledge_base_retriever,
    initialize_llm,
)
from utils.slackbot_helper import (
    reconstruct_history_from_slack,
    create_multimodal_message,
    generate_ai_response_with_tools,
    create_retrieve_context_tool,
)

# set source count(how many chunks to retrieve)
SOURCE_COUNT = 10

# Load environment variables (for local development)
load_dotenv()

# Logging setup
SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Bolt app for AWS Lambda with proper configuration
app = App(
    process_before_response=True,
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)

# Global clients reused between cold/warm starts
bedrock_client = None
llm = None
retriever = None
retrieve_context_tool = None


def initialize_clients():
    global bedrock_client, llm, retriever, retrieve_context_tool
    if bedrock_client is None:
        logger.info("Cold start: initializing Bedrock, LLM, retriever & tools")
        bedrock_client = initialize_bedrock_client()
        llm = initialize_llm(client=bedrock_client)
        retriever = initialize_knowledge_base_retriever(source_count=SOURCE_COUNT)
        retrieve_context_tool = create_retrieve_context_tool(retriever)
        logger.info("Initialization complete.")


# Middleware to skip Slack retry attempts so you don’t duplicate processing
def is_retry_request(req):
    headers = getattr(req, "headers", {}) or {}
    retry_num = headers.get("x-slack-retry-num")
    if retry_num:
        logger.info(
            f"Skipping Slack retry attempt #{retry_num}, reason: {headers.get('x-slack-retry-reason')}"
        )
    return retry_num is not None


@app.use
def skip_retry_middleware(body, req, next):
    if is_retry_request(req):
        return  # Drop retry processing but still return HTTP 200
    return next()


def process_and_respond(body, say, client, context, logger):
    logger.info("Lazy listener: process_and_respond invoked")
    initialize_clients()
    if not (llm and retriever and retrieve_context_tool):
        say("The AI components are not available. Please contact an administrator.")
        return

    event = body.get("event", {})
    user_text_raw = event.get("text", "")
    channel_id = event.get("channel")
    thread_ts = event.get("thread_ts", event.get("ts"))
    files = event.get("files", [])
    bot_user_id = context.get("bot_user_id")
    if not bot_user_id:
        say("Internal error: bot ID not found.")
        return

    try:
        # Get bot_id from auth for proper message filtering
        bot_id_from_auth = None
        try:
            auth_test = client.auth_test()
            bot_id_from_auth = auth_test.get("bot_id")
            logger.info(
                f"Lambda bot_user_id: {bot_user_id}, bot_id_from_auth: {bot_id_from_auth}"
            )
        except Exception as auth_e:
            logger.warning(f"Could not get bot_id_from_auth: {auth_e}")

        history = reconstruct_history_from_slack(
            client, channel_id, thread_ts, bot_user_id, bot_id_from_auth
        )
        cleaned_text = user_text_raw.replace(f"<@{bot_user_id}>", "").strip()

        # Handle empty messages
        if not cleaned_text and not files:
            cleaned_text = "help"

        logger.info(
            f"Lambda processing: cleaned_text='{cleaned_text}', files={len(files)}"
        )

        current_msg = create_multimodal_message(cleaned_text, files)
        final_history = history[:-1] + [current_msg]

        logger.info(
            f"Lambda calling generate_ai_response_with_tools with history length: {len(final_history)}"
        )
        full_response = generate_ai_response_with_tools(
            llm, final_history, retrieve_context_tool
        )

        say(text=full_response, thread_ts=thread_ts)
        logger.info(f"Responded to thread {thread_ts}")
    except Exception:
        logger.error("Error in process_and_respond", exc_info=True)
        say(
            text="I'm sorry, an error occurred while processing your request.",
            thread_ts=thread_ts,
        )


# Handlers that trigger the lazy listener; Bolt auto-calls ack()
def handle_app_mention_events(ack):
    ack()


app.event("app_mention")(ack=handle_app_mention_events, lazy=[process_and_respond])


def handle_message_events(ack):
    ack()


app.event("message")(ack=handle_message_events, lazy=[process_and_respond])


# Entry point for Lambda
def handler(event, context):
    logger.info("Lambda handler invoked")
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
