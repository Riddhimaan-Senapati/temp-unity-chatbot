from langchain_aws import ChatBedrockConverse
import boto3
import os 
from dotenv import load_dotenv
from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever
from data_pipeline.link_cleaner import clean_s3_link
import json
import time

# Load environment variables
load_dotenv()

#Define the System prompt with example usage
system_prompt = (
    "You are a specialized helpful assistant for the Unity High Performance Computing (HPC) cluster. Your primary function is to answer questions based **solely** on the context provided in the user's message. "
    "You **must not** use any external knowledge, personal opinions, or information outside of this provided context.\n\n"

    "**Core Instructions:**\n"
    "1.  **Strictly Context-Bound:** Answer ONLY using the information present in the 'Context' section of the user's message. Do not infer or assume information not explicitly stated.\n"
    "2.  **Inline Citations:** When you answer using the context, cite the source(s) by including the source number in square brackets, like [[1]](https://example.com/), [[2]](https://example2.com/). Place citations next to the information they support.\n\n"

    "**How to Handle User Questions (Follow in this order):**\n\n"
    "**1. Specialized Redirections (Check First):**\n"
    "   a. **Unity News & Announcements:** If the user asks about 'latest news', 'announcements', 'updates', or similar regarding Unity, you **MUST** respond only with: 'For the latest news and announcements about Unity, please visit our official news page at https://docs.unity.rc.umass.edu/news/.'\n\n"
    "   b. **Unity Events:** If the user asks about 'events', 'workshops', 'conferences', or 'seminars' related to Unity, you **MUST** respond only with: 'For information on upcoming Unity events, workshops, and seminars, please visit https://docs.unity.rc.umass.edu/events .'\n\n"

    "**2. Answering from Provided Context:**\n"
    "If the query is not a special redirection, check if the provided context contains the answer.\n"
    "   - **If YES:** Provide the answer directly and include the citation(s) as specified above.\n\n"

    "**3. Handling Questions Not in Context:**\n"
    "If the answer is not in the provided context, determine if the question is related to Unity or HPC.\n"
    "   a. **Related to Unity/HPC, but Answer Not Found:** If the question is on-topic (about Unity, HPC, etc.) but the specific answer is NOT in the context, you **MUST** redirect the user by saying: 'I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].'\n\n"
    "   b. **Unrelated to Unity/HPC:** If the question is clearly off-topic (e.g., general knowledge, politics, the capital of Germany), you **MUST** refuse by responding ONLY with the exact phrase: 'I am sorry, but I can only assist with questions about Unity and High Performance Computing. Please ask a question related to these topics.'\n\n"

    "--- EXAMPLES ---\n\n"
    "**Example 1: Specialized Redirection (News)**\n"
    "Question: Are there any new software updates for Unity?\n"
    "Answer: For the latest news and announcements about Unity, please visit our official news page at example.com/news.\n\n"

    "**Example 2: Answerable from Context**\n"
    "Context: Source 1 (https://example.com/slurm): SLURM is the job scheduler used on Unity.\n"
    "Question: What job scheduler does Unity use?\n"
    "Answer: Unity uses the SLURM job scheduler [[1]](https://example.com/slurm).\n\n"

    "**Example 3: Related to Unity/HPC, but Answer Not Found**\n"
    "Context: Source 1 (https://example.com/storage): Users are allocated 100GB of home directory space.\n"
    "Question: What is the data transfer speed to the scratch storage?\n"
    "Answer: I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].\n\n"

    "**Example 4: Unrelated to Unity/HPC**\n"
    "Question: What is the tallest mountain in the world?\n"
    "Answer: I am sorry, but I can only assist with questions about Unity and High Performance Computing. Please ask a question related to these topics."
)

def initialize_bedrock_client():
    """Initialize and return a Bedrock client using environment variables"""
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN")
    )

def initialize_llm(client,model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"):
    """initialize ChatBedrockConverse LLM"""
    return ChatBedrockConverse(
        client=client,
        model_id=model_id
    )

def initialize_knowledge_base_retriever():
    """Initialize and return the Knowledge Base retriever"""
    return AmazonKnowledgeBasesRetriever(
        knowledge_base_id=os.getenv("KNOWLEDGE_BASE_ID"),
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 5}},
    )

def retrieve_context(retriever,prompt):
    # Retrieve relevant documents from Bedrock Knowledge Base
    relevant_docs = retriever.invoke(prompt)
    
    # Format the context with source information
    context = ""
    if relevant_docs:    
       for i, doc in enumerate(relevant_docs):
                    source_uri = clean_s3_link(doc.metadata.get("source_metadata", {}).get("x-amz-bedrock-kb-source-uri", "unknown source"))
                    context += f"Source {i+1} ({source_uri}):\n{doc.page_content}\n\n"
    else:
        context = "No relevant context found."
    
    # return both the context and the relevant docs
    return context, relevant_docs


# --- Testing Functions---

def testing_retrieve_context(retriever,question):
    # Retrieve relevant documents from Bedrock Knowledge Base
    relevant_docs = retriever.invoke(question)
    
    # Format the context with source information and collect the sources in the sources list
    context = ""
    sources = []
    if relevant_docs:
        for i, doc in enumerate(relevant_docs):
            source_uri = clean_s3_link(doc.metadata.get("source_metadata", {}).get("x-amz-bedrock-kb-source-uri", "unknown source"))
            context += f"Source {i+1} ({source_uri}):\n{doc.page_content}\n\n"
            sources.append({
                "source_number": i+1,
                "uri": source_uri,
                "content": doc.page_content
            })
    else:
        context = "No relevant context found."
    
    # return the context and sources
    return context, sources

def query_with_system_prompt(client, retriever, question, model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"):
    """Query Claude with system prompt and knowledge base context"""
    llm = initialize_llm(client=client, model_id=model_id)
    # Retrieve relevant context from Bedrock Knowledge Base along with the sources
    context, sources = testing_retrieve_context(retriever=retriever,question=question)
    
    # Augment user prompt with retrieved context
    augmented_user_prompt = f"Context: {context}\n\nQuestion: {question}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": augmented_user_prompt}
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
        metrics["tokens_per_second"] = round(metrics["output_tokens"] / response_time, 2) if response_time > 0 else 0
    
    return response.content, sources, metrics

def query_without_system_prompt(client, retriever, question, model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"):
    """Query Claude without system prompt but with knowledge base context"""
    llm = initialize_llm(client=client, model_id=model_id)
    
    # Retrieve relevant context from Bedrock Knowledge Base along with the sources
    context, sources = testing_retrieve_context(retriever=retriever,question=question)

    # Augment user prompt with retrieved context
    augmented_user_prompt = f"Context: {context}\n\nQuestion: {question}"
    
    messages = [
        {"role": "user", "content": augmented_user_prompt}
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
        metrics["tokens_per_second"] = round(metrics["output_tokens"] / response_time, 2) if response_time > 0 else 0
    
    return response.content, sources, metrics

def json_to_markdown(json_file):
    """Convert JSON results to readable Markdown format"""
    with open(json_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    markdown = "# Claude 3.7 Sonnet Comparison Results\n\n"
    
    for thread_name, thread_data in results.items():
        markdown += f"## Thread: {thread_name}\n\n"
        
        # With System Prompt section
        markdown += "### With System Prompt\n\n"
        for i, message in enumerate(thread_data["with_system_prompt"]["messages"]):
            markdown += f"**Q{i+1}: {message['question']}**\n\n"
            markdown += f"{message['answer']}\n\n"
            
            # Add performance metrics if available
            if "metrics" in message:
                markdown += "**Performance:**\n"
                markdown += f"- Response time: {message['metrics'].get('response_time_seconds', 'N/A')} seconds\n"
                if "input_tokens" in message["metrics"]:
                    markdown += f"- Input tokens: {message['metrics'].get('input_tokens', 'N/A')}\n"
                    markdown += f"- Output tokens: {message['metrics'].get('output_tokens', 'N/A')}\n"
                    markdown += f"- Total tokens: {message['metrics'].get('total_tokens', 'N/A')}\n"
                    markdown += f"- Tokens per second: {message['metrics'].get('tokens_per_second', 'N/A')}\n"
                markdown += "\n"
            
            # Add sources if available
            if thread_data["with_system_prompt"]["sources"][i]:
                markdown += "**Sources:**\n\n"
                for source in thread_data["with_system_prompt"]["sources"][i]:
                    markdown += f"- Source {source['source_number']}: [{source['uri']}]({source['uri']})\n"
                markdown += "\n"
        
        # Without System Prompt section
        markdown += "### Without System Prompt\n\n"
        for i, message in enumerate(thread_data["without_system_prompt"]["messages"]):
            markdown += f"**Q{i+1}: {message['question']}**\n\n"
            markdown += f"{message['answer']}\n\n"
            
            # Add performance metrics if available
            if "metrics" in message:
                markdown += "**Performance:**\n"
                markdown += f"- Response time: {message['metrics'].get('response_time_seconds', 'N/A')} seconds\n"
                if "input_tokens" in message["metrics"]:
                    markdown += f"- Input tokens: {message['metrics'].get('input_tokens', 'N/A')}\n"
                    markdown += f"- Output tokens: {message['metrics'].get('output_tokens', 'N/A')}\n"
                    markdown += f"- Total tokens: {message['metrics'].get('total_tokens', 'N/A')}\n"
                    markdown += f"- Tokens per second: {message['metrics'].get('tokens_per_second', 'N/A')}\n"
                markdown += "\n"
            
            # Add sources if available
            if thread_data["without_system_prompt"]["sources"][i]:
                markdown += "**Sources:**\n\n"
                for source in thread_data["without_system_prompt"]["sources"][i]:
                    markdown += f"- Source {source['source_number']}: [{source['uri']}]({source['uri']})\n"
                markdown += "\n"
        
        markdown += "---\n\n"
    
    # Write markdown to file with UTF-8 encoding
    md_file = os.path.join(os.path.dirname(json_file), json_file.replace('.json', '.md'))
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    return md_file