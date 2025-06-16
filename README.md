# Unity RAG Chatbot

This is the code repository for the RAG chatbot based on the Unity HPC documentation

# Structure
```
├── README.md
├── data_pipeline/
│ ├── scrape_and_upload_to_s3.py
│ ├── scrapping_helper.py
│ └── link_cleaner.py
├── .env.example (Template for the .env file)
├── pages/
│ ├── dashboard.py
├── chatbot.py
├── slack_bot.py
├── chatbot_helper.py
├── automated_test.py
├── test_results/
│ ├── claude_comparison_results.json
│ └── claude_comparison_results.md
├── documents/
│ └── (Contains scraped Unity HPC documentation in Markdown files)
├── .dockerignore
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── LICENSE
└── .gitignore
```


## File Descriptions

*   **`README.md`**: The main documentation file for this project, providing an overview, setup instructions, and details about the codebase structure.
*   **`data_pipeline/`**: This directory contains scripts responsible for data ingestion and processing.
    *   **`data_pipeline/scrape_and_upload_to_s3.py`**: A script designed to scrape documentation content and upload it to an AWS S3 bucket.
    *   **`data_pipeline/scrapping_helper.py`**: Contains helper functions and utilities used by the scraping scripts within the `data_pipeline`.
    *   **`data_pipeline/link_cleaner.py`**: A script for cleaning and normalizing URLs and links found during the scraping process. Used in the chatbot, to clean URLs from the S3 filename for displaying to the user since it's not advised to use slashes in S3  filenames.
*   **`pages/`**: This directory contains other pages for the streamlit app. This is how multi-page streamlit apps are made.
    *   **`pages/dashboard.py`**: his file has the streamlit dashbaord to keep track of when a documentation link was last scraped, and has buttons to either scrape a specific URL again or scrape all URLs according to the logic in `data_pipeline/scrape_and_upload_to_s3.py`
*   **`chatbot.py`**: The core Streamlit application that implements the Retrieval-Augmented Generation (RAG) chatbot functionality.
*   **`slack_bot.py`**: The core slack_bot code that implements the Retrieval-Augmented Generation (RAG) chatbot functionality in slack using the slack bolt library.
*   **`chatbot_helper.py`**: This file contains modular functions and helper utilities used across the chatbot application, promoting code reusability and organization.
*   **`automated_test.py`**: Contains automated tests for the chatbot, ensuring its functionality and reliability.
*   **`test_results/`**: This directory stores the results of automated tests, such as comparison outcomes for different models.
    *   **`test_results/claude_comparison_results.json`**: Stores the raw JSON results from comparisons, with Claude 3.7 sonnet.
    *   **`test_results/claude_comparison_results.md`**: A human-readable Markdown report summarizing the comparison results, with Claude 3.7 sonnet.
*   **`documents/`**: This directory stores the scraped documentation in Markdown format, which serves as the knowledge base for the RAG chatbot.
*   **`.dockerignore`**: Specifies files and directories that should be ignored by Docker when building images, similar to `.gitignore`.
*   **`docker-compose.yaml`**: A Docker Compose configuration file that defines how to run the multi-container Docker application, including the Streamlit app.
*   **`Dockerfile`**: Defines the steps to build the Docker image for the chatbot application, specifying the base image, dependencies, and application setup.
*   **`.env.example`**: Template for the .env file without any of the key values.
*   **`requirements.txt`**: Lists all the Python dependencies required to run the chatbot application, used for `pip install`.
*   **`LICENSE`**: The license file for the project.
*   **`.gitignore`**: Specifies files and directories that Git should ignore.


# Installation and usage(for the streamlit chatbot and dashboard)

There are two ways to run the chatbot: With Docker or without

<details>
<summary>Docker</summary>
 

## 1. Prerequisites

Make sure that you have docker desktop installed and running. 

You also need to have access to an AWS account, have a specific S3 bucket along with a folder where you can store the scraped content as well as have to have connected your S3 bucket to an AWS Bedrock Knowledge base

There is a .env.example file where the keys are defined, just copy these in your .env file using

```
cp .env.example .env
```

and then fill the .env file with AWS credentials, knowledge base id, as well as your S3 bucket name and folder name(where you will store the scraped content)

Remember to never commit .env files

## 2. Run the streamlit Application

Run the streamlit application using the following command:

```
docker-compose up --build
```

## 3. Access the Application

Once the server is running, you can access the streamlit application in your web browser at: `http://localhost:8501/`

## 4. Stopping the application

You can end the application using CTRL+C . Make sure to have the streamlit application website is open in the browser otherwise the command doesn't work, in which case, you need to kill the terminal.

</details>

<details>
<summary>Without Docker</summary>

## 1. Prerequisites

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

## 2. Create a Virtual Environment
Create a virtual environment to isolate your project dependencies:

```
python -m venv .venv
```

## 3. Activate the Virtual Environment

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

## 4. Install/Update Dependencies

Install the required packages from requirements.txt:

```
pip install -r requirements.txt
```

If you install any new dependencies, make sure to install them within the
virtual environment and run the following command to update the requirements.txt file

```
pip freeze > requirements.txt
```

## 5. Run the streamlit Application

Run the streamlit application using the following command:

```
streamlit run chatbot.py
```

## 6. Access the Application

Once the server is running, you can access the streamlit application in your web browser at: `http://localhost:8501/`

## 7. Stopping the Application

You can end the application using CTRL+C . Make sure to have the streamlit application website is open in the browser otherwise the command doesn't work, in which case, you need to kill the terminal.

## 8. Deactivating the Virtual Environment

When you're done working, you can deactivate the virtual environment by running:

```
deactivate
```
</details>


# Installation and usage(for the slack chatbot)

## 1. Prerequisites

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

## 2. Create a Virtual Environment
Create a virtual environment to isolate your project dependencies:

```
python -m venv .venv
```

## 3. Activate the Virtual Environment

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

## 4. Install/Update Dependencies

Install the required packages from requirements.txt:

```
pip install -r requirements.txt
```

If you install any new dependencies, make sure to install them within the
virtual environment and run the following command to update the requirements.txt file

```
pip freeze > requirements.txt
```

## 5. Run the Slack bot 

Run the slack bot using the following command:

```
python slack_bot.py
```

## 6. Stopping the Application

You can end the application using CTRL+C . 

## 7. Deactivating the Virtual Environment

When you're done working, you can deactivate the virtual environment by running:

```
deactivate
```
