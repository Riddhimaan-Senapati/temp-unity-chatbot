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
    retrieve_context,
)
from utils.slackbot_helper import (
    reconstruct_history_from_slack,
    create_optimized_query,
    create_multimodal_message,
    generate_ai_response,
)

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


def initialize_clients():
    global bedrock_client, llm, retriever
    if bedrock_client is None:
        logger.info("Cold start: initializing Bedrock, LLM & retriever")
        bedrock_client = initialize_bedrock_client()
        llm = initialize_llm(client=bedrock_client)
        retriever = initialize_knowledge_base_retriever()
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
    if not (llm and retriever):
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
        history = reconstruct_history_from_slack(
            client, channel_id, thread_ts, bot_user_id
        )
        cleaned_text = user_text_raw.replace(f"<@{bot_user_id}>", "").strip()
        prompt_text = cleaned_text or (
            "Describe the attached image(s)." if files else "help"
        )
        optimized_q = create_optimized_query(llm, history, prompt_text)
        context_data, _ = retrieve_context(retriever=retriever, prompt=optimized_q)
        current_msg = create_multimodal_message(cleaned_text, context_data, files)
        final_history = history[:-1] + [current_msg]
        full_response = generate_ai_response(llm, final_history)
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
