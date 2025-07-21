# filename: utils/slackbot_helper.py

import logging
import os
import base64
import requests
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from utils.prompts import (
    question_system_prompt,
    slack_system_prompt_with_followups as slack_system_prompt,
)

logger = logging.getLogger(__name__)


def get_text_from_message(message):
    """Helper to extract text from multimodal messages for text-only processing."""
    if isinstance(message.content, str):
        return message.content
    if isinstance(message.content, list):
        return " ".join(
            [part["text"] for part in message.content if part["type"] == "text"]
        )
    return ""


def download_and_encode_image(url_private, timeout=10):
    """Download and base64 encode an image from Slack."""
    try:
        response = requests.get(
            url_private,
            headers={"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"},
            timeout=timeout,
        )
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to download/process image: {e}")
        raise


def process_image_files(files, message_content_parts, context_type="historical"):
    """Process image files and add them to message content parts."""
    if not files:
        return

    for file in files:
        if file.get("mimetype") in [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
        ]:
            logger.info(
                f"Found image file in {context_type} message: {file.get('name')}"
            )
            url_private = file.get("url_private")
            if url_private:
                try:
                    base64_image = download_and_encode_image(url_private)
                    message_content_parts.append(
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": file.get("mimetype"),
                                "data": base64_image,
                            },
                        }
                    )
                    logger.info(
                        f"Successfully processed {context_type} image: {file.get('name')}"
                    )
                except Exception as img_e:
                    logger.error(
                        f"Failed to download/process {context_type} image {file.get('name')}: {img_e}"
                    )


def reconstruct_history_from_slack(
    client, channel_id, thread_ts, bot_user_id, bot_id_from_auth=None
):
    """Reconstructs conversation history from Slack thread."""
    if not bot_user_id:
        logger.error("Cannot reconstruct history: bot_user_id is not set.")
        return [SystemMessage(content=slack_system_prompt)]

    history = [SystemMessage(content=slack_system_prompt)]
    try:
        result = client.conversations_replies(
            channel=channel_id, ts=thread_ts, limit=200
        )
        messages = result.get("messages", [])
        logger.info(
            f"Fetched {len(messages)} messages from Slack for thread {thread_ts}."
        )

        for msg in sorted(messages, key=lambda x: float(x["ts"])):
            msg_text = msg.get("text", "")
            msg_user = msg.get("user")
            msg_bot_id = msg.get("bot_id")

            # Check if this is a bot message
            is_bot_message = (
                msg_bot_id == bot_id_from_auth or msg_bot_id or msg_user == bot_user_id
            )

            if is_bot_message:
                if msg_text:
                    history.append(AIMessage(content=msg_text))
            elif msg_user:
                # A HumanMessage can contain a list of content parts (text and images).
                message_content_parts = []

                # Part 1: Add the text content
                cleaned_text = msg_text
                if msg["ts"] == thread_ts:  # If it's the root message
                    cleaned_text = msg_text.replace(f"<@{bot_user_id}>", "").strip()

                if cleaned_text:
                    message_content_parts.append({"type": "text", "text": cleaned_text})

                # Part 2: Check for and add image content
                process_image_files(
                    msg.get("files", []), message_content_parts, "historical"
                )

                if message_content_parts:
                    history.append(HumanMessage(content=message_content_parts))

        logger.info(
            f"Reconstructed history for thread {thread_ts} with {len(history) - 1} turns."
        )
    except Exception as e:
        logger.error(
            f"Error reconstructing history from Slack for thread {thread_ts}: {e}",
            exc_info=True,
        )
        return [SystemMessage(content=slack_system_prompt)]
    return history


def create_optimized_query(llm, current_thread_history, query_prompt_text):
    """Create an optimized search query using the LLM."""
    # For query optimization, use a text-only representation of the history.
    text_only_history = [SystemMessage(content=question_system_prompt)]
    if len(current_thread_history) > 1:  # If there's more than the system prompt
        for msg in current_thread_history[1:]:  # Skip system prompt
            text_only_history.append(
                HumanMessage(content=get_text_from_message(msg))
                if isinstance(msg, HumanMessage)
                else msg
            )

    # Construct messages for the query optimization LLM call
    messages_for_query_optimization_llm = text_only_history[
        :-1
    ]  # History up to before the current turn
    messages_for_query_optimization_llm.append(
        HumanMessage(
            content=f'Based on the conversation history (if any), generate an optimized search query for the following user question: "{query_prompt_text}"'
        )
    )

    try:
        # Get the optimized query from the LLM based on text
        query_response = llm.invoke(messages_for_query_optimization_llm)
        optimized_query = query_response.content.strip()
        logger.info(f"Generated optimized query: '{optimized_query}'")
        return optimized_query if optimized_query else query_prompt_text
    except Exception as e:
        logger.error(f"Error generating optimized query: {e}")
        return query_prompt_text


def create_multimodal_message(cleaned_user_text, context, files):
    """Create a multimodal message with text and images."""
    current_turn_content_parts = []

    if cleaned_user_text:
        # The augmented prompt combines RAG context with the user's text
        augmented_text_prompt = f"Context:\n{context}\n\nQuestion: {cleaned_user_text}"
        current_turn_content_parts.append(
            {"type": "text", "text": augmented_text_prompt}
        )
    else:  # If there was no text, we still want to provide the RAG context
        augmented_text_prompt_for_image = (
            f"Context:\n{context}\n\n"
            "User question regarding the following image(s): Describe the image(s) and relate them to the provided context if possible."
        )
        current_turn_content_parts.append(
            {"type": "text", "text": augmented_text_prompt_for_image}
        )

    # Process and add images from the current message
    process_image_files(files, current_turn_content_parts, "attached")

    return HumanMessage(content=current_turn_content_parts)


def generate_ai_response(llm, final_history):
    """Generate AI response and add disclaimer."""
    ai_response = llm.invoke(final_history)
    ai_message_content = (
        ai_response.content if hasattr(ai_response, "content") else str(ai_response)
    )
    disclaimer = "\n\n* *Generative AI is experimental. Please verify answers using official documentation.*"
    return ai_message_content + disclaimer
