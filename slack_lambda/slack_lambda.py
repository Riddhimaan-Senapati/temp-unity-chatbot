import logging
import os
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
import json
import boto3

# Debugging: Print slack_bolt version at runtime
try:
    import slack_bolt

    print(f"DEBUG: slack_bolt version loaded at runtime: {slack_bolt.__version__}")
except ImportError:
    print("DEBUG: slack_bolt not found at runtime.")
except Exception as e:
    print(f"DEBUG: Error checking slack_bolt version: {e}")

from utils.chatbot_helper import (
    BedrockAgent,
    ConversationManager,
    convert_to_langchain_messages,  # Alias to avoid name conflict if needed
)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure the Bedrock client is initialized once
bedrock_client = None

# Initialize the Slack Bolt App
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,  # Ensure this is True for lazy listeners
)

# Initialize the handler for AWS Lambda
slack_handler = SlackRequestHandler(app)


# --- Core Logic for Asynchronous Processing (Lazy Listener) ---
def process_slack_event_lazily(body, say, client, message=None):
    """This function contains the main logic for processing Slack events.
    It's designed to be executed asynchronously by slack_bolt's lazy listener.
    """
    global bedrock_client, llm, retriever  # Access global variables

    # Initialize Bedrock client, LLM, and retriever if not already initialized (cold start)
    if bedrock_client is None:
        try:
            print("Initializing Bedrock client, LLM, and retriever...")
            bedrock_client = boto3.client(
                "bedrock-agent-runtime", region_name="us-east-1"
            )
            llm = BedrockAgent(bedrock_client)
            retriever = ConversationManager(
                bedrock_client,
                os.environ.get("KNOWLEDGE_BASE_ID"),
                os.environ.get("KNOWLEDGE_BASE_REGION"),
            )
            print("Initialization complete.")
        except Exception as e:
            logger.error(
                f"Error during Bedrock client/LLM/retriever initialization: {e}",
                exc_info=True,
            )
            say(f"Error initializing bot components: {e}")
            return

    # Determine if it's an app_mention or a direct message/thread reply
    # For app_mention events, the event['text'] contains the full message with the bot mention.
    # For message events, it's typically a direct message or a reply in a thread.
    # Ensure we get the raw text for processing.

    user_id = ""
    if "event" in body:
        event = body["event"]
        user_text_raw = event["text"]
        channel_id = event["channel"]
        user_id = event.get("user", "")
        thread_ts = event.get(
            "thread_ts", event.get("ts")
        )  # Use ts for new conversations
    elif message:  # For message events, message object is passed directly
        user_text_raw = message["text"]
        channel_id = message["channel"]
        user_id = message.get("user", "")
        thread_ts = message.get("thread_ts", message.get("ts"))
    else:
        logger.error("Could not extract user text from event or message.")
        return

    print(
        f"Processing message from {user_id} in channel {channel_id}, thread {thread_ts}: {user_text_raw}"
    )

    # Conversation History for Context
    # Fetch conversation history from the channel/thread
    conversation_history = []
    try:
        # Ensure 'client' is available and authenticated for conversations_replies
        if thread_ts:
            history = client.conversations_replies(
                channel=channel_id,
                ts=thread_ts,
                inclusive=True,
                latest=thread_ts,
                limit=5,  # Limit to last 5 messages for context
            )
            messages = history["messages"]
            # Convert Slack messages to LangChain messages
            conversation_history = convert_to_langchain_messages(
                messages, os.environ.get("SLACK_BOT_ID")
            )
            logger.info(f"Conversation history fetched: {conversation_history}")
    except Exception as e:
        logger.warning(f"Could not fetch conversation history: {e}")
        # Proceed without history if fetching fails

    # Main Chatbot Logic
    try:
        # Remove bot mention from the user's raw text for query processing
        bot_user_id = os.environ.get("SLACK_BOT_ID")
        if bot_user_id and f"<@{bot_user_id}>" in user_text_raw:
            user_text_query = user_text_raw.replace(f"<@{bot_user_id}>", "").strip()
        else:
            user_text_query = user_text_raw.strip()

        if not user_text_query:
            logger.info("Received empty message after removing bot mention.")
            return  # Do nothing for empty messages

        logger.info(f"User query for Bedrock: {user_text_query}")
        logger.info(f"Conversation history for Bedrock: {conversation_history}")

        # Call the Bedrock agent to get the response
        # The `get_llm_response_with_rag` method should handle the retrieval and generation
        # It will use the `retriever` (ConversationManager) internally.
        response_text, sources = llm.get_llm_response_with_rag(
            user_text_query, conversation_history, retriever
        )
        logger.info(f"Bedrock response: {response_text}")
        logger.info(f"Sources: {sources}")

        # Post the response back to Slack
        say(text=response_text, thread_ts=thread_ts)

        # Optionally, send sources as a follow-up message or attach to the main message
        if sources:
            sources_text = "\n".join([f"- {s}" for s in sources])
            say(text=f"*Sources: *\n{sources_text}", thread_ts=thread_ts)

    except Exception as e:
        logger.error(f"Error processing Slack event with Bedrock: {e}", exc_info=True)
        say(f"Sorry, I encountered an error processing your request: {e}")


# --- Event Listeners ---


# Event Listener for App Mentions (New Conversations OR Mentions in existing threads)
@app.event("app_mention", lazy=[process_slack_event_lazily])  # Use lazy listener
def handle_app_mention_events(body, ack):
    ack()  # Acknowledge the event immediately
    # Check for Slack retries
    retry_num = body.get("X-Slack-Retry-Num")
    if retry_num and int(retry_num) > 0:
        logger.info(
            f"Ignoring app_mention retry event (X-Slack-Retry-Num: {retry_num})."
        )
        return


# Event Listener for Messages (Follow-ups in Threads and DMs)
@app.event("message", lazy=[process_slack_event_lazily])  # Use lazy listener
def handle_message_events(body, ack):
    ack()  # Acknowledge the event immediately
    # Check for Slack retries
    retry_num = body.get("X-Slack-Retry-Num")
    if retry_num and int(retry_num) > 0:
        logger.info(f"Ignoring message retry event (X-Slack-Retry-Num: {retry_num}).")
        return


# --- Main Lambda Handler ---
def handler(event, context):
    # Force logging to work for initial Lambda invocation
    print(f"Lambda invoked! Event: {json.dumps(event, default=str)}")
    logger.info(f"Lambda invoked! Event: {json.dumps(event, default=str)}")

    # Simply pass the event to the SlackRequestHandler.
    # slack_bolt will internally manage the lazy listener invocation.
    response = slack_handler.handle(event, context)
    print(f"API Gateway response: {response}")
    return response
