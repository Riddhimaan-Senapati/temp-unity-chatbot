# 🧪 Local Testing Guide

This guide walks you through using the Unity RAG Chatbot local testing framework to evaluate chatbot performance, test different AI models.

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [📋 Prerequisites](#-prerequisites)
- [🔧 Setup and Configuration](#-setup-and-configuration)
- [📊 Test Data Structure](#-test-data-structure)
- [🚀 Running Tests](#-running-tests)
- [📈 Understanding Test Results](#-understanding-test-results)
- [💰 Cost Analysis](#-cost-analysis)
- [🔧 Troubleshooting](#-troubleshooting)

## 🎯 Overview

The local testing framework provides comprehensive evaluation capabilities for the Unity RAG Chatbot system, including:

- **Multi-Model Testing**: Test different AI models (currently Claude, Llama) with consistent datasets
- **Performance Metrics**: Measure response time, token usage, and cost per query
- **Response Quality**: Compare outputs against
- **System Prompt Validation**: Test with and without system prompts to evaluate guidance effectiveness
- **Automated Test Execution**: Run full test suites against predefined conversation threads
- **Detailed Reporting**: Generate comprehensive reports with metrics and analysis

### Testing Architecture

```
Test Data (JSON) → Automated Test Runner → Knowledge Base Retrieval → AI Model Processing → Results Analysis
                                     ↓
                          System Prompt (Optional) → Response Generation → Metrics Collection
                                     ↓
                              Cost Calculation → Performance Analysis → Report Generation
```

### Key Components

- **`automated_test.py`**: Main test runner for executing full database tests
- **`test_helper.py`**: Core testing functions and system prompt definitions
- **`test_data/`**: Contains question datasets and ground truth responses
- **`test_results/`**: Generated test reports and analysis files

## 📋 Prerequisites

Before running local tests, ensure you have:

- [ ] **AWS Bedrock Access** with required model permissions
- [ ] **Knowledge Base Setup** completed and operational
- [ ] **Environment Variables** configured for AWS access
- [ ] **Python Dependencies** installed (boto3, langchain, etc.)
- [ ] **Valid AWS Credentials** with Bedrock and S3 permissions

### Required Environment Variables

Ensure your `.env` file contains:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Bedrock Knowledge Base
KNOWLEDGE_BASE_ID=your_knowledge_base_id
```

### Required AWS Permissions

Your AWS credentials need access to:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:Retrieve",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🔧 Setup and Configuration

### Step 1: Navigate to Testing Directory

```bash
cd local_testing
```

### Step 2: Verify Dependencies

Ensure all required Python packages are installed:

```bash
pip install boto3 langchain python-dotenv
```

### Step 3: Configure Test Parameters

The testing framework supports multiple AI models with different pricing tiers:

#### Available Models

You can add any model you want from AWS Bedrock Console. Current models are:

| Model Name | Model ID | Input Cost ($/1k tokens) | Output Cost ($/1k tokens) |
|------------|----------|--------------------------|---------------------------|
| claude-4-sonnet | `us.anthropic.claude-sonnet-4-20250514-v1:0` | $0.003 | $0.015 |
| llama-4-maverick | `us.meta.llama4-maverick-17b-instruct-v1:0` | $0.00024 | $0.00097 |

#### Test Configuration Options

- **Source Count**: Number of knowledge base sources to retrieve (default: 10)
- **Test Mode**: Full database test or individual thread testing
- **System Prompt**: Enable/disable system prompt for comparison testing

## 📊 Test Data Structure

### Question Data (`test_data/questions_data.json`)

Contains conversation threads for testing various scenarios:

```json
{
  "threads": [
    {
      "name": "Introduction",
      "messages": [
        "What is the Unity HPC?"
      ]
    },
    {
      "name": "GPU Issues",
      "messages": [
        "GPU error message...",
        "Follow-up question...",
        "Additional context..."
      ]
    }
  ]
}
```

### Ground Truth Data (`test_data/data_with_ground_truths.json`)

Contains expected responses for accuracy evaluation:

This file is not used in local testing but can be used in AWS Evaluations Service for RAG quality evaluations.

```json
{
  "conversationTurns": [
    {
      "prompt": {
        "content": [{"text": "What is the Unity HPC?"}]
      },
      "referenceResponses": [
        {
          "content": [{"text": "Expected response content..."}]
        }
      ]
    }
  ]
}
```

### Test Categories

The test dataset covers various support scenarios which are all taken from real questions from Unity's help-desk Slack channel for possible questions:

1. **Introduction & Overview**: Basic Unity information
2. **GPU Issues**: Hardware problems and troubleshooting
3. **CUDA Problems**: Environment and module configuration
4. **Memory Management**: Resource allocation and optimization
5. **Storage & Data**: File management and transfers
6. **Software Installation**: Application setup and containers
7. **Job Management**: SLURM configuration and debugging
8. **Access & Authentication**: Login and permission issues

## 🚀 Running Tests

### Full Database Test

Run comprehensive tests against all conversation threads:

```python
python automated_test.py

# Available commands:
# 1. Test claude-4-sonnet model
# 2. Test llama-4-maverick model  
# 3. Test specific conversation thread
# 4. List available models
# 5. Exit
```

**Example Full Test Execution:**

```python
# Run full database test with claude-4-sonnet
test_model_on_database("claude-4-sonnet", source_count=10)
```

### Individual Thread Testing on All Models

Test specific conversation thread:

```python
# Choose a thread to run over all models
compare_models("Tricky GPU error driver update problem", source_count=10)
```

### System Prompt Test Scenarios

Test with system prompt and without system prompt:

```python
# Choose a model and a thread to run with system prompt and without system prompt
test_model_with_without_system_prompt("claude-4-sonnet", "Unity basics", 10)
```

## 📈 Understanding Test Results

### Test Report Structure

Each test generates a comprehensive markdown and json report in `test_results/`:

We deleted the json reports since we didn't have the need to keep but it will generate json files after you run the tests.

```
test_results/
├── 10_full_database_test_claude-4-sonnet_20250730_135514.md
└── 10_full_database_test_llama-4-maverick_20250730_123411.md
```

### Report Sections

#### 1. Summary Metrics

```markdown
## Summary Metrics

- **Total Queries:** 54
- **Threads Processed:** 43
- **Total Response Time:** 479.960 seconds
- **Average Response Time:** 8.888 seconds
- **Total Input Tokens:** 384,966
- **Total Output Tokens:** 21,737
- **Total Cost:** $1.480953
```

#### 2. Thread-Level Analysis

```markdown
### Thread: Introduction

**Thread Summary:**
- Queries: 1
- Total Response Time: 6.740 seconds
- Average Response Time: 6.740 seconds
- Total Cost: $0.023934
- Average Tokens/Second: 930.86
```

#### 3. Individual Query Results

```markdown
#### Q1: What is the Unity HPC?

**Response:**
Unity is a collaborative, multi-institutional high-performance computing platform...

**Query Metrics:**
- Response Time: 6.740 seconds
- Input Tokens: 5,848
- Output Tokens: 426
- Total Tokens: 6,274
- Tokens/Second: 63.22
- Input Cost: $0.017544
```

### Performance Metrics

#### Response Time Analysis
- **Fast Response**: < 5 seconds
- **Moderate Response**: 5-15 seconds  
- **Slow Response**: > 15 seconds

#### Token Efficiency
- **Input Tokens**: Context + question length
- **Output Tokens**: Response length
- **Tokens/Second**: Processing speed indicator

#### Cost Efficiency
- **Per-Query Cost**: Individual query expense
- **Total Test Cost**: Complete test suite expense
- **Cost per Token**: Model pricing efficiency

### Quality Assessment

#### Citation Accuracy
- Verify inline citations `[[Source Number]](URL)` are properly formatted
- Check that cited sources are relevant to the response
- Ensure source URLs are accessible and correct

#### Response Relevance
- Compare responses against ground truth data
- Evaluate factual accuracy and completeness
- Assess tone and helpfulness

#### System Prompt Effectiveness
- Compare responses with and without system prompts
- Evaluate adherence to response guidelines
- Check for proper redirection handling

## 💰 Cost Analysis

### Cost Calculation

The testing framework automatically calculates costs based on input token and output token costs.

### Cost Optimization Strategies

#### Model Selection
- **Claude 4 Sonnet**: Higher quality, higher cost ($0.003-$0.015/1k tokens) - Around 30 questions per $1 in our case
- **Llama 4 Maverick**: Lower cost, good performance ($0.00024-$0.00097/1k tokens) - Around 560 questions per $1 in our case

#### Source Count Optimization
- **More Sources**: Better context, higher input token cost, slower response generation
- **Fewer Sources**: Lower cost, potentially reduced accuracy, faster response generation
- **Recommended**: Start with 5 sources, adjust based on quality needs, recommended amount is 5 to 20

#### Query Optimization
- **Focused Questions**: Reduce unnecessary context
- **Batch Testing**: Run comprehensive tests during development, not production

## 🔧 Troubleshooting

### Common Issues

#### 1. **AWS Authentication Errors**

**Symptoms**: `NoCredentialsError` or `AccessDenied` exceptions

**Solutions**:
- Verify `.env` file contains correct AWS credentials
- Check AWS CLI configuration: `aws configure list` or check IAM User AWS Access Key ID and AWS Secret Access Key
- Ensure credentials have Bedrock permissions
- Verify region matches Bedrock service availability

#### 2. **Knowledge Base Connection Issues**

**Symptoms**: `ValidationException` or empty retrieval results

**Solutions**:
- Verify `KNOWLEDGE_BASE_ID` in environment variables
- Check knowledge base is in the same region as your AWS credentials
- Ensure knowledge base has completed data ingestion
- Test knowledge base independently in AWS console

#### 3. **Model Access Denied**

**Symptoms**: `AccessDeniedException` when invoking models

**Solutions**:
- Request model access in AWS Bedrock console
- Wait for model access approval (24-48 hours)
- Verify you're in a supported region (us-east-1, us-west-2)
- Check IAM permissions include `bedrock:InvokeModel`

#### 4. **Import Errors**

**Symptoms**: `ModuleNotFoundError` for chatbot_helper or other modules

**Solutions**:
- Ensure you're running from the `local_testing` directory
- Verify parent directory is in Python path
- Check all required dependencies are installed
- Run `pip install -r requirements.txt` when available (We provided it in our repository.)

#### 5. **Test Data Loading Issues**

**Symptoms**: `FileNotFoundError` for test data files

**Solutions**:
- Verify test data files exist in `test_data/` directory
- Check file permissions and encoding (UTF-8)
- Ensure JSON files have valid syntax
- Verify working directory is `local_testing/`

### Performance Issues

#### Slow Response Times

**Causes & Solutions**:
- **Large Context**: Reduce source count or optimize retrieval
- **Model Latency**: Try different model or region
- **Network Issues**: Check internet connection and AWS service status

#### High Token Usage

**Optimization Strategies**:
- **Reduce Source Count**: Lower retrieval sources from 10 to 5-7
- **Optimize Questions**: Remove unnecessary context from test questions
- **System Prompt Length**: Minimize system prompt size while maintaining quality

#### Memory Issues

**Solutions**:
- **Batch Size**: Process fewer threads simultaneously
- **Clear Variables**: Explicitly delete large response objects
- **Restart Sessions**: Periodically restart Python session for long test runs

## 📊 Advanced Testing Scenarios

### A/B Testing

Compare different configurations:

```python
# Test different source counts
test_model_on_database("claude-4-sonnet", source_count=5)
test_model_on_database("claude-4-sonnet", source_count=10)
```

## 🔄 Next Steps

After completing local testing:

1. **Analyze Results**: Review test reports for performance insights
2. **Optimize Configuration**: Adjust source count, model selection based on results
3. **Update System Prompts**: Refine prompts based on response quality
4. **Production Deployment**: Apply tested configurations to production environment
5. **Continuous Testing**: Establish regular testing schedule for system validation

---

## 📚 Additional Resources

- [Chatbot Helper Functions](../utils/chatbot_helper.py)
- [System Prompt Configuration](../local_testing/test_helper.py)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [LangChain Integration Guide](https://docs.langchain.com/docs/integrations/llms/bedrock)

## 🔐 Testing Best Practices

### Security Considerations
- Store AWS credentials securely in `.env` files
- Never commit credentials to version control
- Use IAM roles with minimal required permissions
- Regularly rotate access keys

### Cost Management
- Monitor testing costs in AWS billing dashboard
- Set up billing alerts for unexpected usage
- Use cheaper models for development testing
- Optimize test data size for frequent testing

### Quality Assurance
- Maintain comprehensive test data covering edge cases
- Regular review and update of ground truth responses
- Document test scenarios and expected outcomes
- Establish quality thresholds for automated validation
