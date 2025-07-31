# filename: lambdas/documentation_scraper/lambda_function.py

import json
import logging
import os
import sys
from datetime import datetime
import boto3

# Add the project root to Python path for local development
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(
    os.path.dirname(current_dir)
)  # Go up two levels to project root
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add Lambda layer path for AWS execution
if "/opt/python" not in sys.path:
    sys.path.append("/opt/python")

# Import the scraping utilities
try:
    from utils.data_pipeline.scrape_and_upload_to_s3 import (
        run_scrape_and_upload_pipeline,
    )

    print("Successfully imported utils modules")
except ImportError as e:
    print(f"Import error: {e}")
    # For Lambda environment, try alternative import paths
    try:
        from scrape_and_upload_to_s3 import (
            run_scrape_and_upload_pipeline,
        )

        print("Successfully imported alternative modules")
    except ImportError as e2:
        print(f"Alternative import error: {e2}")
        print(f"Current sys.path: {sys.path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Lambda file location: {current_dir}")
        print(f"Project root: {project_root}")
        raise e2

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SNS client
sns_client = boto3.client("sns")


def send_notification(subject, message, is_error=False):
    """
    Send SNS notification about scraper execution.

    Args:
        subject: Email subject
        message: Email message body
        is_error: Whether this is an error notification
    """
    try:
        topic_arn = os.getenv("SNS_TOPIC_ARN")
        if not topic_arn:
            logger.warning("SNS_TOPIC_ARN not set, skipping notification")
            return

        # Add emoji and formatting based on success/error
        if is_error:
            formatted_subject = f"❌ {subject}"
            formatted_message = f"🚨 ERROR ALERT 🚨\n\n{message}"
        else:
            formatted_subject = f"✅ {subject}"
            formatted_message = f"🎉 SUCCESS 🎉\n\n{message}"

        response = sns_client.publish(
            TopicArn=topic_arn, Subject=formatted_subject, Message=formatted_message
        )

        logger.info(
            f"SNS notification sent successfully. MessageId: {response['MessageId']}"
        )

    except Exception as e:
        logger.error(f"Failed to send SNS notification: {str(e)}")


def lambda_handler(event, context):
    """
    AWS Lambda handler for scraping documentation websites.

    Args:
        event: Lambda event object containing trigger information
        context: Lambda context object

    Returns:
        dict: Response with status code and execution details
    """

    start_time = datetime.now()
    logger.info(f"Documentation scraper Lambda started at {start_time}")

    try:
        # Log the incoming event for debugging
        logger.info(f"Received event: {json.dumps(event, default=str)}")

        # Check if this is a scheduled event or manual trigger
        event_source = event.get("source", "manual")
        logger.info(f"Event source: {event_source}")

        # Extract any parameters from the event
        scrape_params = event.get("scrape_params", {})
        logger.info(f"scrape_params: {scrape_params}")

        # Log environment variables (without sensitive data)
        logger.info("Environment check:")
        logger.info(
            f"S3_BUCKET_NAME: {'SET' if os.getenv('S3_BUCKET_NAME') else 'NOT SET'}"
        )
        logger.info(f"S3_FOLDER_PREFIX: {os.getenv('S3_FOLDER_PREFIX', 'NOT SET')}")
        logger.info(
            f"SNS_TOPIC_ARN: {'SET' if os.getenv('SNS_TOPIC_ARN') else 'NOT SET'}"
        )

        # Validate required environment variables
        required_env_vars = ["S3_BUCKET_NAME"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]

        if missing_vars:
            error_msg = (
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            logger.error(error_msg)

            # Send configuration error notification
            config_error_message = f"""Unity Documentation Scraper configuration error!

⚙️ Configuration Issue:
• Missing Environment Variables: {", ".join(missing_vars)}
• Timestamp: {start_time.strftime("%Y-%m-%d %H:%M:%S UTC")}

🔧 Action Required: Please check the Lambda function configuration and ensure all required environment variables are set."""

            send_notification(
                "Unity Documentation Scraper - Configuration Error",
                config_error_message,
                is_error=True,
            )

            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "error": error_msg,
                        "timestamp": start_time.isoformat(),
                        "execution_time_seconds": 0,
                    }
                ),
            }

        # Run the scraping pipeline
        logger.info("Starting documentation scraping pipeline...")

        # Execute the main scraping function
        scraping_result = run_scrape_and_upload_pipeline()

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        logger.info(f"Scraping completed successfully in {execution_time:.2f} seconds")

        # Send success notification
        success_message = f"""Unity Documentation Scraper completed successfully!

📊 Execution Details:
• Start Time: {start_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
• End Time: {end_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
• Duration: {execution_time:.2f} seconds
• Event Source: {event_source}
• Result: {scraping_result if scraping_result else "Pipeline executed"}

🔗 Check CloudWatch logs for detailed information:
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Funity-documentation-scraper"""

        send_notification(
            "Unity Documentation Scraper - Success", success_message, is_error=False
        )

        # Prepare success response
        response_body = {
            "message": "Documentation scraping completed successfully",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "execution_time_seconds": execution_time,
            "event_source": event_source,
            "scraping_result": scraping_result
            if scraping_result
            else "Pipeline executed",
        }

        return {"statusCode": 200, "body": json.dumps(response_body, default=str)}

    except Exception as e:
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        error_msg = f"Error during documentation scraping: {str(e)}"
        logger.error(error_msg, exc_info=True)

        # Send error notification
        error_message = f"""Unity Documentation Scraper encountered an error!

❌ Error Details:
• Error: {str(e)}
• Start Time: {start_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
• End Time: {end_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
• Duration: {execution_time:.2f} seconds
• Event Source: {event.get("source", "manual")}

🔍 Please check CloudWatch logs for detailed error information:
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Funity-documentation-scraper

⚠️ Action Required: Please investigate and resolve the issue."""

        send_notification(
            "Unity Documentation Scraper - Error", error_message, is_error=True
        )

        # Prepare error response
        error_response = {
            "error": error_msg,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "execution_time_seconds": execution_time,
            "event_source": event.get("source", "manual"),
        }

        return {"statusCode": 500, "body": json.dumps(error_response, default=str)}


def test_handler():
    """
    Test function for local development and testing.
    """
    test_event = {"source": "test", "scrape_params": {}}

    class MockContext:
        def __init__(self):
            self.function_name = "documentation-scraper-test"
            self.function_version = "$LATEST"
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:documentation-scraper-test"
            self.memory_limit_in_mb = "512"
            self.remaining_time_in_millis = lambda: 300000

    context = MockContext()

    print("Testing documentation scraper Lambda function...")
    result = lambda_handler(test_event, context)
    print(f"Test result: {json.dumps(result, indent=2)}")
    return result


if __name__ == "__main__":
    # For local testing
    test_handler()
