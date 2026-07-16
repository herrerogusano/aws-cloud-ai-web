# AWS Resource Inventory

Status: frontend and backend resources updated in `eu-west-1` for Phase 7.

## Current Inventory

| Resource Type | Identifier | Status | Notes |
| --- | --- | --- | --- |
| CloudFormation stack | `aws-cloud-ai-web-backend` | Created | IaC entry point for backend and frontend infrastructure |
| S3 website bucket | `aws-cloud-ai-web-herrerogusano-frontend` | Created | Public static website bucket for frontend assets |
| S3 bucket policy | Attached to frontend bucket | Created | Public read of frontend objects only |
| Lambda function | `aws-cloud-ai-web-backend-handler` | Created | Calls Amazon Bedrock and returns generated answers |
| Lambda Function URL | Environment-specific URL | Created | Public unauthenticated backend endpoint |
| IAM execution role | Auto-created by SAM/CloudFormation | Created | Used for Lambda execution, CloudWatch logging, and scoped Bedrock invocation |
| CloudWatch log group | `/aws/lambda/aws-cloud-ai-web-backend-handler` | Created | 7-day retention configured |
| SAM managed artifact bucket | `aws-sam-cli-managed-default-samclisourcebucket-tptpcw2u9y7f` | Already present / used | Managed by SAM for deployment artifacts |

## Resource Notes

### CloudFormation stack

- Region: `eu-west-1`
- Created through IaC: yes
- Persistent data: no
- Removal: `sam delete --stack-name aws-cloud-ai-web-backend --region eu-west-1`

### S3 website bucket

- Region: `eu-west-1`
- Created through IaC: yes
- Public data: yes
- Website URL:
  - `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`
- Website configuration:
  - `IndexDocument: index.html`
- Public access model:
  - bucket policy grants `s3:GetObject` on bucket objects
  - public write is not allowed
  - public ACLs remain blocked/ignored
- Cost considerations:
  - low for light usage, but storage and request charges still apply

### S3 bucket policy

- Region: `eu-west-1`
- Created through IaC: yes
- Purpose: allow public read of frontend objects only
- Public write: no

### Lambda function

- Region: `eu-west-1`
- Created through IaC: yes
- Persistent data: no
- Timeout: `20` seconds
- Memory size: `128` MB
- Environment variables:
  - `BEDROCK_MODEL_ID`
  - `BEDROCK_MAX_TOKENS`
  - `BEDROCK_TEMPERATURE`
- Cost considerations:
  - low for light usage, but invocations and Bedrock inference both consume billable usage beyond applicable allowances

### Lambda Function URL

- Region: `eu-west-1`
- Created through IaC: yes
- Authentication: none in this educational phase
- CORS origins:
  - `http://localhost:8000`
  - `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`

### IAM execution role

- Region: `eu-west-1`
- Created through IaC: yes
- Purpose:
  - basic Lambda execution
  - CloudWatch logging
  - `bedrock:GetInferenceProfile` on the selected inference profile ARN
  - `bedrock:InvokeModel` on the selected inference profile ARN
  - `bedrock:InvokeModel` on the linked `amazon.nova-micro-v1:0` foundation-model ARNs with an inference-profile condition

### CloudWatch log group

- Region: `eu-west-1`
- Created through IaC: yes
- Retention: 7 days

### SAM managed artifact bucket

- Region: `eu-west-1`
- Created through IaC: managed automatically by SAM
- Persistent data: stores deployment artifacts

## What Phase 7 Changed

- added the S3 static website bucket
- added the S3 bucket policy for public object reads
- updated Function URL CORS origins for the public website and localhost development
- synchronized public frontend assets to the S3 bucket

## What Phase 7 Did Not Create

- No new CloudFormation stack
- No CloudFront distribution
- No Route 53 resources
- No API Gateway
- No database
- No new Bedrock resources
