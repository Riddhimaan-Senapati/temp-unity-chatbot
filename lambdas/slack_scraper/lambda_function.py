# filename: lambdas/slack_scraper/lambda_function.py

import json
import logging
import os
import sys
import boto3
from datetime import datetime

# Add the project root to Python path for local development
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add Lambda layer path for AWS execution
if "/opt/python" not in sys.path:
    sys.path.append("/opt/python")

# Import the scraping utilities
try:
    from slack_scripts.slack_scraper import run_slack_conversation_scraper

    print("Successfully imported slack scraper module")
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current sys.path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    raise e

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
    AWS Lambda handler for scraping Slack conversations.

    Args:
        event: Lambda event object containing trigger information
        context: Lambda context object

    Returns:
        dict: Response with status code and execution details
    """

    start_time = datetime.now()
    logger.info(f"Slack scraper Lambda started at {start_time}")

    try:
        # Log the incoming event for debugging
        logger.info(f"Received event: {json.dumps(event, default=str)}")

        # Check if this is a scheduled event or manual trigger
        event_source = event.get("source", "manual")
        logger.info(f"Event source: {event_source}")

        # Extract any parameters from the event
        scrape_params = event.get("scrape_params", {})
        start_date = scrape_params.get("start_date")
        logger.info(f"scrape_params: {scrape_params}")

        # Log environment variables (without sensitive data)
        logger.info("Environment check:")
        logger.info(
            f"S3_BUCKET_NAME: {'SET' if os.getenv('S3_BUCKET_NAME') else 'NOT SET'}"
        )
        logger.info(
            f"SCRAPPER_SLACK_BOT_TOKEN: {'SET' if os.getenv('SCRAPPER_SLACK_BOT_TOKEN') else 'NOT SET'}"
        )
        logger.info(
            f"SNS_TOPIC_ARN: {'SET' if os.getenv('SNS_TOPIC_ARN') else 'NOT SET'}"
        )

        # Validate required environment variables
        required_env_vars = ["S3_BUCKET_NAME", "SCRAPPER_SLACK_BOT_TOKEN"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]

        if missing_vars:
            error_msg = (
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            logger.error(error_msg)

            # Send configuration error notification
            config_error_message = f"""Unity Slack Scraper configuration error!

⚙️ Configuration Issue:
• Missing Environment Variables: {", ".join(missing_vars)}
• Timestamp: {start_time.strftime("%Y-%m-%d %H:%M:%S UTC")}

🔧 Action Required: Please check the Lambda function configuration and ensure all required environment variables are set."""

            send_notification(
                "Unity Slack Scraper - Configuration Error",
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
        logger.info("Starting Slack conversation scraping pipeline...")

        # Execute the main scraping function
        scraping_result = run_slack_conversation_scraper(start_date)

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        if scraping_result["success"]:
            logger.info(
                f"Scraping completed successfully in {execution_time:.2f} seconds"
            )

            # Send success notification with metrics
            metrics = scraping_result.get("metrics", {})
            success_message = f"""Unity Slack Scraper completed successfully!

📊 Scraping Metrics:
• Total Conversations Found: {metrics.get("total_conversations", 0)}
• Conversations ≤10 Replies: {metrics.get("conversations_with_10_or_less_replies", 0)}
• Conversations Actually Scraped: {metrics.get("conversations_scraped", 0)}
• Conversations Skipped (>10 replies): {metrics.get("conversations_skipped", 0)}

📈 Execution Details:
• Start Time: {start_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
• End Time: {end_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
• Duration: {execution_time:.2f} seconds
• Event Source: {event_source}

🔗 Check CloudWatch logs for detailed information:
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Funity-slack-scraper"""

            send_notification(
                "Unity Slack Scraper - Success", success_message, is_error=False
            )

            # Prepare success response
            response_body = {
                "message": "Slack conversation scraping completed successfully",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": execution_time,
                "event_source": event_source,
                "metrics": metrics,
                "scraping_result": "Pipeline executed successfully",
            }

            return {"statusCode": 200, "body": json.dumps(response_body, default=str)}
        else:
            # Handle scraping failure
            error_msg = scraping_result.get("error", "Unknown error occurred")
            logger.error(f"Scraping failed: {error_msg}")

            # Send error notification
            error_message = f"""Unity Slack Scraper encountered an error!

❌ Error Details:
• Error: {error_msg}
• Start Time: {start_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
• End Time: {end_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
• Duration: {execution_time:.2f} seconds
• Event Source: {event_source}

🔍 Please check CloudWatch logs for detailed error information:
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Funity-slack-scraper

⚠️ Action Required: Please investigate and resolve the issue."""

            send_notification(
                "Unity Slack Scraper - Error", error_message, is_error=True
            )

            return {
                "statusCode": 500,
                "body": json.dumps(
                    {
                        "error": error_msg,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "execution_time_seconds": execution_time,
                        "event_source": event_source,
                        "metrics": scraping_result.get("metrics", {}),
                    },
                    default=str,
                ),
            }

    except Exception as e:
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        error_msg = f"Error during Slack conversation scraping: {str(e)}"
        logger.error(error_msg, exc_info=True)

        # Send error notification
        error_message = f"""Unity Slack Scraper encountered an error!

❌ Error Details:
• Error: {str(e)}
• Start Time: {start_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
• End Time: {end_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
• Duration: {execution_time:.2f} seconds
• Event Source: {event.get("source", "manual")}

🔍 Please check CloudWatch logs for detailed error information:
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Funity-slack-scraper

⚠️ Action Required: Please investigate and resolve the issue."""

        send_notification("Unity Slack Scraper - Error", error_message, is_error=True)

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
    test_event = {"source": "test", "scrape_params": {"start_date": "2025-01-01"}}

    class MockContext:
        def __init__(self):
            self.function_name = "slack-scraper-test"
            self.function_version = "$LATEST"
            self.invoked_function_arn = (
                "arn:aws:lambda:us-east-1:123456789012:function:slack-scraper-test"
            )
            self.memory_limit_in_mb = "512"
            self.remaining_time_in_millis = lambda: 300000

    context = MockContext()

    print("Testing Slack scraper Lambda function...")
    result = lambda_handler(test_event, context)
    print(f"Test result: {json.dumps(result, indent=2)}")
    return result


if __name__ == "__main__":
    # For local testing
    test_handler()
