# AWS Cloud Deployment & Operations Guide

**Project:** Serverless Chatbot with MLOps Pipeline  
**Student:** Dhanush S (Registration Number: 23MIS0224)  
**Institution:** Vellore Institute of Technology (VIT)  
**Course:** Agile Development Process and DevOps (Prof. Arun Kumar)  

---

## 1. Prerequisites

Before starting the AWS deployment, ensure you have:
1. An active [AWS Account](https://aws.amazon.com/free/) (Free Tier is fully sufficient).
2. [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed on Windows or Linux.
3. Python 3.10 or 3.11 installed.
4. Git installed.
5. (Optional) Free Groq API Key from [console.groq.com](https://console.groq.com/).

---

## 2. Step-by-Step AWS Provisioning

### Step 1: Configure AWS CLI Credentials
Open PowerShell and authenticate your AWS CLI:
```powershell
aws configure
```
Provide:
- **AWS Access Key ID:** `[Your Access Key]`
- **AWS Secret Access Key:** `[Your Secret Access Key]`
- **Default region name:** `us-east-1`
- **Default output format:** `json`

Verify authentication:
```powershell
aws sts get-caller-identity
```

---

### Step 2: Create Amazon S3 Artifacts Bucket
Create a private S3 bucket to store benchmark evaluation datasets and MLOps reports:
```powershell
$BUCKET_NAME = "vit-study-assistant-artifacts-23mis0224"

# Create bucket
aws s3api create-bucket --bucket $BUCKET_NAME --region us-east-1

# Enable Server-Side Encryption (AES256)
aws s3api put-bucket-encryption `
  --bucket $BUCKET_NAME `
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# Block all public access for security
aws s3api put-public-access-block `
  --bucket $BUCKET_NAME `
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

Upload initial evaluation dataset to S3:
```powershell
aws s3 cp data/evaluation_dataset.json s3://$BUCKET_NAME/datasets/evaluation_dataset.json
```

---

### Step 3: Create Amazon DynamoDB Table
Create the NoSQL table `StudyAssistantRecords` with Partition Key (`PK`) and Sort Key (`SK`):
```powershell
aws dynamodb create-table `
    --table-name StudyAssistantRecords `
    --attribute-definitions `
        AttributeName=PK,AttributeType=S `
        AttributeName=SK,AttributeType=S `
    --key-schema `
        AttributeName=PK,KeyType=HASH `
        AttributeName=SK,KeyType=RANGE `
    --billing-mode PAY_PER_REQUEST `
    --region us-east-1
```
Verify creation:
```powershell
aws dynamodb describe-table --table-name StudyAssistantRecords --query "Table.TableStatus"
```
*(Expected output: `"ACTIVE"`)*

---

### Step 4: Create Least-Privilege IAM Role for AWS Lambda

1. Create a trust policy file `trust-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

2. Create the IAM Execution Role:
```powershell
aws iam create-role `
    --role-name StudyAssistantLambdaRole `
    --assume-role-policy-document file://trust-policy.json
```

3. Attach basic Lambda CloudWatch execution policy:
```powershell
aws iam attach-role-policy `
    --role-name StudyAssistantLambdaRole `
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

4. Create an inline policy for DynamoDB and S3 access `lambda-permissions.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDBTableAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:*:table/StudyAssistantRecords"
    },
    {
      "Sid": "S3ArtifactsBucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::vit-study-assistant-artifacts-23mis0224/*"
    }
  ]
}
```

5. Attach the inline permissions:
```powershell
aws iam put-role-policy `
    --role-name StudyAssistantLambdaRole `
    --policy-name StudyAssistantResourcePolicy `
    --policy-document file://lambda-permissions.json
```

---

### Step 5: Package and Deploy AWS Lambda Function

1. Package Python dependencies into a deployment zip:
```powershell
# Create temporary build folder
New-Item -ItemType Directory -Force -Path build_package
pip install -r requirements.txt --target build_package/
Copy-Item -Recurse app build_package/
Copy-Item -Recurse data build_package/

# Compress package
Compress-Archive -Path build_package/* -DestinationPath lambda_deployment.zip -Force
```

2. Deploy the Lambda function:
```powershell
$ROLE_ARN = (aws iam get-role --role-name StudyAssistantLambdaRole --query "Role.Arn" --output text)

aws lambda create-function `
    --function-name StudyAssistantBackend `
    --runtime python3.10 `
    --role $ROLE_ARN `
    --handler app.lambda_handler.lambda_handler `
    --zip-file fileb://lambda_deployment.zip `
    --timeout 20 `
    --memory-size 512 `
    --environment "Variables={APP_ENV=cloud,AWS_STORAGE_ENABLED=true,S3_ARTIFACTS_ENABLED=true,AWS_REGION=us-east-1,AWS_DYNAMODB_TABLE=StudyAssistantRecords,AWS_S3_BUCKET=vit-study-assistant-artifacts-23mis0224,GROQ_MODEL=llama-3.3-70b-versatile}" `
    --region us-east-1
```

---

### Step 6: Create Amazon API Gateway (HTTP API v2)

1. Create the HTTP API:
```powershell
$API_ID = (aws apigatewayv2 create-api `
    --name "StudyAssistantAPI" `
    --protocol-type HTTP `
    --cors-configuration "AllowOrigins='*',AllowMethods='GET,POST,OPTIONS',AllowHeaders='*'" `
    --query "ApiId" --output text)
```

2. Create Lambda integration:
```powershell
$LAMBDA_ARN = (aws lambda get-function --function-name StudyAssistantBackend --query "Configuration.FunctionArn" --output text)

$INTEGRATION_ID = (aws apigatewayv2 create-integration `
    --api-id $API_ID `
    --integration-type AWS_PROXY `
    --integration-uri $LAMBDA_ARN `
    --payload-format-version "2.0" `
    --query "IntegrationId" --output text)
```

3. Create the catch-all proxy route:
```powershell
aws apigatewayv2 create-route `
    --api-id $API_ID `
    --route-key '$default' `
    --target "integrations/$INTEGRATION_ID"
```

4. Grant API Gateway permission to invoke Lambda:
```powershell
aws lambda add-permission `
    --function-name StudyAssistantBackend `
    --statement-id "AllowAPIGatewayInvoke" `
    --action "lambda:InvokeFunction" `
    --principal "apigateway.amazonaws.com" `
    --source-arn "arn:aws:execute-api:us-east-1:*:$API_ID/*"
```

5. Retrieve your deployed Cloud API endpoint URL:
```powershell
$API_ENDPOINT = (aws apigatewayv2 get-api --api-id $API_ID --query "ApiEndpoint" --output text)
Write-Host "Deployed API Base URL: $API_ENDPOINT"
```

---

## 3. Cloud Verification & Testing

### Test 1: Verify Health Endpoint
```powershell
curl "$API_ENDPOINT/api/health"
```
*Expected response:*
```json
{
  "status": "healthy",
  "app_name": "Serverless Chatbot with MLOps Pipeline",
  "app_version": "1.0.0",
  "environment": "cloud",
  "storage_mode": "DynamoDB (Cloud)",
  "ai_provider": "Rule-Based Fallback",
  "model_identifier": "heuristic-academic-v1"
}
```

### Test 2: Verify Chat Endpoint
```powershell
curl -X POST "$API_ENDPOINT/api/chat" `
  -H "Content-Type: application/json" `
  -d '{"message": "What is AWS Lambda and serverless computing?"}'
```

### Test 3: Trigger MLOps Retraining Simulation
```powershell
curl -X POST "$API_ENDPOINT/api/mlops/retrain-simulation" `
  -H "Content-Type: application/json" `
  -d '{"trigger_reason": "Cloud verification run"}'
```

---

## 4. Verifying AWS Console Evidence

1. **Amazon DynamoDB:**
   - Open AWS Console -> DynamoDB -> Tables -> `StudyAssistantRecords` -> Explore Table Items.
   - You will see partition keys `CONVERSATION#conv-...` and `RETRAIN_RUN`.
2. **Amazon S3:**
   - Open AWS Console -> Amazon S3 -> Buckets -> `vit-study-assistant-artifacts-23mis0224`.
   - Inspect folder `mlops-reports/` containing the generated `.json` and `.md` reports.
3. **Amazon CloudWatch:**
   - Open AWS Console -> CloudWatch -> Log Groups -> `/aws/lambda/StudyAssistantBackend`.
   - View invocation logs, duration, memory used, and structured `METRICS_EVENT` records.

---

## 5. Teardown & Resource Cleanup

To ensure no ongoing charges occur after evaluation, delete the cloud resources:
```powershell
# Delete API Gateway
aws apigatewayv2 delete-api --api-id $API_ID

# Delete Lambda Function
aws lambda delete-function --function-name StudyAssistantBackend

# Delete DynamoDB Table
aws dynamodb delete-table --table-name StudyAssistantRecords

# Empty and Delete S3 Bucket
aws s3 rm s3://$BUCKET_NAME --recursive
aws s3api delete-bucket --bucket $BUCKET_NAME

# Delete IAM Role
aws iam delete-role-policy --role-name StudyAssistantLambdaRole --policy-name StudyAssistantResourcePolicy
aws iam detach-role-policy --role-name StudyAssistantLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name StudyAssistantLambdaRole
```
All cloud infrastructure is now cleanly decommissioned.
