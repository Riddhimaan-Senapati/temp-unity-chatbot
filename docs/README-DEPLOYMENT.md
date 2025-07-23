# 🚀 Lambda Deployment Guide

This guide explains how to deploy the Unity Slack Bot and automated scraper Lambda functions to AWS using GitHub Actions.

## 📋 Table of Contents

- [🏗️ Architecture Overview](#️-architecture-overview)
- [🔧 Prerequisites](#-prerequisites)
- [🔑 Step 1: Configure GitHub Secrets](#-step-1-configure-github-secrets)
- [🚀 Step 2: Deploy Lambda Functions](#-step-2-deploy-lambda-functions)
- [✅ Step 3: Verify Deployments](#-step-3-verify-deployments)
- [📅 Customizing Scraper Schedules](#-customizing-scraper-schedules)
- [🔧 Troubleshooting](#-troubleshooting)
- [🔄 Updating Lambda Functions](#-updating-lambda-functions)
- [🧹 Cleaning Up](#-cleaning-up)

## 🏗️ Architecture Overview

This serverless architecture consists of:

1. **Unity Slack Lambda Bot** - Main Slack bot that responds to user messages via API Gateway
2. **Documentation Scraper Lambda** - Automatically scrapes documentation websites via EventBridge scheduling
3. **Slack Conversation Scraper Lambda** - Automatically scrapes Slack conversations via EventBridge scheduling
4. **Contextual Retrieval Lambda** - Enhances document chunks for better retrieval (used by Knowledge Base)
5. **Metadata Filtering Lambda** - Generates metadata for documents (triggered by S3 events)

### 📅 EventBridge Scheduling

The scraper Lambda functions use **AWS EventBridge** (formerly CloudWatch Events) for automated scheduling:

- **Default Schedule**: Both scrapers run weekly on **Sundays at 12:00 PM EDT/11:00 AM EST** (16:00 UTC)
- **Cron Expression**: `cron(0 16 ? * SUN *)`
- **Timezone**: UTC (automatically adjusts for daylight saving time)
- **EventBridge Rules**: Each scraper has its own EventBridge rule that triggers the Lambda function

### 🔄 How EventBridge Works

1. **EventBridge Rule** is created with a cron schedule expression
2. **Rule triggers** the Lambda function at the specified time
3. **Lambda function executes** the scraping logic
4. **Results are stored** in S3 for the Knowledge Base to process
5. **CloudWatch logs** capture execution details and any errors

All Lambda functions are deployed using GitHub Actions workflows and CloudFormation templates.

## 🔧 Prerequisites

Before you begin, make sure you have:

1. **AWS Account** with appropriate permissions for Lambda, API Gateway, S3, Bedrock, EventBridge, and CloudFormation
2. **GitHub Repository** with this codebase
3. **Slack App** configured with proper permissions (see [SLACK-SETUP.md](SLACK-SETUP.md))
4. **AWS Bedrock Knowledge Base** set up (see [KNOWLEDGE-BASE-SETUP.md](KNOWLEDGE-BASE-SETUP.md))
5. **S3 Bucket** for storing scraped content and knowledge base data

## 🔑 Step 1: Configure GitHub Secrets

Add the following secrets to your GitHub repository:

### ✅ Required Secrets:

1. `AWS_ACCESS_KEY_ID`: Your AWS access key
2. `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
3. `AWS_REGION`: The AWS region (e.g., `us-east-1`)
4. `SLACK_BOT_TOKEN`: Your Slack Bot Token (starts with `xoxb-`)
5. `SLACK_SIGNING_SECRET`: Your Slack Signing Secret for request verification
6. `KNOWLEDGE_BASE_ID`: Your AWS Bedrock Knowledge Base ID
7. `S3_BUCKET_NAME`: Your S3 bucket name for storing scraped content
8. `SCRAPPER_SLACK_BOT_TOKEN`: Slack Bot Token for the scraper (can be same as SLACK_BOT_TOKEN)

### ⚙️ Optional Secrets (defaults will be used if not provided):

9. `S3_FOLDER_PREFIX`: Your S3 folder prefix (default: empty)
10. `UNITY_USERNAME`: Username for Unity authentication (if needed)
11. `UNITY_PASSWORD`: Password for Unity authentication (if needed)

### 🔧 How to Add Secrets:

1. Go to your GitHub repository
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret" and add each secret

## 🚀 Step 2: Deploy Lambda Functions

Deploy the Lambda functions using GitHub Actions workflows. You can deploy them individually or trigger all deployments by pushing to the main branch.

### 🤖 Deploy Slack Lambda Bot

This is the main Slack bot that users interact with:

```bash
# Trigger deployment by pushing changes to main branch
git add .
git commit -m "Deploy Slack Lambda Bot"
git push origin main
```

Or manually trigger the workflow:

1. Go to "Actions" tab in your GitHub repository
2. Select "Deploy Unity Slack Lambda Bot"
3. Click "Run workflow"

**Important**: After deployment, the workflow will output the API Gateway endpoint URL that you need to configure in your Slack app. Look for the "API Gateway Endpoint" in the deployment output.

### 📚 Deploy Documentation Scraper

This Lambda function scrapes documentation websites on a schedule:

```bash
# Trigger deployment by modifying files in lambdas/documentation_scraper/
git add lambdas/documentation_scraper/
git commit -m "Update documentation scraper"
git push origin main
```

Or manually trigger the workflow:

1. Go to "Actions" tab
2. Select "Deploy Documentation Scraper Lambda"
3. Click "Run workflow"

### 💬 Deploy Slack Conversation Scraper

This Lambda function scrapes Slack conversations on a schedule:

```bash
# Trigger deployment by modifying files in lambdas/slack_scraper/
git add lambdas/slack_scraper/
git commit -m "Update Slack scraper"
git push origin main
```

Or manually trigger the workflow:

1. Go to "Actions" tab
2. Select "Deploy Slack Scraper Lambda"
3. Click "Run workflow"

## ✅ Step 3: Verify Deployments

### 🤖 Verify Slack Bot Deployment

1. **Check GitHub Actions**: Ensure the deployment workflow completed successfully
2. **Check AWS Lambda**: Verify the `unity-slack-lambda` function exists in AWS Console
3. **Check API Gateway**: Verify the API Gateway endpoint is created
4. **Configure Slack App**:
   - **Get the API Gateway endpoint** from the deployment output
   - **Update your Slack app** with the endpoint URL following the [Slack Setup Guide](SLACK-SETUP.md#step-3-configure-event-subscriptions)
   - **Set Request URL** to: `https://your-api-gateway-id.execute-api.region.amazonaws.com/prod/slack`
5. **Test in Slack**:
   - Mention the bot in a channel: `@YourBotName hello`
   - Send a direct message to the bot
   - Check for responses

**Important**: The Slack bot won't respond until you configure the API Gateway endpoint in your Slack app's Event Subscriptions settings.

### 📚 Verify Documentation Scraper

1. **Check Lambda Function**: Verify `unity-documentation-scraper` exists
2. **Check EventBridge Rule**: Verify the weekly schedule is configured
3. **Check S3 Bucket**: Look for scraped documentation files
4. **Test Manually**: Invoke the function manually from AWS Console

### 💬 Verify Slack Conversation Scraper

1. **Check Lambda Function**: Verify `unity-slack-scraper` exists
2. **Check EventBridge Rule**: Verify the weekly schedule is configured
3. **Check S3 Bucket**: Look for scraped Slack conversation files
4. **Test Manually**: Invoke the function manually from AWS Console

### 📊 Monitor with CloudWatch

Check CloudWatch logs for each Lambda function:

- `/aws/lambda/unity-slack-lambda`
- `/aws/lambda/unity-documentation-scraper`
- `/aws/lambda/unity-slack-scraper`

## 📅 Customizing Scraper Schedules

You can customize when the scraper Lambda functions run by modifying the EventBridge cron expressions in the CloudFormation templates.

### 🕐 Understanding Cron Expressions

EventBridge uses cron expressions with 6 fields:

```
cron(Minutes Hours Day-of-month Month Day-of-week Year)
```

**Current default**: `cron(0 16 ? * SUN *)` = Sundays at 16:00 UTC (12:00 PM EDT/11:00 AM EST)

### 📝 Common Schedule Examples

| Schedule                | Cron Expression            | Description                             |
| ----------------------- | -------------------------- | --------------------------------------- |
| Daily at 2 AM UTC       | `cron(0 2 * * ? *)`        | Every day at 2:00 AM UTC                |
| Weekdays at 9 AM UTC    | `cron(0 9 ? * MON-FRI *)`  | Monday-Friday at 9:00 AM UTC            |
| Twice weekly (Wed, Sun) | `cron(0 14 ? * WED,SUN *)` | Wednesday and Sunday at 2:00 PM UTC     |
| Monthly (1st day)       | `cron(0 10 1 * ? *)`       | First day of each month at 10:00 AM UTC |
| Every 6 hours           | `cron(0 */6 * * ? *)`      | Every 6 hours starting at midnight UTC  |

### 🔧 How to Change Schedules

#### Method 1: Update GitHub Actions Workflows (Recommended)

The GitHub Actions workflows pass the schedule expression to CloudFormation, so you should update them first:

1. **Edit the GitHub Actions workflow**:

   - For Documentation Scraper: `.github/workflows/deploy-documentation-scraper.yml`
   - For Slack Scraper: `.github/workflows/deploy-slack-scraper.yml`

2. **Find the ScheduleExpression parameter**:

   ```yaml
   aws cloudformation deploy \
   --template-file cloudformation-templates/documentation-scraper-lambda.yml \
   --parameter-overrides \
   ScheduleExpression="cron(0 16 ? * SUN *)" \ # <-- Change this line
   ```

3. **Update the cron expression**:

   ```yaml
   ScheduleExpression="cron(0 9 ? * MON-FRI *)" \ # Daily weekdays at 9 AM UTC
   ```

4. **Deploy the changes**:
   ```bash
   git add .github/workflows/
   git commit -m "Update scraper schedule to weekdays at 9 AM UTC"
   git push origin main
   ```

#### Method 2: Modify CloudFormation Templates

1. **Edit the CloudFormation template**:

   - For Documentation Scraper: `cloudformation-templates/documentation-scraper-lambda.yml`
   - For Slack Scraper: `cloudformation-templates/slack-scraper-lambda.yml`

2. **Find the EventBridge rule section**:

   ```yaml
   DocumentationScraperScheduleRule:
     Type: AWS::Events::Rule
     Properties:
       ScheduleExpression: "cron(0 16 ? * SUN *)" # <-- Change this line
   ```

3. **Update the cron expression**:

   ```yaml
   ScheduleExpression: "cron(0 9 ? * MON-FRI *)" # Daily weekdays at 9 AM UTC
   ```

4. **Also update the GitHub Actions workflow** to match (see Method 1)

5. **Deploy the changes**:
   ```bash
   git add cloudformation-templates/ .github/workflows/
   git commit -m "Update scraper schedule"
   git push origin main
   ```

#### Method 3: Update via AWS Console (Temporary)

**Note**: Changes made via console will be overwritten on next deployment.

1. **Go to EventBridge Console**
2. **Navigate to "Rules"**
3. **Find your rule** (e.g., `unity-documentation-scraper-schedule`)
4. **Click "Edit"**
5. **Update the schedule expression**
6. **Save changes**

### ⚠️ Important Scheduling Considerations

1. **UTC Timezone**: All cron expressions are in UTC
2. **Daylight Saving**: UTC doesn't observe daylight saving time
3. **Lambda Timeout**: Ensure your Lambda timeout is sufficient for scraping operations
4. **Rate Limits**: Don't schedule too frequently to avoid hitting API rate limits
5. **S3 Costs**: More frequent scraping = more S3 storage costs
6. **Knowledge Base Sync**: Consider how often you want to sync new content to your Knowledge Base

### 🔍 Monitoring Scheduled Executions

```bash
# Check EventBridge rule status
aws events describe-rule --name unity-documentation-scraper-schedule

# View recent Lambda invocations
aws logs filter-log-events \
  --log-group-name /aws/lambda/unity-documentation-scraper \
  --start-time $(date -d '1 day ago' +%s)000

# Check next scheduled execution
aws events list-targets-by-rule --rule unity-documentation-scraper-schedule
```

## 🔧 Troubleshooting

### ⚠️ Common Issues:

1. **Slack Bot Not Responding**:

   - Check CloudWatch logs for errors
   - Verify Slack app configuration and permissions
   - Ensure API Gateway endpoint is configured in Slack app

2. **Lambda Deployment Fails**:

   - Check GitHub Actions logs for specific errors
   - Verify all required secrets are set
   - Check AWS permissions

3. **Scrapers Not Running on Schedule**:

   - Check EventBridge rules are enabled
   - Verify Lambda function permissions
   - Check S3 bucket permissions
   - Ensure cron expression is valid

4. **EventBridge Rule Issues**:

   - Verify the rule is enabled in EventBridge console
   - Check the target Lambda function is correctly configured
   - Ensure the Lambda function has permission to be invoked by EventBridge

5. **Knowledge Base Integration Issues**:
   - Verify Knowledge Base ID is correct
   - Check IAM permissions for Bedrock access
   - Ensure S3 bucket is properly configured

### 💻 Useful Commands:

```bash
# Check Lambda function status
aws lambda get-function --function-name unity-slack-lambda

# View recent CloudWatch logs
aws logs tail /aws/lambda/unity-slack-lambda --follow

# Test Lambda function manually
aws lambda invoke --function-name unity-slack-lambda --payload '{}' response.json

# Check API Gateway endpoint
aws apigateway get-rest-apis --query 'items[?name==`unity-slack-api`]'

# Check EventBridge rules
aws events list-rules --name-prefix unity

# Check EventBridge rule details
aws events describe-rule --name unity-documentation-scraper-schedule

# Manually trigger EventBridge rule
aws events put-events --entries Source=manual,DetailType=test,Detail='{}'
```

## 🔄 Updating Lambda Functions

To update any Lambda function:

1. **Make your changes** to the relevant files
2. **Commit and push** to the main branch
3. **GitHub Actions will automatically** detect changes and redeploy

### 🎯 Targeted Updates:

- **Slack Bot**: Modify files in `lambdas/slack_lambda/` or `utils/slackbot_helper.py`
- **Documentation Scraper**: Modify files in `lambdas/documentation_scraper/` or `utils/data_pipeline/`
- **Slack Scraper**: Modify files in `lambdas/slack_scraper/` or `slack_scripts/slack_scraper.py`
- **Schedules**: Modify CloudFormation templates in `cloudformation-templates/`

## 🧹 Cleaning Up

To remove all Lambda resources:

### 🗑️ Delete CloudFormation Stacks:

```bash
# Delete Slack Lambda Bot stack
aws cloudformation delete-stack --stack-name unity-slack-lambda-stack

# Delete Documentation Scraper stack
aws cloudformation delete-stack --stack-name unity-documentation-scraper-stack

# Delete Slack Scraper stack
aws cloudformation delete-stack --stack-name unity-slack-scraper-stack
```

### 🧽 Manual Cleanup:

1. **Lambda Layers**: Delete any created Lambda layers
2. **S3 Objects**: Clean up scraped content in S3 bucket
3. **CloudWatch Logs**: Delete log groups if desired
4. **API Gateway**: Verify API Gateway resources are removed
5. **EventBridge Rules**: Verify EventBridge rules are removed

### ⚠️ Important Notes:

- Deleting stacks will remove all associated resources including EventBridge rules
- S3 bucket contents are not automatically deleted
- Knowledge Base and its data will remain intact
- Slack app configuration will remain but won't receive events

---

## 📚 Additional Resources

- [Slack App Setup Guide](SLACK-SETUP.md)
- [Knowledge Base Setup Guide](KNOWLEDGE-BASE-SETUP.md)
- [Project Structure](structure.md)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [AWS EventBridge Documentation](https://docs.aws.amazon.com/eventbridge/)
- [EventBridge Cron Expressions](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html)
