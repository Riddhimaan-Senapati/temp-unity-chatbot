import json
import boto3
import logging
import urllib.parse
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"
MAX_CONTENT_LENGTH = 8000  # Limit content length for LLM processing


def invoke_model_sync(bedrock_runtime, prompt, max_tokens=200):
    """
    Invoke Bedrock model synchronously to generate metadata
    """
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }

    try:
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

    except Exception as e:
        logger.error(f"Error invoking Bedrock model: {str(e)}")
        raise


def extract_content_from_file(s3_client, bucket_name, key):
    """
    Extract content from various file types in S3
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)

        # Get file extension to determine content type
        file_extension = key.lower().split(".")[-1] if "." in key else ""

        if file_extension in ["txt", "md", "markdown"]:
            # Plain text files
            content = response["Body"].read().decode("utf-8")
        elif file_extension == "json":
            # JSON files - extract text content
            json_content = json.loads(response["Body"].read().decode("utf-8"))
            content = json.dumps(json_content, indent=2)
        else:
            # For other file types, try to read as text
            try:
                content = response["Body"].read().decode("utf-8")
            except UnicodeDecodeError:
                logger.warning(
                    f"Could not decode file {key} as UTF-8, treating as binary"
                )
                return None

        # Limit content length for LLM processing
        if len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH] + "..."

        return content

    except Exception as e:
        logger.error(f"Error reading file {key}: {str(e)}")
        return None


def generate_metadata_prompt(file_key, file_content):
    """
    Generate a prompt for the LLM to create metadata attributes
    """
    prompt = f"""
Analyze the following document and generate metadata attributes in JSON format.

File name: {file_key}

Document content:
{file_content}

Please generate metadata attributes that include:
1. "context" - A short category or topic tag (e.g., "Documentation", "Tutorial", "API", "Guide", "About", "Contact", etc.)
2. "summary" - A brief 1-2 sentence summary of the document's content
3. "content_type" - The type of content (e.g., "documentation", "tutorial", "reference", "guide", "contact_info", etc.)
4. "topics" - An array of relevant topics(always one word) or keywords found in the document always keep less than 5 topics

Respond with ONLY a valid JSON object in this exact format:
{{
    "context": "string",
    "summary": "string",
    "content_type": "string", 
    "topics": ["string1", "string2"]
}}

Do not include any additional text or explanation, only the JSON object.
"""
    return prompt


def parse_llm_response(response_text):
    """
    Parse the LLM response and extract JSON metadata
    """
    try:
        # Try to find JSON in the response
        response_text = response_text.strip()

        # If response starts with ```json, extract the JSON block
        if response_text.startswith("```json"):
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != 0:
                json_text = response_text[start:end]
            else:
                json_text = response_text
        else:
            json_text = response_text

        # Parse the JSON
        metadata_attrs = json.loads(json_text)

        # Validate required fields
        required_fields = ["tag", "summary"]
        for field in required_fields:
            if field not in metadata_attrs:
                logger.warning(f"Missing required field: {field}")

        return metadata_attrs

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
        logger.error(f"Response was: {response_text}")

        # Return default metadata if parsing fails
        return {
            "tag": "Document",
            "summary": "Auto-generated metadata for document processing.",
            "content_type": "document",
            "topics": [],
        }


def create_metadata_file(s3_client, bucket_name, original_key, metadata_attributes):
    """
    Create or update metadata JSON file to S3
    """
    try:
        # Create metadata file key
        metadata_key = f"{original_key}.metadata.json"

        # Check if metadata file already exists
        file_exists = False
        try:
            s3_client.head_object(Bucket=bucket_name, Key=metadata_key)
            file_exists = True
            logger.info(f"Updating existing metadata file: {metadata_key}")
        except Exception:
            logger.info(f"Creating new metadata file: {metadata_key}")

        # Create metadata structure
        metadata_content = {
            "metadataAttributes": metadata_attributes,
            "source_file": original_key,
        }

        # Upload metadata file to S3 (creates new or overwrites existing)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=metadata_key,
            Body=json.dumps(metadata_content, indent=2),
            ContentType="application/json",
            Metadata={
                "source-file": original_key,
                "content-type": "metadata",
                "last-updated": datetime.utcnow().isoformat(),
            },
        )

        action = "Updated" if file_exists else "Created"
        logger.info(f"Successfully {action.lower()} metadata file: {metadata_key}")
        return metadata_key

    except Exception as e:
        logger.error(f"Error creating/updating metadata file: {str(e)}")
        raise


def should_process_file(key):
    """
    Determine if a file should be processed for metadata generation
    """
    # Skip if it's already a metadata file
    if key.endswith(".metadata.json"):
        return False

    # Skip system files and folders
    skip_patterns = ["__pycache__", ".git", ".vscode", "thumbs.db", ".ds_store"]

    key_lower = key.lower()
    for pattern in skip_patterns:
        if pattern in key_lower:
            return False

    # Only process files with content (not empty folders)
    if key.endswith("/"):
        return False

    # Process text-based files
    processable_extensions = [".md"]

    file_extension = "." + key.split(".")[-1] if "." in key else ""
    return file_extension.lower() in processable_extensions


def lambda_handler(event, context):
    """
    Lambda handler function triggered by S3 events
    """
    logger.info("Starting metadata filtering processing")
    logger.debug(f"Input event: {json.dumps(event, default=str)}")

    s3_client = boto3.client("s3")
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime", region_name="us-east-1"
    )

    processed_files = []

    try:
        # Process S3 event records
        for record in event.get("Records", []):
            # Parse S3 event
            bucket_name = record["s3"]["bucket"]["name"]
            key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
            event_name = record["eventName"]

            logger.info(
                f"Processing {event_name} event for {key} in bucket {bucket_name}"
            )

            # Only process object creation events
            if not event_name.startswith("ObjectCreated"):
                logger.info(f"Skipping non-creation event: {event_name}")
                continue

            # Check if file should be processed
            if not should_process_file(key):
                logger.info(f"Skipping file: {key} (not eligible for processing)")
                continue

            # Always process files - will create or update metadata files
            metadata_key = f"{key}.metadata.json"
            logger.info(
                f"Processing {key} - will create/update metadata file: {metadata_key}"
            )

            # Extract content from the file
            file_content = extract_content_from_file(s3_client, bucket_name, key)
            if not file_content:
                logger.warning(f"Could not extract content from {key}")
                continue

            # Generate metadata using LLM
            prompt = generate_metadata_prompt(key, file_content)

            try:
                llm_response = invoke_model_sync(
                    bedrock_runtime, prompt, max_tokens=300
                )
                metadata_attributes = parse_llm_response(llm_response)

                # Create and upload metadata file
                metadata_file_key = create_metadata_file(
                    s3_client, bucket_name, key, metadata_attributes
                )

                processed_files.append(
                    {
                        "source_file": key,
                        "metadata_file": metadata_file_key,
                        "metadata_attributes": metadata_attributes,
                    }
                )

                logger.info(f"Successfully processed {key}")

            except Exception as e:
                logger.error(f"Error processing {key}: {str(e)}")
                # Continue processing other files even if one fails
                continue

    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        raise

    logger.info(f"Processing completed. Processed {len(processed_files)} files")

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": f"Successfully processed {len(processed_files)} files",
                "processed_files": processed_files,
            },
            default=str,
        ),
    }
