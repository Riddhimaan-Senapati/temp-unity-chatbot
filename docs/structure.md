# 📂 Structure

```
├── README.md
├── .env.example
├── chatbot.py
├── requirements.txt
├── pages/
│ └── dashboard.py
├── qa_pairs/
│ └── slack_qa_generator.py
├── slack_scripts/
│ ├── slack_bot.py
│ ├── slack_scraper.py
├── utils/
│ ├── chatbot_helper.py
│ ├── slackbot_helper.py
│ ├── streamlit_components.py
│ ├── feedback.py
│ ├── prompts.py
| ├── qa_pair_tab.py
│ └── data_pipeline/
│     ├── scrape_and_upload_to_s3.py
│     ├── scrapping_helper.py
│     └── link_cleaner.py
├── docs/
│ ├── README-DEPLOYMENT.md
│ └── structure.md
├── local_testing/
│ ├── automated_test.py
│ ├── test_data/
│ │ └── conversation_threads.json
│ └── test_results/
│   └── (stores the test results)
├── images/
│ └── (stores images for use in the README and other documentation)
├── .github/
│ ├── pull_request_template.md
│ └── workflows/
│     ├── deploy-chatbot.yml
│     ├── deploy-slackbot-ecs.yml
│     ├── deploy-slack-lambda.yml
│     ├── deploy-documentation-scraper.yml
│     ├── deploy-slack-scraper.yml
│     └── deploy-slack-lambda-bot.yml
├── cloudformation-templates/
│ ├── cloudformation-template-chatbot.yml
│ ├── cloudformation-template-slackbot-ecs.yml
│ ├── documentation-scraper-lambda.yml
│ ├── slack-scraper-lambda.yml
│ └── slack-lambda-infrastructure.yml
├── Dockerfiles/
│ ├── chatbot_dockerfile
│ └── slackbot_dockerfile
├── lambdas/
│ └── contextual_retrieval/
│     └── lambda_function.py
│ └── metadata_filtering/
│     └── lambda_function.py
│ └── documentation_scraper/
│     ├── lambda_function.py
│     └── requirements.txt
│ └── slack_scraper/
│     ├── lambda_function.py
│     └── requirements.txt
│ └── slack_lambda/
│     ├── slack_lambda.py
│     └── requirements.txt
│ └── slack_lambda/
│     ├── slack_lambda.py
│     └── requirements.txt
├── .dockerignore
├── LICENSE
└── .gitignore
```

## 📄 File Descriptions

- **`README.md`**: The main documentation file for this project, providing an overview, setup instructions, and details about the codebase structure.
- **`pages/`**: This directory contains other pages for the streamlit app. This is how multi-page streamlit apps are made.
  - **`pages/dashboard.py`**: The Streamlit dashboard with five tabs: User Feedback Analytics, Data Pipeline Management (for tracking scraped documentation), Slack Conversations (for viewing and editing Slack channel conversations), Q&A Pair Review (for managing generated Q&A pairs from Slack channel conversations) and Add Knowledge (for adding specific information or Q&A pair manually to the knowledge base).
- **`utils/`**: This directory contains utility functions and helper modules used across the application.
  - **`utils/chatbot_helper.py`**: Contains modular functions and helper utilities used across the chatbot application, promoting code reusability and organization.
  - **`utils/slackbot_helper.py`**: Contains shared helper functions for Slack bot functionality, including conversation history reconstruction, image processing, query optimization, and multimodal message creation. Used by both the Socket Mode Slack bot and Lambda-based Slack bot to eliminate code duplication.
  - **`utils/streamlit_components.py`**: Contains reusable Streamlit UI components, including confirmation dialog functionality for user actions. Provides modular confirmation dialogs with customizable messages, warning levels, and button text for actions like scraping operations in the dashboard.
  - **`utils/prompts.py`**: Contains the system prompts used throughout the application, including specialized prompts for Slack interactions with followup question generation.
  - **`utils/feedback.py`**: Handles user feedback collection and analytics functionality for the chatbot interface.
  - **`utils/qa_pair_tab.py`**: The dashboard tab for the generated Q&A Pairs.
  - **`utils/data_pipeline/`**: This subdirectory contains scripts responsible for data ingestion and processing.
    - **`utils/data_pipeline/scrape_and_upload_to_s3.py`**: A script designed to scrape documentation content and upload it to an AWS S3 bucket.
    - **`utils/data_pipeline/scrapping_helper.py`**: Contains helper functions and utilities used by the scraping scripts within the data pipeline.
    - **`utils/data_pipeline/link_cleaner.py`**: A script for cleaning and normalizing URLs and links found during the scraping process. Used in the chatbot to clean URLs from S3 filenames for displaying to users.
- **`chatbot.py`**: The core Streamlit application that implements the Retrieval-Augmented Generation (RAG) chatbot functionality.
- **`qa_pairs/`**: This directory contains scripts for generating question-answer pairs from Slack conversations.
  - **`qa_pairs/slack_qa_generator.py`**: A script that converts Slack conversations from S3 markdown into structured question-answer pairs using LLM processing.
- **`slack_scripts/`**: This directory contains Slack-related functionality for Socket Mode deployment.

  - **`slack_scripts/slack_bot.py`**: The core Slack bot code that implements the Retrieval-Augmented Generation (RAG) chatbot functionality using the Slack Bolt library with Socket Mode for persistent connections. Designed for ECS deployment.
  - **`slack_scripts/slack_scraper.py`**: A script to scrape conversations from Slack channels and store them as markdown files in S3.

- **`docs/`**: This directory contains documentation files.
  - **`docs/README-DEPLOYMENT.md`**: Detailed instructions for deploying the application to AWS.
  - **`docs/structure.md`**: Detailed project structure and file descriptions.
- **`local_testing/`**: This directory contains all testing-related files and scripts for local development and validation.
  - **`local_testing/automated_test.py`**: Contains automated tests for the chatbot, ensuring its functionality and reliability.
  - **`local_testing/test_data/`**: This subdirectory contains test data used by automated testing scripts.
    - **`local_testing/test_data/conversation_threads.json`**: Contains conversation threads with sample questions used by automated_test.py for testing chatbot responses across different scenarios.
  - **`local_testing/test_results/`**: This subdirectory stores the results of automated tests, such as comparison outcomes for different models.
- **`images/`**: This directory stores the images used in the README and other documentation
- **`lambdas/`**: This directory contains AWS Lambda functions for various cloud-based operations.
  - **`lambdas/contextual_retrieval/`**: This directory contains AWS lambda code(in python) for contextual retrieval
    - **`lambdas/contextual_retrieval/lambda_function.py`**: AWS Lambda function used by AWS Bedrock Knowledge Base to generate contextual summaries for document chunks and adds them to the beginning of each chunk, improving retrieval accuracy and relevance.
  - **`lambdas/metadata_filtering/`**: This directory contains AWS lambda code(in python) for metadata filtering
    - **`lambdas/metadata_filtering/lambda_function.py`**: AWS Lambda function triggered by S3 put events to generate metadata.json files for each file in the knowledge base. It generates specific tags for each file to improve retrieval and optimizing performance.
  - **`lambdas/documentation_scraper/`**: This directory contains AWS lambda code(in python) for automated documentation scraping
    - **`lambdas/documentation_scraper/lambda_function.py`**: AWS Lambda function that automatically scrapes documentation websites using the utils data pipeline helpers and uploads content to S3. Scheduled to run weekly on Sundays at 12:00 PM EDT/11:00 AM EST via EventBridge.
    - **`lambdas/documentation_scraper/requirements.txt`**: Python dependencies specific to the documentation scraper Lambda function.
  - **`lambdas/slack_scraper/`**: This directory contains AWS lambda code(in python) for automated Slack conversation scraping
    - **`lambdas/slack_scraper/lambda_function.py`**: AWS Lambda function that automatically scrapes Slack channel conversations from the last week using the slack_scripts/slack_scraper.py functions and uploads them to S3. Scheduled to run weekly on Sundays at 12:00 PM EDT/11:00 AM EST via EventBridge.
    - **`lambdas/slack_scraper/requirements.txt`**: Python dependencies specific to the Slack scraper Lambda function.
  - **`lambdas/slack_lambda/`**: This directory contains AWS lambda code(in python) for serverless Slack bot functionality
    - **`lambdas/slack_lambda/slack_lambda.py`**: The serverless version of the Slack bot that implements RAG chatbot functionality using AWS Lambda with lazy listeners for FaaS environments. Uses the same shared helper functions as the Socket Mode version but optimized for Lambda's execution model.
    - **`lambdas/slack_lambda/requirements.txt`**: Python dependencies specific to the Lambda deployment of the Slack bot.
- **`.dockerignore`**: Specifies files and directories that should be ignored by Docker when building images, similar to `.gitignore`.
- **`cloudformation-templates/`**: Directory containing AWS CloudFormation templates for infrastructure deployment.
  - **`cloudformation-template-chatbot.yml`**: AWS CloudFormation template that defines the infrastructure for the Streamlit chatbot, including VPC, ECS cluster, load balancer, and other AWS resources.
  - **`cloudformation-template-slackbot-ecs.yml`**: AWS CloudFormation template that defines the infrastructure for the Slack bot, including VPC, ECS cluster, and other AWS resources.
  - **`documentation-scraper-lambda.yml`**: AWS CloudFormation template that defines the infrastructure for the documentation scraper Lambda function, including IAM roles, EventBridge scheduling, and CloudWatch logging. Configured to run weekly on Sundays at 12:00 PM EDT/11:00 AM EST.
  - **`slack-scraper-lambda.yml`**: AWS CloudFormation template that defines the infrastructure for the Slack conversation scraper Lambda function, including IAM roles, EventBridge scheduling, and CloudWatch logging. Configured to run weekly on Sundays at 12:00 PM EDT/11:00 AM EST.
  - **`slack-lambda-infrastructure.yml`**: AWS CloudFormation template that defines the complete infrastructure for the Unity Slack Lambda bot, including the Lambda function, API Gateway REST API, IAM roles, and all necessary permissions for serverless Slack bot functionality.
- **`Dockerfiles/`**: Directory containing Docker configuration files.
  - **`Dockerfiles/chatbot_dockerfile`**: Defines the steps to build the Docker image for the Streamlit chatbot application, specifying the base image, dependencies, and application setup.
  - **`Dockerfiles/slackbot_dockerfile`**: Defines the steps to build the Docker image for the Slack bot application.
- **`.env.example`**: Template for the .env file without any of the key values.
- **`requirements.txt`**: Lists all the Python dependencies required to run the chatbot application, used for `pip install`.
- **`LICENSE`**: The license file for the project.
- **`.gitignore`**: Specifies files and directories that Git should ignore.
- **`.github/`**: GitHub-specific configuration files.
  - **`.github/pull_request_template.md`**: Template for pull requests with checklist for code quality, testing, and documentation requirements.
  - **`.github/workflows/deploy-chatbot.yml`**: GitHub Actions workflow file that automates the CI/CD pipeline for deploying the Streamlit chatbot application to AWS ECS.
  - **`.github/workflows/deploy-slackbot-ecs.yml`**: GitHub Actions workflow file that automates the CI/CD pipeline for deploying the Socket Mode Slack bot application to AWS ECS.
  - **`.github/workflows/deploy-slack-lambda.yml`**: GitHub Actions workflow file that automates the CI/CD pipeline for deploying the serverless Slack bot to AWS Lambda, including dependency layer management and API Gateway integration.
  - **`.github/workflows/deploy-documentation-scraper.yml`**: GitHub Actions workflow file that automates the CI/CD pipeline for deploying the documentation scraper Lambda function, including dependency layer creation, function deployment, and EventBridge scheduling configuration.
  - **`.github/workflows/deploy-slack-scraper.yml`**: GitHub Actions workflow file that automates the CI/CD pipeline for deploying the Slack conversation scraper Lambda function, including dependency layer creation, function deployment, and EventBridge scheduling configuration.
  - **`.github/workflows/deploy-slack-lambda-bot.yml`**: GitHub Actions workflow file that automates the CI/CD pipeline for deploying the Unity Slack Lambda bot with API Gateway integration, including infrastructure deployment, dependency layer creation, and function deployment.
