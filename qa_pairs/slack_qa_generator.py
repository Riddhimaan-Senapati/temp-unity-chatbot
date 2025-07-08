import logging
import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Add parent directory to path to import chatbot_helper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.chatbot_helper import initialize_bedrock_client, initialize_llm
from utils.prompts import QA_SYSTEM_PROMPT

# Load Environment Variables
load_dotenv()

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_conversations_from_markdown(markdown_content):
    """Parse individual conversations from markdown content"""
    conversations = []
    current_conversation = ""

    lines = markdown_content.split("\n")
    in_conversation = False

    for line in lines:
        if line.startswith("## Conversation"):
            if current_conversation and in_conversation:
                conversations.append(current_conversation.strip())
            current_conversation = ""
            in_conversation = True
        elif line.startswith("---") and in_conversation:
            if current_conversation:
                conversations.append(current_conversation.strip())
            current_conversation = ""
            in_conversation = False
        elif in_conversation:
            current_conversation += line + "\n"

    # Add the last conversation if exists
    if current_conversation and in_conversation:
        conversations.append(current_conversation.strip())

    logger.info(f"Parsed {len(conversations)} conversations from markdown")
    return conversations


def generate_qa_pairs(llm, conversation_text):
    """Generate Q&A pairs from a single conversation using LLM"""
    try:
        messages = [
            {"role": "system", "content": QA_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Convert this Slack conversation thread into Q&A pairs:\n\n{conversation_text}",
            },
        ]

        response = llm.invoke(messages)
        response_text = response.content.strip()

        # Clean up response text - remove markdown code blocks if present
        if "```json" in response_text:
            # Extract JSON from markdown code blocks
            start_idx = response_text.find("```json") + 7
            end_idx = response_text.find("```", start_idx)
            if end_idx != -1:
                response_text = response_text[start_idx:end_idx].strip()
        elif "```" in response_text:
            # Handle generic code blocks
            start_idx = response_text.find("```") + 3
            end_idx = response_text.find("```", start_idx)
            if end_idx != -1:
                response_text = response_text[start_idx:end_idx].strip()

        # Try to parse JSON response
        try:
            qa_pairs = json.loads(response_text)
            if isinstance(qa_pairs, list):
                # Filter out Q&A pairs with no answers (empty array)
                filtered_qa_pairs = []
                for qa_pair in qa_pairs:
                    if isinstance(qa_pair, dict):
                        answers = qa_pair.get("answers", [])
                        # Skip if answers is empty or not a list
                        if (
                            answers
                            and isinstance(answers, list)
                            and any(
                                ans.strip() for ans in answers if isinstance(ans, str)
                            )
                        ):
                            filtered_qa_pairs.append(qa_pair)
                        else:
                            logger.info(
                                f"Skipping Q&A pair with no valid answers: {qa_pair.get('question', 'Unknown question')[:50]}..."
                            )
                return filtered_qa_pairs
            else:
                return []
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON response: {response_text[:100]}...")
            return []

    except Exception as e:
        logger.error(f"Error generating Q&A pairs: {e}")
        return []


def save_qa_pairs_to_s3(
    qa_pairs, filename="slack_qa_pairs.json", output_dir="slack_conversations"
):
    """Save Q&A pairs to S3 in slack_conversations folder"""
    try:
        S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

        if not S3_BUCKET_NAME:
            logger.error("S3_BUCKET_NAME not found in environment variables")
            return False

        # Create S3 client
        s3 = boto3.client("s3")

        # Create S3 key
        s3_key = f"{output_dir}/{filename}"

        # Create the data structure
        data = {
            "generated_at": datetime.now().isoformat(),
            "total_pairs": len(qa_pairs),
            "source": "slack_conversations",
            "qa_pairs": qa_pairs,
        }

        # Convert to JSON
        content = json.dumps(data, indent=2, ensure_ascii=False)

        # Upload to S3
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=content,
            ContentType="application/json",
            Metadata={
                "generated_at": datetime.now().isoformat(),
                "total_pairs": str(len(qa_pairs)),
                "source": "slack_conversations",
            },
        )

        logger.info(
            f"Saved {len(qa_pairs)} Q&A pairs to S3: s3://{S3_BUCKET_NAME}/{s3_key}"
        )
        return True

    except Exception as e:
        logger.error(f"Error saving Q&A pairs to S3: {e}")
        return False


def get_markdown_from_s3(s3_key="slack_conversations/slack_conversations.md"):
    """Get markdown content from S3"""
    try:
        S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

        if not S3_BUCKET_NAME:
            logger.error("S3_BUCKET_NAME not found in environment variables")
            return None

        # Create S3 client
        s3 = boto3.client("s3")

        # Get object from S3
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        content = response["Body"].read().decode("utf-8")

        logger.info(
            f"Successfully read markdown from S3: s3://{S3_BUCKET_NAME}/{s3_key}"
        )
        return content

    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            logger.error(f"File not found in S3: {s3_key}")
        else:
            logger.error(f"S3 error reading markdown from S3: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading markdown from S3: {e}")
        return None


def main():
    """Main function that reads Slack conversations from S3"""
    # Initialize Bedrock LLM
    logger.info("Initializing Bedrock client and LLM...")
    bedrock_client = initialize_bedrock_client()
    llm = initialize_llm(
        client=bedrock_client, model_id="us.anthropic.claude-sonnet-4-20250514-v1:0"
    )

    # Get markdown content from S3
    logger.info("Reading Slack conversations from S3...")
    markdown_content = get_markdown_from_s3(
        "slack_conversations/slack_conversations.md"
    )

    if not markdown_content:
        logger.error("Failed to retrieve markdown content from S3")
        return False

    # Parse conversations from markdown
    conversations = parse_conversations_from_markdown(markdown_content)

    if not conversations:
        logger.warning("No conversations found in markdown content")
        return False

    # Generate Q&A pairs for each conversation
    logger.info(f"Processing {len(conversations)} conversations...")
    all_qa_pairs = []

    for i, conversation in enumerate(conversations, 1):
        logger.info(f"Processing conversation {i}/{len(conversations)}")
        qa_pairs = generate_qa_pairs(llm, conversation)

        if qa_pairs:
            all_qa_pairs.extend(qa_pairs)
            logger.info(f"Generated {len(qa_pairs)} Q&A pairs from conversation {i}")
        else:
            logger.info(f"No Q&A pairs generated from conversation {i}")

    # Save Q&A pairs to S3 in slack_conversations directory
    if all_qa_pairs:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"slack_qa_pairs_{timestamp}.json"

        if save_qa_pairs_to_s3(
            all_qa_pairs, filename, output_dir="slack_conversations"
        ):
            logger.info(f"Successfully generated {len(all_qa_pairs)} total Q&A pairs")

            # Print summary
            print("\n=== Q&A Generation Summary ===")
            print(f"Conversations processed: {len(conversations)}")
            print(f"Q&A pairs generated: {len(all_qa_pairs)}")
            print(
                f"Output file: s3://{os.getenv('S3_BUCKET_NAME')}/slack_conversations/{filename}"
            )

            # Show first few examples
            print("\n=== Sample Q&A Pairs ===")
            for i, qa in enumerate(all_qa_pairs[:3], 1):
                print(f"\nQ{i}: {qa.get('question', 'N/A')}")
                answers = qa.get("answers", [])
                if answers:
                    print(f"A{i}: {answers[0][:100]}...")
                else:
                    print(f"A{i}: No answers found")

            return True
        else:
            logger.error("Failed to save Q&A pairs to S3")
            return False
    else:
        logger.warning("No Q&A pairs were generated from any conversations")
        return False


if __name__ == "__main__":
    main()
