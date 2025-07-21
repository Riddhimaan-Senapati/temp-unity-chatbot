import os
import time

import boto3
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever

from utils.data_pipeline.link_cleaner import clean_s3_link

from utils.prompts import test_system_prompt

# Load environment variables
load_dotenv()


# --- Initialization Functions ---
def initialize_bedrock_client():
    """Initialize and return a Bedrock client using environment variables"""
    region = os.getenv("AWS_REGION", "us-east-1")
    print(f"Initializing Bedrock client in region: {region}")
    print(f"AWS_ACCESS_KEY_ID exists: {bool(os.getenv('AWS_ACCESS_KEY_ID'))}")

    # Lambda environment - always use IAM role
    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=region,
    )
    print("Bedrock client initialized successfully")
    return client


def initialize_llm(client, model_id="us.anthropic.claude-sonnet-4-20250514-v1:0"):
    """initialize ChatBedrockConverse LLM"""
    return ChatBedrockConverse(client=client, model_id=model_id)


def initialize_knowledge_base_retriever(source_count=10):
    """Initialize and return the Knowledge Base retriever"""
    return AmazonKnowledgeBasesRetriever(
        knowledge_base_id=os.getenv("KNOWLEDGE_BASE_ID"),
        retrieval_config={
            "vectorSearchConfiguration": {"numberOfResults": source_count}
        },
    )


def retrieve_context(retriever, prompt):
    # Retrieve relevant documents from Bedrock Knowledge Base
    relevant_docs = retriever.invoke(prompt)

    # Format the context with source information
    context = ""
    if relevant_docs:
        for i, doc in enumerate(relevant_docs):
            print(
                f"Source {i + 1} \n {doc.metadata.get('source_metadata', {}).get('x-amz-bedrock-kb-source-uri', 'unknown source')}"
            )
            source_uri = clean_s3_link(
                doc.metadata.get("source_metadata", {}).get(
                    "x-amz-bedrock-kb-source-uri", "unknown source"
                )
            )
            context += f"Source {i + 1} ({source_uri}):\n{doc.page_content}\n\n"
    else:
        context = "No relevant context found."

    # return both the context and the relevant docs
    return context, relevant_docs


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
    client, retriever, question, model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
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
    client, retriever, question, model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
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
    client, messages, model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
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
