import json
import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Constants for chunking
MAX_TOKENS = 500
OVERLAP_PERCENTAGE = 0.1
MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"


def estimate_tokens(text):
    """
    Rough estimation of tokens (approximation: 1 token ≈ 4 characters)
    """
    return len(text) // 4


def chunk_text(text, max_tokens=MAX_TOKENS, overlap_percentage=OVERLAP_PERCENTAGE):
    """
    Chunk text based on token estimation with specified max tokens and overlap
    """
    if not text:
        return []

    # Split text into words for better chunking
    words = text.split()
    if not words:
        return []

    chunks = []
    current_chunk = []
    current_tokens = 0

    # Calculate overlap in tokens
    overlap_tokens = int(max_tokens * overlap_percentage)

    i = 0
    while i < len(words):
        word = words[i]
        word_tokens = estimate_tokens(word + " ")

        # If adding this word would exceed max tokens, finalize current chunk
        if current_tokens + word_tokens > max_tokens and current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(chunk_text)

            # Start new chunk with overlap
            if overlap_tokens > 0:
                # Keep last part of current chunk for overlap
                overlap_words = []
                overlap_token_count = 0

                # Work backwards from end of current chunk
                for j in range(len(current_chunk) - 1, -1, -1):
                    word_tokens_overlap = estimate_tokens(current_chunk[j] + " ")
                    if overlap_token_count + word_tokens_overlap <= overlap_tokens:
                        overlap_words.insert(0, current_chunk[j])
                        overlap_token_count += word_tokens_overlap
                    else:
                        break

                current_chunk = overlap_words
                current_tokens = overlap_token_count
            else:
                current_chunk = []
                current_tokens = 0

        # Add current word to chunk
        current_chunk.append(word)
        current_tokens += word_tokens
        i += 1

    # Add final chunk if there are remaining words
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append(chunk_text)

    return chunks


def write_output_to_s3(s3_client, bucket_name, file_name, json_data):
    """
    Write JSON data to S3 bucket
    """
    json_string = json.dumps(json_data)
    response = s3_client.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=json_string,
        ContentType="application/json",
    )

    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise Exception(f"Failed to upload {file_name} to {bucket_name}")

    print(f"Successfully uploaded {file_name} to {bucket_name}")
    return True


def read_from_s3(s3_client, bucket_name, file_name):
    """
    Read JSON data from S3 bucket
    """
    response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
    return json.loads(response["Body"].read().decode("utf-8"))


def parse_s3_path(s3_path):
    """
    Parse S3 path into bucket and key
    """
    s3_path = s3_path.replace("s3://", "")
    parts = s3_path.split("/", 1)
    if len(parts) != 2:
        raise ValueError("Invalid S3 path format")
    return parts[0], parts[1]


def invoke_model_with_response_stream(bedrock_runtime, prompt, max_tokens=1000):
    """
    Invoke Bedrock model with streaming response using the correct model format
    """
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }

    response = bedrock_runtime.invoke_model_with_response_stream(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(request_body),
    )

    response_text = ""
    for event in response.get("body"):
        chunk = json.loads(event["chunk"]["bytes"].decode())
        if chunk["type"] == "content_block_delta":
            response_text += chunk["delta"]["text"]
        elif chunk["type"] == "message_delta":
            if "stop_reason" in chunk["delta"]:
                break

    result = response_text.strip()
    if not result:
        raise Exception("Model returned empty response")

    return result


def invoke_model_sync(bedrock_runtime, prompt, max_tokens=100):
    """
    Invoke Bedrock model synchronously (non-streaming) for more reliable results
    """
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }

    response = bedrock_runtime.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(request_body),
    )

    response_body = json.loads(response["body"].read())
    content = response_body.get("content", [])

    if not content or len(content) == 0:
        raise Exception("Model returned no content")

    result = content[0].get("text", "").strip()
    if not result:
        raise Exception("Model returned empty text")

    return result


# Define the contextual retrieval prompt
contextual_retrieval_prompt = """
    <document>
    {doc_content}
    </document>

    Here is the chunk we want to situate within the whole document
    <chunk>
    {chunk_content}
    </chunk>

    Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
    Answer only with the succinct context and nothing else.
    """


def lambda_handler(event, context):
    """
    Lambda handler function for Bedrock Knowledge Base custom chunking
    """
    logger.info("Starting contextual retrieval processing")
    logger.debug(f"Input event: {json.dumps(event, default=str)}")

    s3_client = boto3.client("s3")
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime", region_name="us-east-1"
    )

    input_files = event.get("inputFiles")
    input_bucket = event.get("bucketName")

    if not all([input_files, input_bucket]):
        raise ValueError("Missing required input parameters")

    output_files = []

    for input_file in input_files:
        processed_batches = []
        content_batches = input_file.get("contentBatches", [])

        for batch in content_batches:
            input_key = batch.get("key")
            if not input_key:
                raise ValueError("Missing key in content batch")

            logger.info(f"Processing batch: {input_key}")

            # Read file content from S3
            file_content = read_from_s3(
                s3_client, bucket_name=input_bucket, file_name=input_key
            )
            if not file_content:
                raise Exception(f"Failed to read file content for {input_key}")

            # Get original document content for context
            original_document_content = "".join(
                content.get("contentBody", "")
                for content in file_content.get("fileContents", [])
                if content
            )

            if not original_document_content.strip():
                raise Exception("Document content is empty")

            # Limit document size for LLM context
            if len(original_document_content) > 8000:
                original_document_content = original_document_content[:8000] + "..."

            chunked_content = {"fileContents": []}

            for content in file_content.get("fileContents", []):
                content_body = content.get("contentBody", "")
                content_type = content.get("contentType", "text/plain")
                content_metadata = content.get("contentMetadata", {})

                if not content_body.strip():
                    continue

                # Apply chunking strategy
                chunks = chunk_text(content_body)
                logger.info(f"Created {len(chunks)} chunks from content")

                for i, chunk in enumerate(chunks):
                    if not chunk.strip():
                        raise Exception(f"Empty chunk generated at index {i}")

                    # Generate context for this chunk
                    prompt = contextual_retrieval_prompt.format(
                        doc_content=original_document_content, chunk_content=chunk
                    )

                    # Use synchronous model invocation
                    chunk_context = invoke_model_sync(
                        bedrock_runtime, prompt, max_tokens=100
                    )

                    # Ensure we have valid context
                    if not chunk_context or not chunk_context.strip():
                        raise Exception(f"Failed to generate context for chunk {i}")

                    # Combine context with original chunk
                    enhanced_content = f"{chunk_context}: {chunk}"

                    chunked_content["fileContents"].append(
                        {
                            "contentBody": enhanced_content,
                            "contentType": content_type,
                            "contentMetadata": {
                                **content_metadata,
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                                "estimated_tokens": estimate_tokens(chunk),
                                "has_context": True,
                                "context_length": len(chunk_context),
                            },
                        }
                    )

            # Write processed content back to S3
            output_key = f"Output/{input_key}"
            write_output_to_s3(s3_client, input_bucket, output_key, chunked_content)
            processed_batches.append({"key": output_key})
            logger.info(
                f"Successfully processed {len(chunked_content['fileContents'])} chunks for {input_key}"
            )

        output_files.append(
            {
                "originalFileLocation": input_file.get("originalFileLocation"),
                "fileMetadata": input_file.get("fileMetadata", {}),
                "contentBatches": processed_batches,
            }
        )

    logger.info(f"Processing completed. Generated {len(output_files)} output files")
    return {"outputFiles": output_files}
