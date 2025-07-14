import logging
import os
import json
import boto3

from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

from utils.chatbot_helper import (
    BedrockAgent,
    ConversationManager,
    convert_to_langchain_messages,
    logger as chatbot_logger
)

# Initialize global variables for Bedrock client, LLM, and retriever
bedrock_client = None
llm = None
retriever = None

# process_before_response must be True when running on FaaS
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True, # Ensure this is True for lazy listeners
)

# This function contains the core logic for processing Slack events,
# including interacting with Bedrock. It's designed to be executed asynchronously
# by slack_bolt's lazy listener.
def process_slack_event_lazily(body, say, client):
    global bedrock_client, llm, retriever

    # Initialize Bedrock client, LLM, and retriever if not already initialized (cold start)
    if bedrock_client is None:
        try:
            print("Initializing Bedrock client, LLM, and retriever...")
            bedrock_client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
            llm = BedrockAgent(bedrock_client)
            retriever = ConversationManager(
                bedrock_client,
                os.environ.get("KNOWLEDGE_BASE_ID"),
                os.environ.get("KNOWLEDGE_BASE_REGION"),
            )
            print("Initialization complete.")
        except Exception as e:
            chatbot_logger.error(f"Error during Bedrock client/LLM/retriever initialization: {e}", exc_info=True)
            say(f"Error initializing bot components: {e}")
            return

    # Only process if the message is new and not a retry from Slack
    retry_num = body.get("X-Slack-Retry-Num")
    if retry_num and int(retry_num) > 0:
        chatbot_logger.info(f"Ignoring retry event (X-Slack-Retry-Num: {retry_num}).")
        return

    # Extract necessary information based on event type
    event = body.get("event", {})
    message_data = body.get("event", {})
    user_text_raw = event.get("text", message_data.get("text", ""))
    channel_id = event.get("channel", message_data.get("channel", ""))
    user_id = event.get("user", message_data.get("user", ""))
    thread_ts = event.get("thread_ts", event.get("ts", message_data.get("thread_ts", message_data.get("ts"))))

    if not user_text_raw:
        chatbot_logger.info("Received empty message or event without text.")
        return

    print(f"Processing message from {user_id} in channel {channel_id}, thread {thread_ts}: {user_text_raw}")

    # Conversation History for Context
    conversation_history = []
    if thread_ts and channel_id:
        try:
            # Fetch conversation history from Slack API
            history = client.conversations_replies(
                channel=channel_id,
                ts=thread_ts,
                inclusive=True,
                latest=thread_ts,
                limit=5, # Limit to last 5 messages for context
            )
            messages = history["messages"]
            # Convert Slack messages to LangChain messages
            conversation_history = convert_to_langchain_messages(
                messages, os.environ.get("SLACK_BOT_ID")
            )
            chatbot_logger.info(f"Conversation history fetched: {conversation_history}")
        except Exception as e:
            chatbot_logger.error(f"Error fetching conversation history: {e}", exc_info=True)
            # Continue without history if there's an error
            pass

    try:
        # Generate response using BedrockAgent
        response_text, sources = llm.invoke(user_text_raw, conversation_history, retriever)

        # Remove bot mention from the user query
        bot_id = os.environ.get("SLACK_BOT_ID")
        user_text_query = user_text_raw.replace(f"<@{bot_id}>", "").strip()

        if not user_text_query:
            chatbot_logger.info("Received empty message after removing bot mention.")
            return # Do nothing for empty messages

        chatbot_logger.info(f"User query for Bedrock: {user_text_query}")

        # Post the response back to Slack
        say(text=response_text, thread_ts=thread_ts)

        # Optionally, send sources as a follow-up message or attach to the main message
        if sources:
            sources_text = "\n".join([f"- {s}" for s in sources])
            say(text=f"*Sources: *\n{sources_text}", thread_ts=thread_ts)

    except Exception as e:
        chatbot_logger.error(f"Error processing message with Bedrock: {e}", exc_info=True)
        say(f"An error occurred while processing your request: {e}")

# Event Listener for App Mentions (New Conversations OR Mentions in existing threads)
@app.event("app_mention", lazy=[process_slack_event_lazily])
def handle_app_mention_events(ack):
    ack() # Acknowledge the event immediately

# Event Listener for Messages (Follow-ups in Threads and DMs)
@app.event("message", lazy=[process_slack_event_lazily])
def handle_message_events(ack):
    ack() # Acknowledge the event immediately

# Clear all existing log handlers and set up basic logging
SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

def handler(event, context):
    print(f"Lambda invoked! Event: {json.dumps(event, default=str)}")
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
