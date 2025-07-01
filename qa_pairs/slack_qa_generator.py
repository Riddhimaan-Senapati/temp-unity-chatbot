import logging
import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv

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
            return qa_pairs if isinstance(qa_pairs, list) else []
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON response: {response_text[:100]}...")
            return []

    except Exception as e:
        logger.error(f"Error generating Q&A pairs: {e}")
        return []


def save_qa_pairs_locally(
    qa_pairs, filename="slack_qa_pairs.json", output_dir="qa_pairs"
):
    """Save Q&A pairs to local JSON file in specified directory"""
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Create full file path
        file_path = os.path.join(output_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(qa_pairs)} Q&A pairs to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving Q&A pairs locally: {e}")
        return False


def get_markdown_from_local(local_file_path, search_dir="qa_pairs"):
    """Get markdown content from local file, searching in specified directory"""
    try:
        # First try the file path as given
        if os.path.exists(local_file_path):
            file_path = local_file_path
        else:
            # Try in the search directory
            file_path = os.path.join(search_dir, local_file_path)
            if not os.path.exists(file_path):
                logger.error(f"Local file not found: {local_file_path} or {file_path}")
                return None

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        logger.info(f"Successfully read markdown from local file: {file_path}")
        return content

    except Exception as e:
        logger.error(f"Error reading local markdown file: {e}")
        return None


def main():
    # Configuration
    qa_pairs_dir = "qa_pairs"  # Directory to search for markdown files and save output
    local_markdown_file = "slack_conversations.md"  # Local file to process

    # Initialize Bedrock LLM
    logger.info("Initializing Bedrock client and LLM...")
    bedrock_client = initialize_bedrock_client()
    llm = initialize_llm(
        client=bedrock_client, model_id="us.anthropic.claude-sonnet-4-20250514-v1:0"
    )

    # Get markdown content from local file (search in qa_pairs directory)
    logger.info(f"Reading Slack conversations from: {local_markdown_file}")
    markdown_content = get_markdown_from_local(
        local_markdown_file, search_dir=qa_pairs_dir
    )

    if not markdown_content:
        logger.error(f"Failed to retrieve markdown content from {local_markdown_file}")
        return

    # Parse conversations from markdown
    conversations = parse_conversations_from_markdown(markdown_content)

    if not conversations:
        logger.warning("No conversations found in markdown content")
        return

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

    # Save Q&A pairs locally in qa_pairs directory
    if all_qa_pairs:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"slack_qa_pairs_{timestamp}.json"

        if save_qa_pairs_locally(all_qa_pairs, filename, output_dir=qa_pairs_dir):
            logger.info(f"Successfully generated {len(all_qa_pairs)} total Q&A pairs")

            # Print summary
            print("\n=== Q&A Generation Summary ===")
            print(f"Conversations processed: {len(conversations)}")
            print(f"Q&A pairs generated: {len(all_qa_pairs)}")
            print(f"Output file: {os.path.join(qa_pairs_dir, filename)}")

            # Show first few examples
            print("\n=== Sample Q&A Pairs ===")
            for i, qa in enumerate(all_qa_pairs[:3], 1):
                print(f"\nQ{i}: {qa.get('question', 'N/A')}")
                answers = qa.get("answers", [])
                if answers:
                    print(f"A{i}: {answers[0][:100]}...")
                else:
                    print(f"A{i}: No answers found")
        else:
            logger.error("Failed to save Q&A pairs locally")
    else:
        logger.warning("No Q&A pairs were generated from any conversations")


if __name__ == "__main__":
    main()
