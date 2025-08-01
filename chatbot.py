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

from utils.prompts import main_system_prompt, question_system_prompt

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

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Log when initial system prompt is added to messages
    logger.info("Initializing chat messages with main system prompt.")
    # Add the system prompt to the beginning of the messages
    st.session_state.messages.append({"role": "system", "content": main_system_prompt})

# store messages for short-term memory
# displays all messages, except the first one which is a system prompt
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        # Display text content
        if isinstance(message["content"], str):
            st.markdown(message["content"])
        elif isinstance(message["content"], list):
            # Handle multimodal content
            for part in message["content"]:
                if part["type"] == "text":
                    st.markdown(part["text"])

        # Display images if they exist
        if message.get("images"):
            for img_file in message["images"]:
                st.image(img_file, caption=img_file.name, width=300)

        # Display sources if they exist in the message
        if (
            message["role"] == "assistant"
            and "sources" in message
            and message["sources"]
        ):
            st.markdown("---")
            st.markdown("**Sources**")
            for j, doc in enumerate(message["sources"]):
                with st.expander(f"🔍 Source {j + 1}"):
                    st.text(doc.page_content)
                    # Add source-specific feedback form
                    source_unique_key = f"{len(st.session_state.messages)}_source_{i}_{hash(doc.page_content) % 10000}"
                    # For historical messages, get the user question from the previous message
                    user_question = "N/A"  # Default
                    if i > 0 and st.session_state.messages[i - 1]["role"] == "user":
                        user_question = st.session_state.messages[i - 1]["content"]
                    display_feedback_form_for_sources(
                        user_question, message["content"], doc, source_unique_key
                    )

        # Add feedback form for assistant messages in chat history
        if (
            message["role"] == "assistant" and i > 1
        ):  # Skip system message and ensure there's a preceding user message
            user_message = "N/A"  # Default
            if i > 0 and st.session_state.messages[i - 1]["role"] == "user":
                user_message = st.session_state.messages[i - 1]["content"]
            unique_key = f"history_{i}_{hash(message['content']) % 10000}"
            display_feedback_form(user_message, message["content"], unique_key)

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

    # Store message with multimodal content
    st.session_state.messages.append(
        {
            "role": "user",
            "content": message_content_parts
            if len(message_content_parts) > 1
            else prompt,
            "images": uploaded_files if uploaded_files else None,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)
        # Display uploaded images
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.image(uploaded_file, caption=uploaded_file.name, width=300)

    with st.chat_message("assistant"):
        # First phase: Searching documentation
        with st.spinner(text="Searching documentation..."):
            # First, generate an optimized search query using conversation history
            query_messages = [
                {"role": "system", "content": question_system_prompt},
                *[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[
                        1:-1
                    ]  # History up to before current user prompt
                ],
                {
                    "role": "user",
                    "content": f"Based on this conversation history, generate a search query for: {prompt}",
                },
            ]
            # Log messages being sent for query optimization (can be verbose)
            logger.debug(f"Messages for query optimization LLM: {query_messages}")

            optimized_query = prompt  # Fallback
            try:
                # Get the optimized query from the LLM
                query_response = llm.invoke(query_messages)
                optimized_query_content = (
                    query_response.content.strip()
                    if hasattr(query_response, "content")
                    else str(query_response).strip()
                )
                if optimized_query_content:  # Use if not empty
                    optimized_query = optimized_query_content
                # Log the optimized query
                logger.info(f"Generated optimized query: '{optimized_query}'")
            except Exception as e_query_opt:
                logger.error(
                    f"Error during query optimization LLM call: {e_query_opt}",
                    exc_info=True,
                )
                logger.warning(
                    f"Falling back to original prompt '{prompt}' for retrieval due to query optimization error."
                )
                # optimized_query is already set to prompt as fallback

            # Log what query is being used for retrieval
            logger.info(f"Retrieving context with query: '{optimized_query}'")
            # Retrieve the relevant context and docs using the retriever and optimized query
            context, relevant_docs = retrieve_context(
                retriever=retriever, prompt=optimized_query
            )
            # Log a snippet of retrieved context or if no docs found
            if relevant_docs:
                logger.debug(
                    f"Retrieved {len(relevant_docs)} documents. Context snippet (first 100 chars): {str(context)[:100]}"
                )
            else:
                logger.info("No relevant documents found by retriever.")

            # Create multimodal message for LLM
            current_turn_content_parts = []

            # Add augmented text with context
            if prompt:
                augmented_text = f"Context:\n{context}\n\nQuestion: {prompt}"
                current_turn_content_parts.append(
                    {"type": "text", "text": augmented_text}
                )
            else:
                # If no text but has images
                augmented_text = f"Context:\n{context}\n\nUser question regarding the following image(s): Describe the image(s) and relate them to the provided context if possible."
                current_turn_content_parts.append(
                    {"type": "text", "text": augmented_text}
                )

            # Add images to current turn
            if uploaded_files:
                import base64

                for uploaded_file in uploaded_files:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    image_bytes = uploaded_file.read()
                    base64_image = base64.b64encode(image_bytes).decode("utf-8")
                    mime_type = f"image/{uploaded_file.type.split('/')[-1]}"

                    current_turn_content_parts.append(
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": base64_image,
                            },
                        }
                    )

            messages_for_main_llm = [{"role": "system", "content": main_system_prompt}]

            # Add historical messages
            for m in st.session_state.messages[1:-1]:
                if isinstance(m["content"], str):
                    messages_for_main_llm.append(
                        {"role": m["role"], "content": m["content"]}
                    )
                else:
                    # Handle multimodal historical messages
                    messages_for_main_llm.append(
                        {"role": m["role"], "content": m["content"]}
                    )

            # Add current multimodal turn
            messages_for_main_llm.append(
                {
                    "role": "user",
                    "content": current_turn_content_parts
                    if len(current_turn_content_parts) > 1
                    else current_turn_content_parts[0]["text"],
                }
            )
            # Log messages being sent to the main LLM (can be verbose)
            logger.info(f"Sending {len(messages_for_main_llm)} messages to main LLM.")
            logger.debug(f"Final messages for main LLM: {messages_for_main_llm}")

        # Second phase: Generating response
        with st.spinner(text="Generating response..."):
            # the response variable keeps track of the streamed response
            response = ""  # This will store the final concatenated response text

            # this will allow our streaming response to be displayed as it arrives in "chunks"
            placeholder = st.empty()

            try:
                # Log that streaming is starting
                logger.info("Starting to stream response from main LLM.")
                # chunk is part of a response received from LLM
                for chunk in llm.stream(messages_for_main_llm):
                    # add the text of it to our response
                    response += chunk.text()
                    placeholder.markdown(
                        response
                    )  # Display intermediate streaming text

                # Log the full final response from LLM
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
                        display_feedback_form_for_sources(
                            prompt, response, doc, source_unique_key
                        )

            # Display feedback form for this response
            unique_key = f"{len(st.session_state.messages)}_{hash(response) % 10000}"
            display_feedback_form(prompt, response, unique_key)

    # Log the assistant message being added to session state
    logger.info("Adding assistant response to session state.")
    # update memory
    st.session_state.messages.append(
        {"role": "assistant", "content": response, "sources": relevant_docs}
    )
