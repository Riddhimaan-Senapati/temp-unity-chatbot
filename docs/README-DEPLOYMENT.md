# 🚀 Deploying Unity Chatbot and Slackbot to AWS

This guide explains how to deploy both the Unity Chatbot and Slackbot applications to AWS using the CI/CD pipelines set up with GitHub Actions.

## 📋 Table of Contents

- [📂 Deployment Architecture](#-deployment-architecture)
- [📋 Prerequisites](#-prerequisites)
- [🔧 Step 1: Set Up Required AWS Resources](#-step-1-set-up-required-aws-resources)
  - [🔐 1.1 Create SSL Certificate](#-11-create-ssl-certificate-for-chatbot-only)
  - [🌐 1.2 Set Up Route 53 Hosted Zone](#-12-set-up-route-53-hosted-zone-for-chatbot-only)
- [🔑 Step 2: Configure GitHub Secrets](#-step-2-configure-github-secrets)
- [🚀 Step 3: Deploy Your Applications](#-step-3-deploy-your-applications)
- [✅ Step 4: Verify Deployments](#-step-4-verify-deployments)
  - [🌐 Chatbot Verification](#-chatbot-verification)
  - [💬 Slackbot Verification](#-slackbot-verification)
- [🔧 Troubleshooting](#-troubleshooting)
- [🔄 Updating the Applications](#-updating-the-applications)
- [🧹 Cleaning Up](#-cleaning-up)

## 📂 Deployment Architecture

This project uses a dual-deployment architecture:

1. **Streamlit Chatbot** - A web application with public access via an Application Load Balancer
2. **Slack Bot** - A background service that connects to Slack without public internet access

## 📋 Prerequisites

1. **AWS Account**: You need an AWS account with appropriate permissions.
2. **GitHub Repository**: Your code should be in a GitHub repository.
3. **Domain Name**: A registered domain name for the web chatbot.
4. **SSL Certificate**: An SSL certificate for your domain in AWS Certificate Manager.
5. **Slack App**: A configured Slack app with appropriate tokens.

## 🔧 Step 1: Set Up Required AWS Resources

### 🔐 1.1 Create SSL Certificate (for Chatbot only)

1. Go to AWS Certificate Manager (ACM).
2. Request a new certificate for your domain (e.g., `chatbot.yourdomain.com`).
3. Follow the validation process (typically DNS validation).
4. Note the ARN of the certificate for later use.

### 🌐 1.2 Set Up Route 53 Hosted Zone (for Chatbot only)

1. Go to Route 53 console.
2. Create a hosted zone for your domain if you don't have one already.
3. Make sure your domain's DNS is properly configured to use Route 53 nameservers.

## 🔑 Step 2: Configure GitHub Secrets

Add the following secrets to your GitHub repository:

### ✅ Required Secrets:

1. `AWS_ACCESS_KEY_ID`: Your AWS access key
2. `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
3. `AWS_REGION`: The AWS region (e.g., `us-east-1`)
4. `DOMAIN_NAME`: Your domain name (for chatbot)
5. `CERTIFICATE_ARN`: The ARN of your SSL certificate (for chatbot)
6. `SLACK_BOT_TOKEN`: Your Slack Bot Token (for slackbot)
7. `SLACK_APP_TOKEN`: Your Slack App Token (for slackbot)

### ⚙️ Optional Secrets (defaults will be used if not provided):

8. `ECR_REPOSITORY`: Name of the chatbot ECR repository (default: `unity-chatbot`)
9. `SLACKBOT_ECR_REPOSITORY`: Name of the slackbot ECR repository (default: `unity-slackbot`)
10. `KNOWLEDGE_BASE_ID`: Your AWS Bedrock Knowledge Base ID
11. `S3_BUCKET_NAME`: Your S3 bucket name
12. `S3_FOLDER_PREFIX`: Your S3 folder prefix
13. `UNITY_USERNAME`: Username for Unity authentication
14. `UNITY_PASSWORD`: Password for Unity authentication

To add these secrets:

1. Go to your GitHub repository
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret" and add each secret

## 🚀 Step 3: Deploy Your Applications

Simply push your code to the `main` branch:

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

The GitHub Actions workflows will automatically:

1. Build Docker images for both applications
2. Push the images to Amazon ECR
3. Create the CloudFormation stacks if they don't exist
4. Update the stacks if they already exist
5. Deploy both applications to ECS

## ✅ Step 4: Verify Deployments

### 🌐 Chatbot Verification

1. Wait for the GitHub Actions workflows to complete (check the "Actions" tab in your repository).
2. Visit your domain (e.g., `https://chatbot.yourdomain.com`) to verify that the chatbot is running.

### 💬 Slackbot Verification

1. Check that the Slackbot is online in your Slack workspace.
2. Send a message to the bot to verify it responds.
3. Check CloudWatch logs if the bot is not responding.

## 🔧 Troubleshooting

### ⚠️ Common Issues:

1. **Deployment Fails**: Check the GitHub Actions logs for specific error messages.
2. **Chatbot Not Accessible**: Verify that the ECS service is running and the load balancer health checks are passing.
3. **Slackbot Not Responding**: Check the CloudWatch logs for the Slackbot service.
4. **SSL Certificate Issues**: Make sure the certificate is validated and in the same region as your resources.

### 💻 Useful Commands:

```bash
# Check Chatbot ECS service status
aws ecs describe-services --cluster unity-chatbot-cluster --services unity-chatbot-service

# Check Slackbot ECS service status
aws ecs describe-services --cluster unity-slackbot-cluster --services unity-slackbot-service

# View Chatbot CloudWatch logs
aws logs get-log-events --log-group-name /ecs/unity-chatbot --log-stream-name <log-stream-name>

# View Slackbot CloudWatch logs
aws logs get-log-events --log-group-name /ecs/unity-slackbot --log-stream-name <log-stream-name>
```

## 🔄 Updating the Applications

To update either application, simply push changes to the `main` branch. The CI/CD pipelines will automatically build and deploy the new versions.

You can also manually trigger either workflow from the "Actions" tab in your GitHub repository.

## 🧹 Cleaning Up

To remove all resources:

1. Delete the CloudFormation stacks:
   ```bash
   aws cloudformation delete-stack --stack-name unity-chatbot-stack
   aws cloudformation delete-stack --stack-name unity-slackbot-stack
   ```
2. Delete any manually created resources not managed by CloudFormation.