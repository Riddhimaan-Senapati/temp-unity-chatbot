import logging
import os
import json
import sys # Added sys import back

# Explicitly add the current directory to Python path to ensure bundled modules are found
sys.path.insert(0, os.path.dirname(__file__))

from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# process_before_response must be True when running on FaaS
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True, # Ensure this is True for lazy listeners
)

# This function will be executed asynchronously by slack_bolt's lazy listener.
def process_slack_event_lazily(body, say, client):
    # This is a test message to confirm lazy listener is triggered
    print("DEBUG: process_slack_event_lazily triggered!")
    event = body.get("event", {})
    user_text_raw = event.get("text", "No text found")
    channel_id = event.get("channel", "")
    thread_ts = event.get("thread_ts", event.get("ts"))
    user_id = event.get("user", "")

    print(f"DEBUG: Processing lazy event from {user_id} in channel {channel_id}, thread {thread_ts}: {user_text_raw}")
    say(text=f"Hello from lazy listener! You said: {user_text_raw}", thread_ts=thread_ts)

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
