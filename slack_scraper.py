import logging
import os
import boto3
from datetime import datetime
from dotenv import load_dotenv
from slack_bolt import App

# Load Environment Variables
load_dotenv()

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Slack App Initialization
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


def scrape_channel_conversations(channel_id, limit=200):
    """
    Scrape the last 200 conversation messages/threads from a channel.
    Each thread is limited to 5 messages.
    """
    try:
        # Get the last 5 messages from the channel
        result = app.client.conversations_history(channel=channel_id, limit=limit)

        messages = result.get("messages", [])
        conversations = []

        for msg in messages:
            conversation = {
                "timestamp": msg.get("ts"),
                "user": msg.get("user"),
                "text": msg.get("text", ""),
                "thread_messages": [],
            }

            # If this message has a thread, get thread replies (limited to 5)
            if msg.get("thread_ts"):
                thread_result = app.client.conversations_replies(
                    channel=channel_id, ts=msg["thread_ts"], limit=5
                )

                thread_messages = thread_result.get("messages", [])
                for thread_msg in thread_messages[1:]:  # Skip the parent message
                    conversation["thread_messages"].append(
                        {
                            "timestamp": thread_msg.get("ts"),
                            "user": thread_msg.get("user"),
                            "text": thread_msg.get("text", ""),
                        }
                    )

            conversations.append(conversation)

        return conversations

    except Exception as e:
        logger.error(f"Error scraping channel {channel_id}: {e}")
        return []


def upload_markdown_to_s3(markdown_content, conversation_count, bucket_name, s3_key):
    """Upload markdown data to S3"""
    try:
        s3 = boto3.client("s3")
        current_datetime = datetime.now().isoformat()
        metadata = {
            "ScrapedDatetime": current_datetime,
            "ChannelId": "C05L060P5NF",
            "ConversationCount": str(conversation_count),
        }
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=markdown_content,
            ContentType="text/markdown",
            Metadata=metadata,
        )
        logger.info(f"Successfully uploaded to s3://{bucket_name}/{s3_key}")
        return True
    except Exception as e:
        logger.error(f"Error uploading to S3: {e}")
        return False


def convert_to_markdown(conversations):
    """Convert JSON conversations to human-readable markdown format"""
    markdown = f"# Slack Conversations\n\nScraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    for i, conv in enumerate(conversations, 1):
        markdown += f"## Conversation {i}\n\n"
        markdown += f"**User:** {conv['user']}\n"
        markdown += f"**Timestamp:** {conv['timestamp']}\n\n"
        markdown += f"{conv['text']}\n\n"

        if conv["thread_messages"]:
            markdown += "### Thread Replies:\n\n"
            for j, reply in enumerate(conv["thread_messages"], 1):
                markdown += f"**Reply {j}** (User: {reply['user']}):\n"
                markdown += f"{reply['text']}\n\n"

        markdown += "---\n\n"

    return markdown


def main():
    # channel_id of tech-help channel
    channel_id = "C05L060P5NF"

    conversations = scrape_channel_conversations(channel_id)

    # Convert to markdown
    markdown_content = convert_to_markdown(conversations)

    # S3 configuration
    bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_folder = "slack_conversations/"
    s3_key = f"{s3_folder}slack_conversations.md"

    # Upload markdown to S3
    if bucket_name:
        upload_markdown_to_s3(markdown_content, len(conversations), bucket_name, s3_key)
    else:
        logger.warning("S3_BUCKET_NAME not set, cannot save conversations")

    logger.info(f"Scraped {len(conversations)} conversations from channel {channel_id}")

    # Print summary
    for i, conv in enumerate(conversations):
        print(f"Conversation {i + 1}:")
        print(f"  User: {conv['user']}")
        print(f"  Text: {conv['text']}...")
        print(f"  Thread replies: {len(conv['thread_messages'])}")
        print()


if __name__ == "__main__":
    main()
