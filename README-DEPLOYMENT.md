# Deploying Unity Chatbot to AWS with Custom Domain

This guide explains how to deploy the Unity Chatbot application to AWS using the CI/CD pipeline set up with GitHub Actions.

## Prerequisites

1. **AWS Account**: You need an AWS account with appropriate permissions.
2. **GitHub Repository**: Your code should be in a GitHub repository.
3. **Domain Name**: A registered domain name that you want to use for your application.
4. **SSL Certificate**: An SSL certificate for your domain in AWS Certificate Manager.

## Step 1: Set Up Required AWS Resources

### 1.1 Create SSL Certificate

1. Go to AWS Certificate Manager (ACM).
2. Request a new certificate for your domain (e.g., `chatbot.yourdomain.com`).
3. Follow the validation process (typically DNS validation).
4. Note the ARN of the certificate for later use.

### 1.2 Set Up Route 53 Hosted Zone

1. Go to Route 53 console.
2. Create a hosted zone for your domain if you don't have one already.
3. Make sure your domain's DNS is properly configured to use Route 53 nameservers.

## Step 2: Configure GitHub Secrets

Add the following secrets to your GitHub repository:

### Required Secrets:
1. `AWS_ACCESS_KEY_ID`: Your AWS access key
2. `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
3. `AWS_REGION`: The AWS region (e.g., `us-east-1`)
4. `DOMAIN_NAME`: Your domain name
5. `CERTIFICATE_ARN`: The ARN of your SSL certificate

### Optional Secrets (defaults will be used if not provided):
6. `ECR_REPOSITORY`: Name of the ECR repository (default: `unity-chatbot`)
7. `ECS_CLUSTER`: Name of the ECS cluster (default: `unity-chatbot-cluster`)
8. `ECS_SERVICE`: Name of the ECS service (default: `unity-chatbot-service`)
9. `KNOWLEDGE_BASE_ID`: Your AWS Bedrock Knowledge Base ID
10. `S3_BUCKET_NAME`: Your S3 bucket name
11. `S3_FOLDER_PREFIX`: Your S3 folder prefix
12. `UNITY_USERNAME`: Username for Unity authentication
13. `UNITY_PASSWORD`: Password for Unity authentication
14. `SLACK_BOT_TOKEN`: Your Slack Bot Token (if using Slack)
15. `SLACK_APP_TOKEN`: Your Slack App Token (if using Slack)

To add these secrets:
1. Go to your GitHub repository
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret" and add each secret

## Step 3: Deploy Your Application

Simply push your code to the `main` branch:

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

The GitHub Actions workflow will automatically:
1. Build a Docker image of your application
2. Push the image to Amazon ECR
3. Create the CloudFormation stack if it doesn't exist
4. Update the stack if it already exists
5. Deploy the application to ECS

## Step 4: Verify Deployment

1. Wait for the GitHub Actions workflow to complete (check the "Actions" tab in your repository).
2. Visit your domain (e.g., `https://chatbot.yourdomain.com`) to verify that the application is running.
3. Check the CloudWatch logs if you encounter any issues.

## Troubleshooting

### Common Issues:

1. **Deployment Fails**: Check the GitHub Actions logs for specific error messages.
2. **Application Not Accessible**: Verify that the ECS service is running and the load balancer health checks are passing.
3. **SSL Certificate Issues**: Make sure the certificate is validated and in the same region as your resources.

### Useful Commands:

```bash
# Check ECS service status
aws ecs describe-services --cluster unity-chatbot-cluster --services unity-chatbot-service

# View CloudWatch logs
aws logs get-log-events --log-group-name /ecs/unity-chatbot --log-stream-name <log-stream-name>
```

## Updating the Application

To update the application, simply push changes to the `main` branch. The CI/CD pipeline will automatically build and deploy the new version.

## Cleaning Up

To remove all resources:

1. Delete the CloudFormation stack:
   ```bash
   aws cloudformation delete-stack --stack-name unity-chatbot-stack
   ```
2. Delete any manually created resources not managed by CloudFormation.