# filename: utils/slackbot_helper.py

import logging
import os
import base64
import requests
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.documents import Document
from utils.prompts import (
    slack_system_prompt_with_tools as slack_system_prompt,
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


def create_retrieve_context_tool(retriever):
    """Create the retrieve_context tool for LangChain."""
    def retrieve_context_tool(query: str):
        from utils.chatbot_helper import retrieve_context
        logger.info(f"retrieve_context_tool: Retrieving context for query: '{query}'")
        context, relevant_docs = retrieve_context(retriever=retriever, prompt=query)
        # Convert relevant_docs to a serializable format
        serializable_docs = []
        for doc in relevant_docs:
            serializable_docs.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })
        return {"context": context, "relevant_docs": serializable_docs}
    
    return retrieve_context_tool


def create_multimodal_message(cleaned_user_text, files):
    """Create a multimodal message with text and images."""
    current_turn_content_parts = []

    if cleaned_user_text:
        current_turn_content_parts.append(
            {"type": "text", "text": cleaned_user_text}
        )
    else:  # If there was no text but there are images
        current_turn_content_parts.append(
            {"type": "text", "text": "Please help me with the following image(s):"}
        )

    # Process and add images from the current message
    process_image_files(files, current_turn_content_parts, "attached")

    return HumanMessage(content=current_turn_content_parts)


def generate_ai_response_with_tools(llm, final_history, retrieve_context_tool):
    """Generate AI response using LangChain tools and add disclaimer."""
    try:
        logger.info("Starting generate_ai_response_with_tools")
        
        # First pass: Get response potentially with tool calls
        first_pass_response_obj = llm.invoke(final_history, tools=[retrieve_context_tool], tool_choice="auto")
        
        # Handle content that might be a string or list
        full_response_text = ""
        if first_pass_response_obj.content:
            if isinstance(first_pass_response_obj.content, str):
                full_response_text = first_pass_response_obj.content
            elif isinstance(first_pass_response_obj.content, list):
                # Extract text from multimodal content
                text_parts = [part.get("text", "") for part in first_pass_response_obj.content if isinstance(part, dict) and part.get("type") == "text"]
                full_response_text = " ".join(text_parts)
            else:
                full_response_text = str(first_pass_response_obj.content)
        
        tool_calls_made = first_pass_response_obj.tool_calls if hasattr(first_pass_response_obj, "tool_calls") else []
        logger.info(f"First pass response: '{full_response_text[:100]}...', Tool calls made: {len(tool_calls_made)}")
        
        # If tool calls were made, execute them and get final response
        if tool_calls_made:
            logger.info(f"Executing {len(tool_calls_made)} tool calls")
            
            # Add the AI message with tool calls to history
            ai_message_with_tools = AIMessage(
                content=full_response_text,
                tool_calls=tool_calls_made
            )
            updated_history = final_history + [ai_message_with_tools]
            
            # Execute tool calls and add tool messages
            for i, tool_call in enumerate(tool_calls_made):
                logger.info(f"Executing tool call {i+1}: {tool_call.get('name', 'unknown')} with args: {tool_call.get('args', {})}")
                
                if tool_call["name"] == "retrieve_context_tool":
                    tool_output = retrieve_context_tool(**tool_call["args"])
                    context = tool_output.get("context", "No context found.")
                    logger.info(f"Tool call {i+1} returned context length: {len(context)} chars")
                    
                    # Create tool message in Bedrock format
                    tool_message = HumanMessage(
                        content=[
                            {"toolResult": {
                                "toolUseId": tool_call["id"],
                                "content": [{"text": context}]
                            }}
                        ]
                    )
                    updated_history.append(tool_message)
                else:
                    logger.warning(f"Unknown tool call: {tool_call['name']}")
            
            logger.info(f"Updated history length after tool execution: {len(updated_history)}")
            
            # Get final response after tool execution
            final_response_obj = llm.invoke(updated_history, tools=[retrieve_context_tool], tool_choice="auto")
            
            # Handle final response content that might be a string or list
            response_content = ""
            if final_response_obj.content:
                if isinstance(final_response_obj.content, str):
                    response_content = final_response_obj.content
                elif isinstance(final_response_obj.content, list):
                    # Extract text from multimodal content
                    text_parts = [part.get("text", "") for part in final_response_obj.content if isinstance(part, dict) and part.get("type") == "text"]
                    response_content = " ".join(text_parts)
                else:
                    response_content = str(final_response_obj.content)
            
            logger.info(f"Final response after tool execution: '{response_content[:100]}...'")
        else:
            logger.info("No tool calls made, using first pass response")
            response_content = full_response_text
        
        disclaimer = "\n\n* *Generative AI is experimental. Please verify answers using official documentation.*"
        final_result = response_content + disclaimer
        logger.info(f"Returning final response length: {len(final_result)} chars")
        return final_result
        
    except Exception as e:
        logger.error(f"Error in generate_ai_response_with_tools: {e}", exc_info=True)
        return "Sorry, I encountered an error while generating the response."
