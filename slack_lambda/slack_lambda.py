import logging
import os
import json
import boto3

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage # Added Langchain message types
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# Re-added Bedrock and related imports
from utils.chatbot_helper import (
    logger as chatbot_logger,
    initialize_llm,
    initialize_knowledge_base_retriever
)

# Define convert_to_langchain_messages locally
def convert_to_langchain_messages(slack_messages, bot_user_id):
    langchain_messages = []
    for msg in slack_messages:
        # Skip bot messages that are not responses from our bot (e.g., app mention itself)
        if msg.get("bot_id") and msg.get("bot_id") != bot_user_id:
            continue

        text = msg.get("text", "").strip()
        if not text:
            continue

        # Determine sender and message type
        if msg.get("user") == bot_user_id or msg.get("bot_id") == bot_user_id:
            # Message from the bot
            langchain_messages.append(AIMessage(content=text))
        else:
            # Message from a user
            langchain_messages.append(HumanMessage(content=text))
    return langchain_messages

# Initialize global variables for Bedrock client, LLM, and retriever
bedrock_client = None
llm = None
retriever = None

# process_before_response must be True when running on FaaS
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    # Set to False because we will manually handle async invocation for events
    process_before_response=False,  # Changed to False for manual async handling
)


# New lazy function to process Slack events asynchronously
def process_slack_event_lazily(body, say, client):
    global bedrock_client, llm, retriever

    # Initialize Bedrock client, LLM, and retriever if not already initialized (cold start)
    if bedrock_client is None:
        try:
            print("Initializing Bedrock client, LLM, and retriever...")
            # Changed to bedrock-agent-runtime as used in chatbot_helper
            bedrock_client = boto3.client("bedrock-agent-runtime", region_name='us-east-1') 
            llm = initialize_llm(bedrock_client)
            retriever = initialize_knowledge_base_retriever() # Use initialize_knowledge_base_retriever function
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
    event_data = body.get("event", {})
    user_text_raw = event_data.get("text", "No text found")
    channel_id = event_data.get("channel", "")
    user_id = event_data.get("user", "")
    thread_ts = event_data.get("thread_ts", event_data.get("ts"))

    if not user_text_raw:
        chatbot_logger.info("Received empty message or event without text.")
        return

    print(
        f"Processing message from {user_id} in channel {channel_id}, thread {thread_ts}: {user_text_raw}"
    )

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
                limit=5,  # Limit to last 5 messages for context
            )
            messages = history["messages"]
            # Convert Slack messages to LangChain messages
            conversation_history = convert_to_langchain_messages(
                messages, os.environ.get("SLACK_BOT_ID")
            )
            chatbot_logger.info(f"Conversation history fetched: {conversation_history}")
        except Exception as e:
            chatbot_logger.error(
                f"Error fetching conversation history: {e}", exc_info=True
            )
            # Continue without history if there's an error
            pass

    try:
        # Generate response using BedrockAgent (assuming invoke now directly returns text and sources)
        response_text, sources = llm.invoke(
            conversation_history + [HumanMessage(content=user_text_query)],
            config={'retriever': retriever} if retriever else None
        ) # Modified invoke call to use correct Langchain format and pass retriever as config

        # Remove bot mention from the user query
        bot_id = os.environ.get("SLACK_BOT_ID")
        user_text_query = user_text_raw.replace(f"<@{bot_id}>", "").strip()

        if not user_text_query:
            chatbot_logger.info("Received empty message after removing bot mention.")
            return  # Do nothing for empty messages

        chatbot_logger.info(f"User query for Bedrock: {user_text_query}")

        # Post the response back to Slack
        say(text=response_text, thread_ts=thread_ts)

        # Optionally, send sources as a follow-up message or attach to the main message
        if sources:
            sources_text = "\n".join([f"- {s}" for s in sources])
            say(text=f"*Sources: *\n{sources_text}", thread_ts=thread_ts)

    except Exception as e:
        chatbot_logger.error(
            f"Error processing message with Bedrock: {e}", exc_info=True
        )
        say(f"An error occurred while processing your request: {e}")


# Event Listener for App Mentions (New Conversations OR Mentions in existing threads)
@app.event("app_mention")
def handle_app_mention_events(body, ack, context):
    ack()  # Acknowledge the event immediately
    # Asynchronously invoke the Lambda for actual processing
    lambda_client = boto3.client("lambda")
    # Ensure the payload includes a flag for async invocation
    payload = json.dumps({"x-slack-async-invoke": True, "body": body})
    lambda_client.invoke(
        FunctionName=context.invoked_function_arn.split(":")[
            6
        ],  # Get function name from ARN
        InvocationType="Event",  # Asynchronous invocation
        Payload=payload,
    )


# Event Listener for Messages (Follow-ups in Threads and DMs)
@app.event("message")
def handle_message_events(body, ack, context):
    ack()  # Acknowledge the event immediately
    # Asynchronously invoke the Lambda for actual processing
    lambda_client = boto3.client("lambda")
    # Ensure the payload includes a flag for async invocation
    payload = json.dumps({"x-slack-async-invoke": True, "body": body})
    lambda_client.invoke(
        FunctionName=context.invoked_function_arn.split(":")[
            6
        ],  # Get function name from ARN
        InvocationType="Event",  # Asynchronous invocation
        Payload=payload,
    )


# Clear all existing log handlers and set up basic logging
SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


def handler(event, context):
    print(f"Lambda invoked! Event: {json.dumps(event, default=str)}")

    # Check if this is an asynchronous self-invocation
    if event.get("x-slack-async-invoke") and event.get("body"):
        print("Detected asynchronous self-invocation. Processing event lazily.")
        # Unpack the original event body and process it
        original_body = event["body"]
        slack_handler = SlackRequestHandler(app=app)
        # Manually call the appropriate event handler or process directly
        # For this simplified test, we'll directly call the lazy function
        # In a real app, you might re-dispatch based on event type
        process_slack_event_lazily(
            original_body,
            slack_handler.create_say_instance(original_body),
            slack_handler.create_client_instance(),
        )
        return {"statusCode": 200, "body": "Lazy processing initiated."}
    else:
        print(
            "Detected initial API Gateway invocation. Acknowledging Slack immediately."
        )
        # This is the initial invocation from API Gateway (Slack).
        # Bolt will internally handle the acknowledgment for standard events.
        slack_handler = SlackRequestHandler(app=app)
        return slack_handler.handle(event, context)
