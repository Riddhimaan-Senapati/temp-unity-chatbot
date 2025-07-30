import time
from utils.chatbot_helper import initialize_llm
from utils.data_pipeline.link_cleaner import clean_s3_link

# Define the system prompt for testing purposes
test_system_prompt = """
You are a specialized helpful assistant for the Unity High Performance Computing (HPC) cluster. Your primary function is to answer questions based **solely** on the context provided in the user's message. You **must not** use any external knowledge, personal opinions, or information outside of this provided context.

**Core Instructions:**
1.  **Strictly Context-Bound:** Answer ONLY using the information present in the 'Context' section of the user's message. Do not infer or assume information not explicitly stated.
2.  **Inline Citations:** When you answer using the context, cite the source(s) by including the source number as a link. The format is `[[Source Number]](URL)`. Place citations next to the information they support.

**How to Handle User Questions (Follow in this order):**

**1. Specialized Redirections (Check First):**
   a. **Unity News & Announcements:** If the user asks about 'latest news', 'announcements', 'updates', or similar regarding Unity, you **MUST** respond only with: 'For the latest news and announcements about Unity, please visit our official news page at https://docs.unity.rc.umass.edu/news/.'

   b. **Unity Events:** If the user asks about 'events', 'workshops', 'conferences', or 'seminars' related to Unity, you **MUST** respond only with: 'For information on upcoming Unity events, workshops, and seminars, please visit https://docs.unity.rc.umass.edu/events .'

**2. Answering from Provided Context:**
If the query is not a special redirection, check if the provided context contains the answer.
   - **If YES:** Provide the answer directly and include the citation(s) with hover text as specified above.

**3. Handling Questions Not in Context:**
If the answer is not in the provided context, determine if the question is related to Unity or HPC.
   a. **Related to Unity/HPC, but Answer Not Found:** If the question is on-topic (about Unity, HPC, etc.) but the specific answer is NOT in the context, you should provide insights or troubleshooting steps using ONLY documentation and redirect the user by letting user know that the specific information is not available in the documents. And for further assistance, they can reach out to Unity's help desk at [hpc@umass.edu] or visit Unity's community page at [https://docs.unity.rc.umass.edu/contact/community/].

   b. **Unrelated to Unity/HPC:** If the question is clearly off-topic (e.g., general knowledge, politics, the capital of Germany), you **MUST** refuse by responding ONLY with the exact phrase: 'I am sorry, but I can only assist with questions about Unity and High Performance Computing. Please ask a question related to these topics.'

--- EXAMPLES ---

**Example 1: Specialized Redirection (News)**
Question: Are there any new software updates for Unity?
Answer: For the latest news and announcements about Unity, please visit our official news page at https://docs.unity.rc.umass.edu/news/.

**Example 2: Answerable from Context**
Context: Source 1 (https://example.com/slurm): SLURM is the job scheduler used on Unity.
Question: What job scheduler does Unity use?
Answer: Unity uses the SLURM job scheduler [[1]](https://example.com/slurm).

**Example 3: Related to Unity/HPC, but Answer Not Found**
Context: Source 1 (https://example.com/storage): Users are allocated 100GB of home directory space.
Question: What is the data transfer speed to the scratch storage?
Answer: I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

**Example 4: Unrelated to Unity/HPC**
Question: What is the tallest mountain in the world?
Answer: I am sorry, but I can only assist with questions about Unity and High Performance Computing. Please ask a question related to these topics.
"""

# --- Testing Functions---


def testing_retrieve_context(retriever, question):
    # Retrieve relevant documents from Bedrock Knowledge Base
    relevant_docs = retriever.invoke(question)

    # Format the context with source information and collect the sources in the sources list
    context = ""
    sources = []
    if relevant_docs:
        for i, doc in enumerate(relevant_docs):
            source_uri = clean_s3_link(
                doc.metadata.get("source_metadata", {}).get(
                    "x-amz-bedrock-kb-source-uri", "unknown source"
                )
            )
            context += f"Source {i + 1} ({source_uri}):\n{doc.page_content}\n\n"
            sources.append(
                {"source_number": i + 1, "uri": source_uri, "content": doc.page_content}
            )
    else:
        context = "No relevant context found."

    # return the context and sources
    return context, sources


def query_with_system_prompt(
    client, retriever, question, model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0"
):
    """Query Claude with system prompt and knowledge base context"""
    llm = initialize_llm(client=client, model_id=model_id)
    # Retrieve relevant context from Bedrock Knowledge Base along with the sources
    context, sources = testing_retrieve_context(retriever=retriever, question=question)

    # Augment user prompt with retrieved context
    augmented_user_prompt = f"Context: {context}\n\nQuestion: {question}"

    messages = [
        {"role": "system", "content": test_system_prompt},
        {"role": "user", "content": augmented_user_prompt},
    ]

    # Measure response time
    start_time = time.time()
    response = llm.invoke(messages)
    end_time = time.time()

    # Calculate metrics
    response_time = end_time - start_time

    # Get metrics from Bedrock client response
    metrics = {
        "response_time_seconds": round(response_time, 2),
    }

    # Extract token usage if available in response
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        metrics["input_tokens"] = response.usage_metadata.get("input_tokens", 0)
        metrics["output_tokens"] = response.usage_metadata.get("output_tokens", 0)
        metrics["total_tokens"] = response.usage_metadata.get("total_tokens", 0)
        metrics["tokens_per_second"] = (
            round(metrics["output_tokens"] / response_time, 2)
            if response_time > 0
            else 0
        )

    return response.content, sources, metrics


def query_without_system_prompt(
    client, retriever, question, model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0"
):
    """Query Claude without system prompt but with knowledge base context"""
    llm = initialize_llm(client=client, model_id=model_id)

    # Retrieve relevant context from Bedrock Knowledge Base along with the sources
    context, sources = testing_retrieve_context(retriever=retriever, question=question)

    # Augment user prompt with retrieved context
    augmented_user_prompt = f"Context: {context}\n\nQuestion: {question}"

    messages = [{"role": "user", "content": augmented_user_prompt}]

    # Measure response time
    start_time = time.time()
    response = llm.invoke(messages)
    end_time = time.time()

    # Calculate metrics
    response_time = end_time - start_time

    # Get metrics from Bedrock client response
    metrics = {
        "response_time_seconds": round(response_time, 2),
    }

    # Extract token usage if available in response
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        metrics["input_tokens"] = response.usage_metadata.get("input_tokens", 0)
        metrics["output_tokens"] = response.usage_metadata.get("output_tokens", 0)
        metrics["total_tokens"] = response.usage_metadata.get("total_tokens", 0)
        metrics["tokens_per_second"] = (
            round(metrics["output_tokens"] / response_time, 2)
            if response_time > 0
            else 0
        )

    return response.content, sources, metrics


def invoke_llm(
    client, messages, model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0"
):
    """Simple LLM invocation function without knowledge base retrieval"""
    llm = initialize_llm(client=client, model_id=model_id)

    # Measure response time
    start_time = time.time()
    response = llm.invoke(messages)
    end_time = time.time()

    # Calculate metrics
    response_time = end_time - start_time

    # Get metrics from Bedrock client response
    metrics = {
        "response_time_seconds": round(response_time, 2),
    }

    # Extract token usage if available in response
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        metrics["input_tokens"] = response.usage_metadata.get("input_tokens", 0)
        metrics["output_tokens"] = response.usage_metadata.get("output_tokens", 0)
        metrics["total_tokens"] = response.usage_metadata.get("total_tokens", 0)
        metrics["tokens_per_second"] = (
            round(metrics["output_tokens"] / response_time, 2)
            if response_time > 0
            else 0
        )

    return response.content, metrics
