# 🧠 Unity RAG Chatbot

This is the code repository for the RAG chatbot based on the Unity HPC documentation

## 📋 Table of Contents

- [📂 Structure](#-structure)
- [📄 File Descriptions](#-file-descriptions)
- [🏗️ Deployment to AWS](#️-deployment-to-aws)
  - [🏗️ Deployment Architecture](#️-deployment-architecture)
  - [⚙️ Deployment Process](#️-deployment-process)
- [🛠️ Installation and usage (Streamlit Chatbot)](#️-installation-and-usagefor-the-streamlit-chatbot-and-dashboard)
- [🛠️ Installation and usage (Slack Chatbot)](#️-installation-and-usagefor-the-slack-chatbot)


# 📂 Structure
```
├── README.md
├── README-DEPLOYMENT.md
├── .env.example (Template for the .env file)
├── pages/
│ ├── dashboard.py
├── utils/
│ ├── chatbot_helper.py
│ ├── feedback.py
| |── prompts.py
│ └── data_pipeline/
│     ├── scrape_and_upload_to_s3.py
│     ├── scrapping_helper.py
│     └── link_cleaner.py
├── qa_pairs/
│ ├── slack_qa_generator.py
│ ├── slack_conversations.md
| |── slack_qa_pairs_{}_{}.json
├── chatbot.py
├── slack_bot.py
├── slack_scraper.py
├── automated_test.py
├── test_results/
│ ├── claude_comparison_results.json
│ └── claude_comparison_results.md
├── documents/
│ └── (Contains scraped Unity HPC documentation in Markdown files)
├── .github/
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
├── docker-compose.yaml
├── requirements.txt
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
*   **`qa_pairs/`**: This directory contains code and sample inputs and outputs for generating q&a pairs from slack conversation history stored as markdown and stores them locally as json
    *   **`qa_pairs/slack_qa_generator.py`**: A script for converting slack conversation histories stored in markdown to json using LLMs
    *   **`qa_pairs/slack_conversations.md`**: Contains the slack history in markdown format
    *   **`qa_pairs/slack_qa_pairs_{}_{}.json`**: Stores the output of `qa_pairs/slack_qa_generator.py` in a json file.
*   **`chatbot.py`**: The core Streamlit application that implements the Retrieval-Augmented Generation (RAG) chatbot functionality.
*   **`slack_bot.py`**: The core slack_bot code that implements the Retrieval-Augmented Generation (RAG) chatbot functionality in slack using the slack bolt library.
*   **`slack_scraper.py`**: A script to scrape conversations from Slack channels and store them as markdown files in S3.
*   **`automated_test.py`**: Contains automated tests for the chatbot, ensuring its functionality and reliability.
*   **`test_results/`**: This directory stores the results of automated tests, such as comparison outcomes for different models.
    *   **`test_results/claude_comparison_results.json`**: Stores the raw JSON results from comparisons, with Claude 3.7 sonnet.
    *   **`test_results/claude_comparison_results.md`**: A human-readable Markdown report summarizing the comparison results, with Claude 3.7 sonnet.
*   **`documents/`**: This directory stores the scraped documentation in Markdown format, which serves as the knowledge base for the RAG chatbot.
*   **`.dockerignore`**: Specifies files and directories that should be ignored by Docker when building images, similar to `.gitignore`.
*   **`cloudformation-templates/`**: Directory containing AWS CloudFormation templates for infrastructure deployment.
    *   **`cloudformation-templates/cloudformation-template-chatbot.yml`**: AWS CloudFormation template that defines the infrastructure for the Streamlit chatbot, including VPC, ECS cluster, load balancer, and other AWS resources.
    *   **`cloudformation-templates/cloudformation-template-slackbot.yml`**: AWS CloudFormation template that defines the infrastructure for the Slack bot, including VPC, ECS cluster, and other AWS resources.
*   **`Dockerfiles/`**: Directory containing Docker configuration files.
    *   **`Dockerfiles/chatbot_dockerfile`**: Defines the steps to build the Docker image for the Streamlit chatbot application, specifying the base image, dependencies, and application setup.
    *   **`Dockerfiles/slackbot_dockerfile`**: Defines the steps to build the Docker image for the Slack bot application.
*   **`.env.example`**: Template for the .env file without any of the key values.
*   **`requirements.txt`**: Lists all the Python dependencies required to run the chatbot application, used for `pip install`.
*   **`LICENSE`**: The license file for the project.
*   **`.gitignore`**: Specifies files and directories that Git should ignore.
*   **`README-DEPLOYMENT.md`**: Detailed instructions for deploying the application to AWS.
*   **`.github/workflows/deploy-chatbot.yml`**: GitHub Actions workflow file that automates the CI/CD pipeline for deploying the Streamlit chatbot application to AWS.
*   **`.github/workflows/deploy-slackbot.yml`**: GitHub Actions workflow file that automates the CI/CD pipeline for deploying the Slack bot application to AWS.


# 🏗️ Deployment to AWS

The applications can be automatically deployed to AWS using the GitHub Actions workflows and CloudFormation templates included in this repository. For detailed deployment instructions, see [README-DEPLOYMENT.md](README-DEPLOYMENT.md).

## 🏗️ Deployment Architecture

This project uses a dual-deployment architecture:

1. **Streamlit Chatbot** - A web application with public access via an Application Load Balancer
2. **Slack Bot** - A background service that connects to Slack without public internet access

## ⚙️ Deployment Process

Both applications are deployed independently through separate GitHub Actions workflows that run when:
- Code is pushed to the main branch
- The workflow is manually triggered

Each workflow:
1. Builds the respective Docker image (chatbot or slackbot)
2. Pushes it to Amazon ECR
3. Creates or updates the corresponding CloudFormation stack
4. Deploys the application to ECS

The CloudFormation templates provision all necessary AWS resources including:
- VPC and networking components
- ECS clusters and services
- Application Load Balancer (for the chatbot only)
- IAM roles and policies
- CloudWatch logs

# 🛠️ Installation and usage(for the streamlit chatbot and dashboard)

There are two ways to run the chatbot: With Docker or without

<details>
<summary>Docker</summary>
 

## 1️⃣ Prerequisites

Make sure that you have docker desktop installed and running. 

You also need to have access to an AWS account, have a specific S3 bucket along with a folder where you can store the scraped content as well as have to have connected your S3 bucket to an AWS Bedrock Knowledge base

There is a .env.example file where the keys are defined, just copy these in your .env file using

```
cp .env.example .env
```

and then fill the .env file with AWS credentials, knowledge base id, as well as your S3 bucket name and folder name(where you will store the scraped content)

Remember to never commit .env files

## 2️⃣ Run the streamlit Application

Run the streamlit application using the following command:

```
docker-compose up --build
```

## 3️⃣ Access the Application

Once the server is running, you can access the streamlit application in your web browser at: `http://localhost:8501/`

## 4️⃣ Stopping the application

You can end the application using CTRL+C . Make sure to have the streamlit application website is open in the browser otherwise the command doesn't work, in which case, you need to kill the terminal.

</details>

<details>
<summary>Without Docker</summary>

## 1️⃣ Prerequisites

Make sure you have the following installed on your machine:

- Python 3.7 or higher
- pip (Python package installer)

You also need to have access to an AWS account, have a specific S3 bucket along with a folder where you can store the scraped content as well as have to have connected your S3 bucket to an AWS Bedrock Knowledge base

There is a .env.example file where the keys are defined, just copy these in your .env file using

```
cp .env.example .env
```

and then fill the .env file with AWS credentials, knowledge base id, as well as your S3 bucket name and folder name(where you will store the scraped content)

Remember to never commit .env files

## 2️⃣ Create a Virtual Environment
Create a virtual environment to isolate your project dependencies:

```
python -m venv .venv
```

## 3️⃣ Activate the Virtual Environment

Activate the virtual environment:

<details>
<summary>For Windows Powershell</summary>

```
.venv\Scripts\activate.ps1
```

</details>

<details>
<summary>For Windows Command Prompt </summary>

```
.venv\Scripts\Activate.bat
```

</details>

<details>
<summary>For MacOs/Linux</summary>

```
source .venv/bin/activate
```

</details>

## 4️⃣ Install/Update Dependencies

Install the required packages from requirements.txt:

```
pip install -r requirements.txt
```

If you install any new dependencies, make sure to install them within the
virtual environment and run the following command to update the requirements.txt file

```
pip freeze > requirements.txt
```

## 5️⃣ Run the streamlit Application

Run the streamlit application using the following command:

```
streamlit run chatbot.py
```

## 6️⃣ Access the Application

Once the server is running, you can access the streamlit application in your web browser at: `http://localhost:8501/`

## 7️⃣ Stopping the Application

You can end the application using CTRL+C . Make sure to have the streamlit application website is open in the browser otherwise the command doesn't work, in which case, you need to kill the terminal.

## 8️⃣ Deactivating the Virtual Environment

When you're done working, you can deactivate the virtual environment by running:

```
deactivate
```
</details>


# 🛠️ Installation and usage(for the slack chatbot)

## 1️⃣ Prerequisites

Make sure you have the following installed on your machine:

- Python 3.7 or higher
- pip (Python package installer)

There is a .env.example file where the keys are defined, just copy these in your .env file using

```
cp .env.example .env
```

and then fill the .env file with your credentials. These credentials are defined in the above instructions for the chatbot.
You also need to setup a slack app beforehand and have the slack bot and slack app tokens ready. Make sure to give your app the following permissions (`app_mentions:read`, `assistant:write`, `channels:history`, `chat:write`, `groups:history`, `im:history`, `im:read`, `users:read`)

Remember to never commit .env files

## 2️⃣ Create a Virtual Environment
Create a virtual environment to isolate your project dependencies:

```
python -m venv .venv
```

## 3️⃣ Activate the Virtual Environment

Activate the virtual environment:

<details>
<summary>For Windows Powershell</summary>

```
.venv\Scripts\activate.ps1
```

</details>

<details>
<summary>For Windows Command Prompt </summary>

```
.venv\Scripts\Activate.bat
```

</details>

<details>
<summary>For MacOs/Linux</summary>

```
source .venv/bin/activate
```

</details>

## 4️⃣ Install/Update Dependencies

Install the required packages from requirements.txt:

```
pip install -r requirements.txt
```

If you install any new dependencies, make sure to install them within the
virtual environment and run the following command to update the requirements.txt file

```
pip freeze > requirements.txt
```

## 5️⃣ Run the Slack bot 

Run the slack bot using the following command:

```
python slack_bot.py
```

## 6️⃣ Stopping the Application

You can end the application using CTRL+C . 

## 7️⃣ Deactivating the Virtual Environment

When you're done working, you can deactivate the virtual environment by running:

```
deactivate
```
