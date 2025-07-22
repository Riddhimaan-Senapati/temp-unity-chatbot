# filename: lambdas/slack_scraper/lambda_function.py

import json
import logging
import os
import sys
from datetime import datetime, timedelta

# Add the project root to Python path for local development
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels to project root
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add Lambda layer path for AWS execution
if "/opt/python" not in sys.path:
    sys.path.append("/opt/python")

# Import the slack scraper functions
try:
    from slack_scripts.slack_scraper import main as slack_scraper_main
    print("Successfully imported slack_scraper module")
except ImportError as e:
    print(f"Import error: {e}")
    # For Lambda environment, try alternative import paths
    try:
        import slack_scraper
        from slack_scraper import main as slack_scraper_main
        print("Successfully imported alternative slack_scraper module")
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


def lambda_handler(event, context):
    """
    AWS Lambda handler for scraping Slack conversations from the last week.
    
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
        event_source = event.get('source', 'manual')
        logger.info(f"Event source: {event_source}")
        
        # Calculate the start date for last week's conversations
        # Default to scraping last 7 days of conversations
        days_back = event.get('days_back', 7)
        start_date = datetime.now() - timedelta(days=days_back)
        start_date_str = start_date.strftime('%Y-%m-%d')
        
        logger.info(f"Scraping Slack conversations from the last {days_back} days (since {start_date_str})")
        
        # Log environment variables (without sensitive data)
        logger.info("Environment check:")
        logger.info(f"S3_BUCKET_NAME: {'SET' if os.getenv('S3_BUCKET_NAME') else 'NOT SET'}")
        logger.info(f"SCRAPPER_SLACK_BOT_TOKEN: {'SET' if os.getenv('SCRAPPER_SLACK_BOT_TOKEN') else 'NOT SET'}")
        
        # Validate required environment variables
        required_env_vars = ['S3_BUCKET_NAME', 'SCRAPPER_SLACK_BOT_TOKEN']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': error_msg,
                    'timestamp': start_time.isoformat(),
                    'execution_time_seconds': 0
                })
            }
        
        # Run the Slack scraper
        logger.info(f"Starting Slack conversation scraping for date: {start_date_str}")
        
        # Execute the main scraping function with the calculated start date
        scraping_result = slack_scraper_main(start_date_str)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Slack scraping completed successfully in {execution_time:.2f} seconds")
        
        # Prepare success response
        response_body = {
            'message': 'Slack conversation scraping completed successfully',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'execution_time_seconds': execution_time,
            'event_source': event_source,
            'scrape_start_date': start_date_str,
            'days_scraped': days_back,
            'scraping_result': scraping_result if scraping_result else 'Scraping completed'
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(response_body, default=str)
        }
        
    except Exception as e:
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        error_msg = f"Error during Slack conversation scraping: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Prepare error response
        error_response = {
            'error': error_msg,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'execution_time_seconds': execution_time,
            'event_source': event.get('source', 'manual')
        }
        
        return {
            'statusCode': 500,
            'body': json.dumps(error_response, default=str)
        }


def test_handler():
    """
    Test function for local development and testing.
    """
    test_event = {
        'source': 'test',
        'days_back': 7  # Scrape last 7 days
    }
    
    class MockContext:
        def __init__(self):
            self.function_name = 'slack-scraper-test'
            self.function_version = '$LATEST'
            self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:slack-scraper-test'
            self.memory_limit_in_mb = '512'
            self.remaining_time_in_millis = lambda: 300000
    
    context = MockContext()
    
    print("Testing Slack scraper Lambda function...")
    print(f"Will scrape conversations from the last {test_event['days_back']} days")
    result = lambda_handler(test_event, context)
    print(f"Test result: {json.dumps(result, indent=2)}")
    return result


if __name__ == "__main__":
    # For local testing
    test_handler()