import streamlit as st
import os 
from dotenv import load_dotenv
from chatbot_helper import (system_prompt, initialize_bedrock_client, initialize_knowledge_base_retriever, 
initialize_llm, retrieve_context)

#load the environment variables
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
                st.rerun()# rerun to display the app content 
            else:
                st.error("Incorrect username or password.")
    st.stop() # Stop execution if not logged in

# If we reach here, the user is logged in
st.sidebar.button("Logout", on_click=lambda: st.session_state.update(logged_in=False, messages=[]))


# Initialize Bedrock client
bedrock_client = initialize_bedrock_client()

# Initialize ChatBedrockConverse LLM
llm = initialize_llm(client=bedrock_client)

# Initialize the Knowledge Base retriever
retriever = initialize_knowledge_base_retriever()

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add the system prompt to the beginning of the messages
    st.session_state.messages.append({"role": "system", "content": system_prompt})

# store messages for short-term memory
# displays all messages, except the first one which is a system prompt
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        #Show thinking spinner while it's fetching a response from the LLM
        with st.spinner(text="Thinking..."):
            # Retrieve the relevant context and docs using the retriever and prompt
            context, relevant_docs = retrieve_context(retriever=retriever,prompt=prompt)
            
            # Augment user prompt with retrieved context
            augmented_user_prompt = f"Context: {context}\n\nQuestion: {prompt}"

            # Convert messages to LangChain format(all except the last one)
            messages = [
               {"role": m["role"], "content": m["content"]}
               for m in st.session_state.messages[:-1]
            ]

            # In place of the last message which is the current user prompt, pass in the augumented_user_prompt
            messages.append({"role":"user", "content": augmented_user_prompt})
        
            # Get response from Bedrock using streaming
            #the response variable keeps track of the streamed response 
            response=""

            #this will alow our streaming response to be displayed as it arrives in "chunks"
            placeholder = st.empty()

            #chunk is part of a response received from LLM
            for chunk in llm.stream(messages):
                #add the text of it to our response
                response+=chunk.text()
                #display the current response as plain text for now
                placeholder.text(response)

            #render the entire response in markdown since .markdown adds a line
            #after every time it is called. Hence, why we used placeholder.text above
            placeholder.markdown(response)

            # Display the sources used to answer the questions
            if relevant_docs:
                 st.markdown("---")
                 st.markdown("**Sources**")
                 for i,doc in enumerate(relevant_docs):
                    with st.expander(f"Source {i+1}"):
                        st.markdown(doc.page_content)

    #update memory
    st.session_state.messages.append({"role": "assistant", "content": response})