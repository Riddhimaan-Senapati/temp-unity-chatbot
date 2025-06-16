import os
import streamlit as st
from dotenv import load_dotenv

from chatbot_helper import (
    initialize_bedrock_client,
    initialize_knowledge_base_retriever,
    initialize_llm,
    main_system_prompt,
    question_system_prompt,
    retrieve_context,
)
from feedback import display_feedback_form

# load the environment variables
load_dotenv()

st.title("Unity Chatbot")

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
                st.success("Logged in successfully!")
                st.rerun()  # rerun to display the app content
            else:
                st.error("Incorrect username or password.")
    st.stop()  # Stop execution if not logged in

# If we reach here, the user is logged in
st.sidebar.button(
    "Logout", on_click=lambda: st.session_state.update(logged_in=False, messages=[])
)


# Initialize Bedrock client
bedrock_client = initialize_bedrock_client()

# Initialize ChatBedrockConverse LLM
llm = initialize_llm(client=bedrock_client)

# Initialize the Knowledge Base retriever
retriever = initialize_knowledge_base_retriever()

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add the system prompt to the beginning of the messages
    st.session_state.messages.append({"role": "system", "content": main_system_prompt})

# store messages for short-term memory
# displays all messages, except the first one which is a system prompt
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Add feedback form for assistant messages in chat history
        if message["role"] == "assistant" and i > 1:  # Skip system message and ensure there's a preceding user message
            # Find the corresponding user message (should be the previous one)
            user_message = st.session_state.messages[i-1]["content"] if i > 0 else "Unknown question"
            unique_key = f"history_{i}_{hash(message['content']) % 10000}"
            display_feedback_form(user_message, message["content"], [], unique_key)

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # First phase: Searching documentation
        with st.spinner(text="Searching documentation..."):
            # First, generate an optimized search query using conversation history
            query_messages = [
                {"role": "system", "content": question_system_prompt},
                *[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[1:-1]
                ],  # All messages except the current one and the main_system_prompt
                {
                    "role": "user",
                    "content": f"Based on this conversation history, generate a search query for: {prompt}",
                },
            ]

            # Get the optimized query from the LLM
            query_response = llm.invoke(query_messages)
            optimized_query = query_response.content.strip()

            # Retrieve the relevant context and docs using the retriever and optimized query
            context, relevant_docs = retrieve_context(
                retriever=retriever, prompt=optimized_query
            )

            # Augment user prompt with retrieved context
            augmented_user_prompt = f"Context: {context}\n\nQuestion: {prompt}"

            # Convert messages to LangChain format(all except the last one) using query_messages
            messages = query_messages
            messages[0] = {"role": "system", "content": main_system_prompt}
            messages[-1] = {"role": "user", "content": augmented_user_prompt}

        # Second phase: Generating response
        with st.spinner(text="Generating response..."):
            # Get response from Bedrock using streaming
            # the response variable keeps track of the streamed response
            response = ""

            # this will alow our streaming response to be displayed as it arrives in "chunks"
            placeholder = st.empty()

            # chunk is part of a response received from LLM
            for chunk in llm.stream(messages):
                # add the text of it to our response
                response += chunk.text()
                # display the current response as plain text for now
                placeholder.text(response)

            # render the entire response in markdown since .markdown adds a line
            # after every time it is called. Hence, why we used placeholder.text above
            placeholder.markdown(response)            # Display the sources used to answer the questions
            if relevant_docs:
                st.markdown("---")
                st.markdown("**Sources**")
                for i, doc in enumerate(relevant_docs):
                    with st.expander(f"Source {i + 1}"):
                        st.markdown(doc.page_content)

            # Display feedback form for this response
            unique_key = f"{len(st.session_state.messages)}_{hash(response) % 10000}"
            display_feedback_form(prompt, response, relevant_docs if relevant_docs else [], unique_key)

    # update memory
    st.session_state.messages.append({"role": "assistant", "content": response})
