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
│ ├── SLACK-SETUP.md
│ ├── KNOWLEDGE-BASE-SETUP.md
│ ├── structure.md
│ └── manifests/
│     └── (Slack app manifest files for different deployment methods)
├── local_testing/
│ ├── automated_test.py
│ ├── test_data/
│ │ └── conversation_threads.json
│ └── test_results/
│   └── (stores the test results)
├── images/
│ └── (screenshots, diagrams, and visual assets for documentation)
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
├── .dockerignore
├── LICENSE
└── .gitignore
```

## 📄 File Descriptions

### Core Components (Required)

- **`README.md`**: The main documentation file for this project, providing an overview, setup instructions, and details about the codebase structure.
- **`utils/`**: This directory contains utility functions and helper modules used across the application.
  - **`utils/slackbot_helper.py`**: Contains shared helper functions for Slack bot functionality, including conversation history reconstruction, image processing, query optimization, and multimodal message creation. Used by the Lambda-based Slack bot.
  - **`utils/prompts.py`**: Contains the system prompts used throughout the application, including specialized prompts for Slack interactions with followup question generation.
  - **`utils/data_pipeline/`**: This subdirectory contains scripts responsible for data ingestion and processing.
    - **`utils/data_pipeline/scrape_and_upload_to_s3.py`**: A script designed to scrape documentation content and upload it to an AWS S3 bucket.
    - **`utils/data_pipeline/scrapping_helper.py`**: Contains helper functions and utilities used by the scraping scripts within the data pipeline.
    - **`utils/data_pipeline/link_cleaner.py`**: A script for cleaning and normalizing URLs and links found during the scraping process.
- **`slack_scripts/`**: This directory contains Slack-related functionality.
  - **`slack_scripts/slack_scraper.py`**: A script to scrape conversations from Slack channels and store them as markdown files in S3. Used by the Lambda scraper function.
- **`docs/`**: This directory contains documentation files.
  - **`docs/README-DEPLOYMENT.md`**: Detailed instructions for deploying the Lambda functions to AWS using GitHub Actions.
  - **`docs/SLACK-SETUP.md`**: Step-by-step guide for setting up Slack apps and configuring bot permissions.
  - **`docs/KNOWLEDGE-BASE-SETUP.md`**: Instructions for creating and configuring AWS Bedrock Knowledge Base.
  - **`docs/structure.md`**: Detailed project structure and file descriptions.
  - **`docs/manifests/`**: Directory containing Slack app manifest files for quick app setup with pre-configured permissions and settings for different deployment methods (Lambda, ECS, and scraper configurations).

### Optional Components (For Development/Testing)

- **`pages/`**: This directory contains other pages for the streamlit app (optional Streamlit dashboard).
  - **`pages/dashboard.py`**: The Streamlit dashboard with five tabs for managing the system (optional).
- **`utils/chatbot_helper.py`**: Contains modular functions for the optional Streamlit chatbot application.
- **`utils/streamlit_components.py`**: Contains reusable Streamlit UI components (optional).
- **`utils/feedback.py`**: Handles user feedback collection for the optional chatbot interface.
- **`utils/qa_pair_tab.py`**: Dashboard tab for generated Q&A Pairs (optional).
- **`chatbot.py`**: The optional Streamlit application that implements the RAG chatbot functionality.
- **`qa_pairs/`**: This directory contains scripts for generating question-answer pairs from Slack conversations (optional).
  - **`qa_pairs/slack_qa_generator.py`**: A script that converts Slack conversations from S3 markdown into structured question-answer pairs.
- **`slack_scripts/slack_bot.py`**: The optional Socket Mode Slack bot for ECS deployment.
- **`local_testing/`**: This directory contains all testing-related files and scripts for local development and validation (optional).
  - **`local_testing/automated_test.py`**: Contains automated tests for the chatbot.
  - **`local_testing/test_data/`**: Test data used by automated testing scripts.
    - **`local_testing/test_data/conversation_threads.json`**: Sample conversation threads for testing.
  - **`local_testing/test_results/`**: Stores the results of automated tests.
- **`images/`**: This directory stores screenshots, diagrams, and visual assets used throughout the documentation, including setup guides, architectural diagrams, and user interface examples.
- **`lambdas/`**: This directory contains AWS Lambda functions for the core serverless functionality.
  - **`lambdas/contextual_retrieval/`**: **[REQUIRED]** AWS Lambda function for contextual retrieval
    - **`lambdas/contextual_retrieval/lambda_function.py`**: AWS Lambda function used by AWS Bedrock Knowledge Base to generate contextual summaries for document chunks and adds them to the beginning of each chunk, improving retrieval accuracy and relevance.
  - **`lambdas/metadata_filtering/`**: **[REQUIRED]** AWS Lambda function for metadata filtering
    - **`lambdas/metadata_filtering/lambda_function.py`**: AWS Lambda function triggered by S3 put events to generate metadata.json files for each file in the knowledge base. It generates specific tags for each file to improve retrieval and optimizing performance.
  - **`lambdas/documentation_scraper/`**: **[REQUIRED]** AWS Lambda function for automated documentation scraping
    - **`lambdas/documentation_scraper/lambda_function.py`**: AWS Lambda function that automatically scrapes documentation websites using the utils data pipeline helpers and uploads content to S3. Scheduled to run weekly on Sundays at 12:00 PM EDT/11:00 AM EST via EventBridge.
    - **`lambdas/documentation_scraper/requirements.txt`**: Python dependencies specific to the documentation scraper Lambda function.
  - **`lambdas/slack_scraper/`**: **[REQUIRED]** AWS Lambda function for automated Slack conversation scraping
    - **`lambdas/slack_scraper/lambda_function.py`**: AWS Lambda function that automatically scrapes Slack channel conversations from the last week using the slack_scripts/slack_scraper.py functions and uploads them to S3. Scheduled to run weekly on Sundays at 12:00 PM EDT/11:00 AM EST via EventBridge.
    - **`lambdas/slack_scraper/requirements.txt`**: Python dependencies specific to the Slack scraper Lambda function.
  - **`lambdas/slack_lambda/`**: **[REQUIRED]** AWS Lambda function for serverless Slack bot functionality
    - **`lambdas/slack_lambda/slack_lambda.py`**: The serverless Slack bot that implements RAG chatbot functionality using AWS Lambda with lazy listeners for FaaS environments. This is the main bot that users interact with in Slack.
    - **`lambdas/slack_lambda/requirements.txt`**: Python dependencies specific to the Lambda deployment of the Slack bot.
- **`cloudformation-templates/`**: Directory containing AWS CloudFormation templates for infrastructure deployment.
  - **`documentation-scraper-lambda.yml`**: AWS CloudFormation template for the documentation scraper Lambda function, including IAM roles, EventBridge scheduling, and CloudWatch logging.
  - **`slack-scraper-lambda.yml`**: AWS CloudFormation template for the Slack conversation scraper Lambda function, including IAM roles, EventBridge scheduling, and CloudWatch logging.
  - **`slack-lambda-infrastructure.yml`**: AWS CloudFormation template that defines the complete infrastructure for the Unity Slack Lambda bot, including the Lambda function, API Gateway REST API, IAM roles, and all necessary permissions.

### Optional Files (For Development/Alternative Deployments)

- **`.dockerignore`**: Specifies files and directories that should be ignored by Docker when building images (optional for Docker deployments).
- **`cloudformation-template-chatbot.yml`**: AWS CloudFormation template for optional Streamlit chatbot ECS deployment.
- **`cloudformation-template-slackbot-ecs.yml`**: AWS CloudFormation template for optional Socket Mode Slack bot ECS deployment.
- **`Dockerfiles/`**: Directory containing Docker configuration files (optional for ECS deployments).
  - **`Dockerfiles/chatbot_dockerfile`**: Docker image configuration for the optional Streamlit chatbot application.
  - **`Dockerfiles/slackbot_dockerfile`**: Docker image configuration for the optional Socket Mode Slack bot application.
- **`.env.example`**: Template for the .env file without any of the key values.
- **`requirements.txt`**: Lists all the Python dependencies required to run the chatbot application, used for `pip install`.
- **`LICENSE`**: The license file for the project.
- **`.gitignore`**: Specifies files and directories that Git should ignore.
- **`.github/`**: GitHub-specific configuration files.
  - **`.github/pull_request_template.md`**: Template for pull requests with checklist for code quality, testing, and documentation requirements.
  - **`.github/workflows/deploy-slack-lambda-bot.yml`**: **[REQUIRED]** GitHub Actions workflow file that automates the CI/CD pipeline for deploying the Unity Slack Lambda bot with API Gateway integration, including infrastructure deployment, dependency layer creation, and function deployment.
  - **`.github/workflows/deploy-documentation-scraper.yml`**: **[REQUIRED]** GitHub Actions workflow file that automates the CI/CD pipeline for deploying the documentation scraper Lambda function, including dependency layer creation, function deployment, and EventBridge scheduling configuration.
  - **`.github/workflows/deploy-slack-scraper.yml`**: **[REQUIRED]** GitHub Actions workflow file that automates the CI/CD pipeline for deploying the Slack conversation scraper Lambda function, including dependency layer creation, function deployment, and EventBridge scheduling configuration.

### Optional GitHub Workflows (For Alternative Deployments)

- **`.github/workflows/deploy-chatbot.yml`**: GitHub Actions workflow for deploying the optional Streamlit chatbot application to AWS ECS.
- **`.github/workflows/deploy-slackbot-ecs.yml`**: GitHub Actions workflow for deploying the optional Socket Mode Slack bot application to AWS ECS.
- **`.github/workflows/deploy-slack-lambda.yml`**: Alternative GitHub Actions workflow for deploying the serverless Slack bot (use deploy-slack-lambda-bot.yml instead).
