# filename: slack_lambda/slack_lambda.py

import logging
import os
import base64
import requests
import json

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# Import your existing helper functions
from utils.chatbot_helper import (
    initialize_bedrock_client,
    initialize_knowledge_base_retriever,
    initialize_llm,
    retrieve_context,
)
from utils.prompts import question_system_prompt, slack_system_prompt

# Load Environment Variables for local testing if needed
load_dotenv()

# --- Logging Setup for Lambda ---
# Bolt's Lambda handler configures logging, but we can set a format.
SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s", level=logging.INFO)
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
            logger.info("Cold start: Initializing Bedrock client, LLM, and retriever...")
            bedrock_client = initialize_bedrock_client()
            llm = initialize_llm(client=bedrock_client)
            retriever = initialize_knowledge_base_retriever()
            logger.info("Initialization complete.")
        except Exception as e:
            logger.critical(f"FATAL: Could not initialize Bedrock/LangChain clients: {e}", exc_info=True)
            raise e # Fail loudly so the Lambda execution shows an error

def reconstruct_history_from_slack(client, channel_id, thread_ts, bot_user_id):
    """Reconstructs conversation history, now receiving bot_user_id as a parameter."""
    history = [SystemMessage(content=slack_system_prompt)]
    try:
        result = client.conversations_replies(channel=channel_id, ts=thread_ts, limit=200)
        messages = result.get("messages", [])
        logger.info(f"Fetched {len(messages)} messages from Slack for thread {thread_ts}.")

        for msg in sorted(messages, key=lambda x: float(x["ts"])):
            msg_text = msg.get("text", "")
            msg_bot_id = msg.get("bot_id")

            if msg_bot_id or msg.get("user") == bot_user_id:
                if msg_text: history.append(AIMessage(content=msg_text))
            elif msg.get("user"):
                message_content_parts = []
                cleaned_text = msg_text.replace(f"<@{bot_user_id}>", "").strip() if msg["ts"] == thread_ts else msg_text
                if cleaned_text: message_content_parts.append({"type": "text", "text": cleaned_text})

                if msg.get("files"):
                    for file in msg.get("files", []):
                        if file.get("mimetype") in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
                            url_private = file.get("url_private")
                            if url_private:
                                try:
                                    response = requests.get(url_private, headers={"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"}, timeout=10)
                                    response.raise_for_status()
                                    base64_image = base64.b64encode(response.content).decode("utf-8")
                                    message_content_parts.append({
                                        "type": "image", "source": {"type": "base64", "media_type": file.get("mimetype"), "data": base64_image}
                                    })
                                    logger.info(f"Successfully processed historical image: {file.get('name')}")
                                except Exception as img_e:
                                    logger.error(f"Failed to download/process historical image {file.get('name')}: {img_e}")
                if message_content_parts:
                    history.append(HumanMessage(content=message_content_parts))
    except Exception as e:
        logger.error(f"Error reconstructing history from Slack for thread {thread_ts}: {e}", exc_info=True)
        return [SystemMessage(content=slack_system_prompt)]
    return history

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
        current_thread_history = reconstruct_history_from_slack(client, channel_id, thread_ts_for_history, bot_user_id)
        
        def get_text_from_message(message):
            if isinstance(message.content, str): return message.content
            if isinstance(message.content, list): return " ".join([p["text"] for p in message.content if p["type"] == "text"])
            return ""

        text_only_history = [SystemMessage(content=question_system_prompt)]
        if len(current_thread_history) > 1:
            for msg in current_thread_history[1:]:
                text_only_history.append(HumanMessage(content=get_text_from_message(msg)) if isinstance(msg, HumanMessage) else msg)
        
        cleaned_user_text = user_text_raw.replace(f"<@{bot_user_id}>", "").strip()
        query_prompt_text = cleaned_user_text or ("Describe the attached image(s)." if files else "help")
        
        messages_for_query_opt = text_only_history[:-1] + [HumanMessage(content=f'Generate a search query for: "{query_prompt_text}"')]
        
        query_response = llm.invoke(messages_for_query_opt)
        optimized_query = query_response.content.strip() or query_prompt_text
        logger.info(f"Generated optimized query: '{optimized_query}'")

        context, _ = retrieve_context(retriever=retriever, prompt=optimized_query)

        content_parts = []
        augmented_text = f"Context:\n{context}\n\nQuestion: {cleaned_user_text}"
        content_parts.append({"type": "text", "text": augmented_text})
        
        if files:
            for file in files:
                if file.get("mimetype") in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
                    try:
                        response = requests.get(file["url_private"], headers={"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"}, timeout=10)
                        response.raise_for_status()
                        b64_img = base64.b64encode(response.content).decode("utf-8")
                        content_parts.append({"type": "image", "source": {"type": "base64", "media_type": file["mimetype"], "data": b64_img}})
                        logger.info(f"Successfully processed attached image: {file.get('name')}")
                    except Exception as img_e:
                        logger.error(f"Failed to process attached image {file.get('name')}: {img_e}")

        final_history = current_thread_history[:-1] + [HumanMessage(content=content_parts)]
        
        ai_response = llm.invoke(final_history)
        ai_message_content = ai_response.content if hasattr(ai_response, 'content') else str(ai_response)
        disclaimer = "\n\n* *Generative AI is experimental. Please verify answers using official documentation.*"
        full_response = ai_message_content + disclaimer
        
        say(text=full_response, thread_ts=thread_ts_for_history)
        logger.info(f"Successfully sent LLM response to thread {thread_ts_for_history}.")

    except Exception as e:
        logger.error(f"Error in lazy processing function: {e}", exc_info=True)
        say(text=f"I'm sorry, an error occurred while processing your request.", thread_ts=thread_ts_for_history)

# --- Event Handlers using the lazy=[] parameter ---
# This is the simplest and most robust way to handle the 3-second timeout.
# Bolt automatically calls ack() and then runs the functions in the lazy list.

def handle_app_mention_events(ack):
    ack()

app.event("app_mention")(ack=handle_app_mention_events, lazy=[process_and_respond])

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
            return # Stop processing, don't call next()

    # For all other events (like app_mention), or for valid DMs, continue.
    next()

def handle_message_events(ack):
    # The middleware above has already filtered out unwanted messages.
    # If the execution reaches here, it's a valid DM to process.
    ack()

app.event("message")(ack=handle_message_events, lazy=[process_and_respond])

# --- Lambda Handler Entrypoint ---
def handler(event, context):
    """
    Handles incoming requests from API Gateway.
    """
    logger.info("Lambda handler invoked")
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)