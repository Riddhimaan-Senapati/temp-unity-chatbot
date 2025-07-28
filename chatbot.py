import logging  # Added for logging
import os

import streamlit as st
from dotenv import load_dotenv

from utils.chatbot_helper import (
    initialize_bedrock_client,
    initialize_knowledge_base_retriever,
    initialize_llm,
    retrieve_context,
)
from utils.feedback import display_feedback_form, display_feedback_form_for_sources
from langchain_core.documents import Document # Moved import to top
from langchain_core.messages import ToolMessage # Import ToolMessage
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage # Added for LangChain BaseMessage

from utils.prompts import main_system_prompt_with_tools

# load the environment variables
load_dotenv()

# --- Initialize Logging ---
# You can set the level to logging.DEBUG to see more verbose logs
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# --- End Logging Initialization ---

st.set_page_config(page_title="🧠 Unity HPC Chatbot")
st.title("🧠 Unity HPC Chatbot")

# Authentication Logic
UNITY_USERNAME = os.getenv("UNITY_USERNAME")
UNITY_PASSWORD = os.getenv("UNITY_PASSWORD")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.header("Login")
    with st.form("login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            if username_input == UNITY_USERNAME and password_input == UNITY_PASSWORD:
                st.session_state.logged_in = True
                # Log successful login
                logger.info(f"User '{username_input}' logged in successfully.")
                st.success("Logged in successfully!")
                st.rerun()  # rerun to display the app content
            else:
                # Log failed login attempt
                logger.warning(
                    f"Failed login attempt for username: '{username_input}'."
                )
                st.error("Incorrect username or password.")
    st.stop()  # Stop execution if not logged in


# If we reach here, the user is logged in
def logout_action_with_logging():
    # Log logout action
    # Attempt to get username if it was stored or use a placeholder
    logged_in_username = getattr(
        st.session_state, "username_input_on_login", "Unknown User"
    )
    logger.info(f"User '{logged_in_username}' initiated logout.")
    st.session_state.update(logged_in=False, messages=[])
    # Log successful logout and session clear
    logger.info("User logged out, session messages cleared.")


st.sidebar.button(
    "Logout",
    on_click=logout_action_with_logging,  # Changed to use the new function with logging
)

# Add source count configuration in sidebar
source_count = st.sidebar.slider(
    "Number of Sources",
    min_value=5,
    max_value=20,
    value=10,
    help="Choose how many sources to retrieve for context",
)

# Privacy Warning
st.warning(
    "⚠️ **Privacy Notice**: Do not share personal information. Conversation history may be stored for system improvement purposes."
)

# Initialize Bedrock client
# Log Bedrock client initialization attempt
logger.info("Initializing Bedrock client...")
bedrock_client = initialize_bedrock_client()

# Initialize ChatBedrockConverse LLM
# Log LLM initialization attempt
logger.info("Initializing LLM...")
llm = initialize_llm(client=bedrock_client)

# Initialize the Knowledge Base retriever
# Log Retriever initialization attempt
logger.info("Initializing Knowledge Base retriever...")
retriever = initialize_knowledge_base_retriever(source_count)

# Define the tool-compatible wrapper for retrieve_context
def retrieve_context_tool(query: str):
    logger.info(f"retrieve_context_tool called with query: '{query}'")
    context, relevant_docs = retrieve_context(retriever=retriever, prompt=query)
    # Convert relevant_docs to a serializable format if necessary for the tool output
    # For now, assuming relevant_docs are already compatible or can be directly returned
    # If relevant_docs contains non-serializable objects (e.g., Doc instances),
    # you might need to convert them to dictionaries or a simpler structure.
    serializable_docs = []
    for doc in relevant_docs:
        serializable_docs.append({
            "page_content": doc.page_content,
            "metadata": doc.metadata
        })
    return {"context": context, "relevant_docs": serializable_docs}

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Log when initial system prompt is added to messages
    logger.info("Initializing chat messages with main system prompt.")
    # Add the system prompt to the beginning of the messages
    st.session_state.messages.append(SystemMessage(content=main_system_prompt_with_tools))

# store messages for short-term memory
# displays all messages, except the first one which is a system prompt
for i, message in enumerate(st.session_state.messages):
    if message.type == "system": # Access type attribute directly
        continue
    
    # Determine the role for st.chat_message display
    display_role = "user" if message.type == "human" else message.type
    with st.chat_message(display_role):
        # Display text content
        if isinstance(message.content, str):
            st.markdown(message.content)
        elif isinstance(message.content, list):
            # Handle multimodal content
            for part in message.content:
                if part["type"] == "text":
                    st.markdown(part["text"])

        # Display images if they exist
        if hasattr(message, "images") and message.images:
            for img_file in message.images:
                st.image(img_file, caption=img_file.name, width=300)

        # Display sources if they exist in the message
        if (
            message.type == "assistant" # Access type attribute directly
            and hasattr(message, "sources")
            and message.sources
        ):
            st.markdown("---")
            st.markdown("**Sources**")
            for j, doc in enumerate(message.sources):
                if isinstance(doc, Document): # Defensive check
                    with st.expander(f"🔍 Source {j + 1}"):
                        st.text(doc.page_content)
                        # Add source-specific feedback form
                        source_unique_key = f"{len(st.session_state.messages)}_source_{j}_{hash(doc.page_content) % 10000}"
                        # For historical messages, get the user question from the previous message
                        user_question = "N/A"  # Default
                        if j > 0 and st.session_state.messages[j - 1].type == "human": # Access type attribute directly
                            user_question = st.session_state.messages[j - 1].content # Access content attribute directly
                        
                        # Ensure response_content is always a string for feedback form
                        response_content_for_feedback_sources = message.content # Access content attribute directly
                        if isinstance(response_content_for_feedback_sources, ToolMessage):
                            response_content_for_feedback_sources = response_content_for_feedback_sources.content
                        elif isinstance(response_content_for_feedback_sources, list):
                            # For multimodal content, join text parts or convert to string
                            text_parts = [p["text"] for p in response_content_for_feedback_sources if p["type"] == "text"]
                            response_content_for_feedback_sources = " ".join(text_parts) if text_parts else str(response_content_for_feedback_sources)

                        display_feedback_form_for_sources(
                            user_question, response_content_for_feedback_sources, doc, source_unique_key
                        )
                else:
                    logger.error(f"Unexpected object in relevant_docs: {type(doc)}. Expected Document.")
                    st.markdown(f"**Source {j + 1}: [Content not available - unexpected format]**")

        # Add feedback form for assistant messages in chat history
        if (
            message.type == "assistant" and i > 1 # Access type attribute directly
        ):  # Skip system message and ensure there's a preceding user message
            user_message = "N/A"  # Default
            if i > 0 and st.session_state.messages[i - 1].type == "human": # Access type attribute directly
                user_message = st.session_state.messages[i - 1].content # Access content attribute directly
            
            # Ensure response_content is always a string for feedback form
            response_content_for_feedback = message.content # Access content attribute directly
            if isinstance(response_content_for_feedback, ToolMessage):
                response_content_for_feedback = response_content_for_feedback.content
            elif isinstance(response_content_for_feedback, list):
                # For multimodal content, join text parts or convert to string
                text_parts = [p["text"] for p in response_content_for_feedback if p["type"] == "text"]
                response_content_for_feedback = " ".join(text_parts) if text_parts else str(response_content_for_feedback)

            # Robust hashing for unique_key
            content_to_hash = response_content_for_feedback # Use the potentially converted string
            unique_key = f"history_{i}_{hash(content_to_hash) % 10000}"
            display_feedback_form(user_message, response_content_for_feedback, unique_key)

# Image upload widget
uploaded_files = st.file_uploader(
    "Upload images (optional)",
    type=["png", "jpg", "jpeg", "gif", "webp"],
    accept_multiple_files=True,
    key="image_uploader",
)

if prompt := st.chat_input("What is up?"):
    # Log the user's raw input
    logger.info(
        f"User input received: '{prompt}', Images: {len(uploaded_files) if uploaded_files else 0}"
    )

    # Create multimodal message content
    message_content_parts = []

    # Add text content
    if prompt:
        message_content_parts.append({"type": "text", "text": prompt})

    # Add image content
    if uploaded_files:
        for uploaded_file in uploaded_files:
            import base64

            # Read and encode image
            image_bytes = uploaded_file.read()
            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            # Determine MIME type
            mime_type = f"image/{uploaded_file.type.split('/')[-1]}"

            message_content_parts.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime_type,
                        "data": base64_image,
                    },
                }
            )
            logger.info(f"Added image to message: {uploaded_file.name}")

    # Store message with multimodal content using HumanMessage
    user_message = HumanMessage(
        content=message_content_parts
        if len(message_content_parts) > 1
        else prompt,
        additional_kwargs={
            "images": uploaded_files if uploaded_files else None
        }, # Store images in additional_kwargs
    )
    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        if isinstance(user_message.content, str):
            st.markdown(user_message.content)
        elif isinstance(user_message.content, list):
            for part in user_message.content:
                if part["type"] == "text":
                    st.markdown(part["text"])
        # Display uploaded images from additional_kwargs
        if "images" in user_message.additional_kwargs and user_message.additional_kwargs["images"]:
            for uploaded_file in user_message.additional_kwargs["images"]:
                st.image(uploaded_file, caption=uploaded_file.name, width=300)

    with st.chat_message("assistant"):
        with st.spinner(text="Searching documentation..."):
            
            # Use all messages as BaseMessage objects for the initial LLM call
            messages_for_llm_first_pass = [m for m in st.session_state.messages]
            logger.debug(f"Messages for LLM (first pass): {messages_for_llm_first_pass}")

        with st.spinner(text="Generating response..."):
            placeholder = st.empty()
            full_ai_response_text = ""
            full_ai_tool_calls = []
            relevant_docs = []

            try:
                # First pass: Get response potentially with tool calls
                for chunk in llm.stream(messages_for_llm_first_pass, tools=[retrieve_context_tool], tool_choice="auto"):
                    if chunk.text:
                        full_ai_response_text += chunk.text()
                        placeholder.markdown(full_ai_response_text)
                    if hasattr(chunk, "tool_calls") and chunk.tool_calls:
                        full_ai_tool_calls.extend(chunk.tool_calls)
                        # Break if tool calls are detected, as the LLM is waiting for tool output
                        break 
                
                # Construct the AI message (even if incomplete, with tool calls) and append to history
                ai_message_from_first_pass = AIMessage(
                    content=full_ai_response_text, 
                    tool_calls=full_ai_tool_calls if full_ai_tool_calls else None
                )
                st.session_state.messages.append(ai_message_from_first_pass)

                # If tool calls were made in the first pass, execute them and send results back to LLM
                if full_ai_tool_calls:
                    tool_messages = []
                    for tool_call in full_ai_tool_calls:
                        if tool_call["name"] == "retrieve_context_tool":
                            tool_output_dict = retrieve_context_tool(**tool_call["args"])
                            # We'll put the context string as content for the ToolMessage
                            tool_message_content = tool_output_dict.get("context", "No context found.")
                            
                            # Construct Bedrock-specific toolResult structure within a HumanMessage
                            tool_messages.append(HumanMessage(
                                content=[
                                    {"toolResult": {
                                        "toolUseId": tool_call["id"],
                                        "content": [{"text": tool_message_content}]
                                    }}
                                ]
                            ))
                            relevant_docs.extend([Document(page_content=d['page_content'], metadata=d['metadata']) for d in tool_output_dict.get("relevant_docs", [])])
                        else:
                            # Handle unknown tool or other tools if they were added
                            tool_messages.append(HumanMessage(
                                content=[
                                    {"toolResult": {
                                        "toolUseId": tool_call["id"],
                                        "content": [{"text": "Error: Unknown tool or unsupported tool execution."}]
                                    }}
                                ]
                            ))
                    
                    # Append the tool messages to session state (which now includes the AIMessage with tool_calls)
                    st.session_state.messages.extend(tool_messages)
                    
                    # Now, make the second LLM call to get the final answer, including streaming it
                    logger.info("Re-invoking LLM with tool results.")
                    # Use the updated session state messages for the second pass
                    messages_for_llm_second_pass = [m for m in st.session_state.messages] 

                    # Clear placeholder for fresh streaming from second pass
                    placeholder = st.empty() 
                    final_response_text = ""

                    for chunk in llm.stream(messages_for_llm_second_pass, tools=[retrieve_context_tool], tool_choice="auto"):
                        if chunk.text:
                            final_response_text += chunk.text()
                            placeholder.markdown(final_response_text)
                        # No more tool calls expected in this simple two-pass
                        # If more tool calls were to be handled, this would become recursive.

                    response = final_response_text # Final response is from the second pass
                else:
                    response = full_ai_response_text # If no tool calls, response is just first pass text

                logger.info(
                    f"Full LLM response received (length: {len(response)}): '{response}...'"
                )
                placeholder.markdown(response)
            except Exception as e_stream:
                logger.error(f"Error during LLM stream: {e_stream}", exc_info=True)
                response = "Sorry, I encountered an error while generating the response."  # Fallback response
                placeholder.error(response)

            # Add disclaimer
            st.markdown(
                "\n\n* *Generative AI is experimental. Please use the inline citation links or the source text below to verify answers.*"
            )

            # Display the sources used to answer the questions
            if relevant_docs:
                st.markdown("---")
                st.markdown("**Sources**")
                for i_doc, doc in enumerate(relevant_docs):
                    with st.expander(f"🔍 Source {i_doc + 1}"):
                        st.text(doc.page_content)
                        source_unique_key = f"{len(st.session_state.messages)}_source_{i_doc}_{hash(doc.page_content) % 10000}"
                        user_question_for_sources_feedback = user_message.content if isinstance(user_message.content, str) else str(user_message.content) # Ensure string
                        response_content_for_feedback_sources = response if isinstance(response, str) else str(response) # Ensure string
                        display_feedback_form_for_sources(
                            user_question_for_sources_feedback, response_content_for_feedback_sources, doc, source_unique_key
                        )

            # Display feedback form for this response
            unique_key = f"{len(st.session_state.messages)}_{hash(response) % 10000}"
            user_question_for_feedback = user_message.content if isinstance(user_message.content, str) else str(user_message.content) # Ensure string
            display_feedback_form(user_question_for_feedback, response, unique_key)

    # Log the assistant message being added to session state
    logger.info("Adding assistant response to session state.")
    # update memory
    st.session_state.messages.append(
        AIMessage(content=response, additional_kwargs={"sources": relevant_docs})
    )
