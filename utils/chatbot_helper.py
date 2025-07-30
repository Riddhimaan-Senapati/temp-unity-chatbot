import os

import boto3
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever

from utils.data_pipeline.link_cleaner import clean_s3_link

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


def initialize_llm(client, model_id=(os.getenv("MODEL_ID"))):
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
