# 📂 Structure
```
├── README.md
├── .env.example
├── chatbot.py
├── automated_test.py
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
│ ├── feedback.py
│ ├── prompts.py
│ └── data_pipeline/
│     ├── scrape_and_upload_to_s3.py
│     ├── scrapping_helper.py
│     └── link_cleaner.py
├── docs/
│ ├── README-DEPLOYMENT.md
│ └── structure.md
├── test_data/
│ └── conversation_threads.json
├── test_results/
│ ├── claude_comparison_results.json
│ └── claude_comparison_results.md
├── images/
│ └── (stores images for use in the README and other documentation)
├── .github/
│ ├── pull_request_template.md
│ └── workflows/
│     ├── deploy-chatbot.yml
│     └── deploy-slackbot.yml
├── cloudformation-templates/
│ ├── cloudformation-template-chatbot.yml
│ └── cloudformation-template-slackbot.yml
├── Dockerfiles/
│ ├── chatbot_dockerfile
│ └── slackbot_dockerfile
├── .dockerignore
├── LICENSE
└── .gitignore
```

## 📄 File Descriptions

*   **`README.md`**: The main documentation file for this project, providing an overview, setup instructions, and details about the codebase structure.
*   **`pages/`**: This directory contains other pages for the streamlit app. This is how multi-page streamlit apps are made.
    *   **`pages/dashboard.py`**: The Streamlit dashboard with three tabs: User Feedback Analytics, Data Pipeline Management (for tracking scraped documentation), and Slack Conversations (for viewing and editing Slack channel conversations).
*   **`utils/`**: This directory contains utility functions and helper modules used across the application.
    *   **`utils/chatbot_helper.py`**: Contains modular functions and helper utilities used across the chatbot application, promoting code reusability and organization.
    *   **`utils/prompts.py`**: Contains the system prompt used throughout the application
    *   **`utils/feedback.py`**: Handles user feedback collection and analytics functionality for the chatbot interface.
    *   **`utils/data_pipeline/`**: This subdirectory contains scripts responsible for data ingestion and processing.
        *   **`utils/data_pipeline/scrape_and_upload_to_s3.py`**: A script designed to scrape documentation content and upload it to an AWS S3 bucket.
        *   **`utils/data_pipeline/scrapping_helper.py`**: Contains helper functions and utilities used by the scraping scripts within the data pipeline.
        *   **`utils/data_pipeline/link_cleaner.py`**: A script for cleaning and normalizing URLs and links found during the scraping process. Used in the chatbot to clean URLs from S3 filenames for displaying to users.
*   **`chatbot.py`**: The core Streamlit application that implements the Retrieval-Augmented Generation (RAG) chatbot functionality.
*   **`qa_pairs/`**: This directory contains scripts for generating question-answer pairs from Slack conversations.
    *   **`qa_pairs/slack_qa_generator.py`**: A script that converts Slack conversations from S3 markdown into structured question-answer pairs using LLM processing.
*   **`slack_scripts/`**: This directory contains Slack-related functionality.
    *   **`slack_scripts/slack_bot.py`**: The core slack_bot code that implements the Retrieval-Augmented Generation (RAG) chatbot functionality in slack using the slack bolt library.
    *   **`slack_scripts/slack_scraper.py`**: A script to scrape conversations from Slack channels and store them as markdown files in S3.
*   **`docs/`**: This directory contains documentation files.
    *   **`docs/README-DEPLOYMENT.md`**: Detailed instructions for deploying the application to AWS.
    *   **`docs/structure.md`**: Detailed project structure and file descriptions.
*   **`test_data/`**: This directory contains test data used by automated testing scripts.
    *   **`test_data/conversation_threads.json`**: Contains conversation threads with sample questions used by automated_test.py for testing chatbot responses across different scenarios.
*   **`automated_test.py`**: Contains automated tests for the chatbot, ensuring its functionality and reliability.
*   **`test_results/`**: This directory stores the results of automated tests, such as comparison outcomes for different models.
    *   **`test_results/claude_comparison_results.json`**: Stores the raw JSON results from comparisons, with Claude 3.7 sonnet.
    *   **`test_results/claude_comparison_results.md`**: A human-readable Markdown report summarizing the comparison results, with Claude 3.7 sonnet.
*   **`images/`**: This directory stores the images used in the README and other documentation
*   **`.dockerignore`**: Specifies files and directories that should be ignored by Docker when building images, similar to `.gitignore`.
*   **`cloudformation-templates/`**: Directory containing AWS CloudFormation templates for infrastructure deployment.
    *   **`cloudformation-template-chatbot.yml`**: AWS CloudFormation template that defines the infrastructure for the Streamlit chatbot, including VPC, ECS cluster, load balancer, and other AWS resources.
    *   **`cloudformation-template-slackbot.yml`**: AWS CloudFormation template that defines the infrastructure for the Slack bot, including VPC, ECS cluster, and other AWS resources.
*   **`Dockerfiles/`**: Directory containing Docker configuration files.
    *   **`Dockerfiles/chatbot_dockerfile`**: Defines the steps to build the Docker image for the Streamlit chatbot application, specifying the base image, dependencies, and application setup.
    *   **`Dockerfiles/slackbot_dockerfile`**: Defines the steps to build the Docker image for the Slack bot application.
*   **`.env.example`**: Template for the .env file without any of the key values.
*   **`requirements.txt`**: Lists all the Python dependencies required to run the chatbot application, used for `pip install`.
*   **`LICENSE`**: The license file for the project.
*   **`.gitignore`**: Specifies files and directories that Git should ignore.
*   **`.github/`**: GitHub-specific configuration files.
    *   **`.github/pull_request_template.md`**: Template for pull requests with checklist for code quality, testing, and documentation requirements.
    *   **`.github/workflows/deploy-chatbot.yml`**: GitHub Actions workflow file that automates the CI/CD pipeline for deploying the Streamlit chatbot application to AWS.
    *   **`.github/workflows/deploy-slackbot.yml`**: GitHub Actions workflow file that automates the CI/CD pipeline for deploying the Slack bot application to AWS.