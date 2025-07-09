# API Gateway Setup for Unity Slack Lambda

## Manual Setup Steps (After Lambda Deployment)

1. **Create API Gateway REST API**:
   ```bash
   aws apigateway create-rest-api --name unity-slack-api --description "Unity Slack Bot API"
   ```

2. **Get the API ID and Root Resource ID**:
   ```bash
   API_ID=$(aws apigateway get-rest-apis --query "items[?name=='unity-slack-api'].id" --output text)
   ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query "items[?path=='/'].id" --output text)
   ```

3. **Create Resource for Slack Events**:
   ```bash
   aws apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID --path-part slack
   SLACK_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query "items[?pathPart=='slack'].id" --output text)
   ```

4. **Create POST Method**:
   ```bash
   aws apigateway put-method --rest-api-id $API_ID --resource-id $SLACK_RESOURCE_ID --http-method POST --authorization-type NONE
   ```

5. **Set Lambda Integration**:
   ```bash
   LAMBDA_ARN="arn:aws:lambda:us-east-1:ACCOUNT_ID:function:unity_slack_lambda"
   aws apigateway put-integration --rest-api-id $API_ID --resource-id $SLACK_RESOURCE_ID --http-method POST --type AWS_PROXY --integration-http-method POST --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations"
   ```

6. **Grant API Gateway Permission to Invoke Lambda**:
   ```bash
   aws lambda add-permission --function-name unity_slack_lambda --statement-id apigateway-invoke --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn "arn:aws:execute-api:us-east-1:ACCOUNT_ID:$API_ID/*/*"
   ```

7. **Deploy API**:
   ```bash
   aws apigateway create-deployment --rest-api-id $API_ID --stage-name prod
   ```

8. **Get API Endpoint**:
   ```bash
   echo "https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/slack"
   ```

## Benefits of API Gateway

- **Scalability**: Automatic scaling and throttling
- **Security**: Built-in DDoS protection and request validation
- **Monitoring**: CloudWatch metrics and logging
- **Caching**: Response caching capabilities
- **Rate Limiting**: Request throttling and quotas

## Slack Configuration

Use the API Gateway endpoint URL in your Slack app configuration:
- **Request URL**: `https://API_ID.execute-api.us-east-1.amazonaws.com/prod/slack`