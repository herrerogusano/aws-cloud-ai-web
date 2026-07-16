# AWS Resource Inventory

Status: application resources remain deployed in `eu-west-1`, and GitHub Actions frontend deployment bootstrap resources were added on July 16, 2026.

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
| CloudFormation bootstrap stack | `aws-cloud-ai-web-github-frontend-bootstrap` | Created | Separate bootstrap stack for GitHub OIDC and frontend deployment IAM |
| GitHub OIDC provider | `arn:aws:iam::344774635844:oidc-provider/token.actions.githubusercontent.com` | Created | Shared AWS account-level identity provider for GitHub Actions |
| GitHub frontend deploy role | `aws-cloud-ai-web-github-frontend-deploy` | Created | Dedicated OIDC-assumed role for frontend-only S3 deployment |

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

### CloudFormation bootstrap stack

- Region: `eu-west-1`
- Created through IaC: yes, from `bootstrap/github-frontend-deploy-iam.yaml`
- Purpose:
  - provision GitHub Actions OIDC authentication resources outside the application stack
  - keep IAM bootstrap separate from normal frontend deployment

### GitHub OIDC provider

- Region scope: account-level IAM resource
- Created through IaC: yes, via the bootstrap stack
- Provider URL:
  - `https://token.actions.githubusercontent.com`
- Audience:
  - `sts.amazonaws.com`
- Reuse note:
  - this provider may be shared by future repositories in the same AWS account

### GitHub frontend deploy role

- Region scope: account-level IAM resource
- Created through IaC: yes, via the bootstrap stack
- Role name:
  - `aws-cloud-ai-web-github-frontend-deploy`
- Trust restriction:
  - `repo:herrerogusano/aws-cloud-ai-web:ref:refs/heads/main`
- Purpose:
  - allow GitHub Actions to validate and deploy frontend files to the existing S3 website bucket
- Granted permissions:
  - `s3:ListBucket`
  - `s3:GetBucketLocation`
  - `s3:PutObject`
  - `s3:DeleteObject`
- Explicitly not granted:
  - Lambda deployment
  - CloudFormation modification
  - IAM modification
  - Bedrock invocation

## What Phase 7 Changed

- added the S3 static website bucket
- added the S3 bucket policy for public object reads
- updated Function URL CORS origins for the public website and localhost development
- synchronized public frontend assets to the S3 bucket

## What Phase 8-9 Bootstrap Changed

- added a separate bootstrap stack for GitHub Actions OIDC and the frontend deployment role
- created the shared GitHub OIDC provider in the AWS account
- created a repository-specific `main`-branch deployment role for S3 frontend sync only
- configured GitHub repository variables for AWS region, frontend bucket, and deployment role ARN

## What Phase 7 Did Not Create

- No new CloudFormation stack
- No CloudFront distribution
- No Route 53 resources
- No API Gateway
- No database
- No new Bedrock resources
- No GitHub-stored permanent AWS access keys
- No backend deployment role for GitHub Actions yet
