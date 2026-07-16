# AWS Resource Inventory

This inventory records the AWS and GitHub-to-AWS deployment resources used by `aws-cloud-ai-web`.

Status checked on July 16, 2026:

- Application stack status: `UPDATE_COMPLETE`
- Bootstrap stack status: `UPDATE_COMPLETE`

## Resource Table

| Resource | Type | Purpose | Region or scope | Created by | Public | Stores data | Cost signal | Deletion path | Shared |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `aws-cloud-ai-web-backend` | CloudFormation stack | Main application stack | `eu-west-1` | AWS SAM | No | No | Low control-plane overhead | `sam delete` | No |
| `aws-cloud-ai-web-backend-handler` | Lambda function | Backend request handling and Bedrock invocation | `eu-west-1` | Application stack | Indirectly via Function URL | No | Lambda duration and requests | Stack deletion | No |
| Lambda Function URL | Lambda URL | Public backend entry point | `eu-west-1` | Application stack | Yes | No | Minimal by itself | Stack deletion | No |
| `/aws/lambda/aws-cloud-ai-web-backend-handler` | CloudWatch log group | Backend operational logs | `eu-west-1` | Application stack | No | Yes, transient logs | Log storage | Stack deletion | No |
| SAM-managed Lambda execution role | IAM role | Runtime permissions for Lambda and Bedrock | Account-level IAM | Application stack | No | No | No direct runtime cost | Stack deletion | No |
| `aws-cloud-ai-web-herrerogusano-frontend` | S3 bucket | Public static website hosting | `eu-west-1` | Application stack | Yes | Yes, static assets | S3 storage and requests | Stack deletion after bucket emptying | No |
| Frontend bucket policy | S3 bucket policy | Public read of frontend objects | `eu-west-1` | Application stack | Yes | No | None by itself | Stack deletion | No |
| S3 website configuration | S3 website hosting setting | Website endpoint for frontend | `eu-west-1` | Application stack | Yes | No | None by itself | Stack deletion | No |
| `aws-sam-cli-managed-default-samclisourcebucket-tptpcw2u9y7f` | S3 bucket | SAM deployment artifacts | `eu-west-1` | SAM managed | No | Yes, deployment artifacts | S3 storage and requests | Manual review | Potentially yes |
| `aws-cloud-ai-web-github-frontend-bootstrap` | CloudFormation stack | IAM bootstrap for GitHub OIDC deployment | `eu-west-1` | Manual bootstrap deployment | No | No | Low control-plane overhead | `aws cloudformation delete-stack` | No |
| `token.actions.githubusercontent.com` provider | IAM OIDC provider | GitHub Actions federation | Account-level IAM | Bootstrap stack | No | No | None by itself | Manual review | Yes |
| `aws-cloud-ai-web-github-backend-deploy` | IAM role | GitHub backend deployment orchestration | Account-level IAM | Bootstrap stack | No | No | None by itself | Bootstrap stack deletion | No |
| `aws-cloud-ai-web-cloudformation-execution` | IAM role | CloudFormation execution for application stack updates | Account-level IAM | Bootstrap stack | No | No | None by itself | Bootstrap stack deletion | No |
| `aws-cloud-ai-web-github-frontend-deploy` | IAM role | GitHub frontend file sync to S3 | Account-level IAM | Bootstrap stack | No | No | None by itself | Bootstrap stack deletion | No |

## Runtime Resources

### CloudFormation stack

- Name: `aws-cloud-ai-web-backend`
- Status observed: `UPDATE_COMPLETE`
- Purpose: manage the Lambda, Function URL, log group, frontend bucket, and related configuration

### Lambda function

- Name: `aws-cloud-ai-web-backend-handler`
- Runtime: `python3.13`
- Memory: `128 MB`
- Timeout: `20 seconds`
- Purpose: validate requests, call Bedrock, and return a controlled response

### Lambda Function URL

- Auth type: `NONE`
- Invoke mode: `BUFFERED`
- Allowed browser origins:
  - `http://localhost:8000`
  - `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`

### Lambda execution role

- Purpose:
  - CloudWatch logging
  - `bedrock:GetInferenceProfile` on the selected inference profile
  - `bedrock:InvokeModel` on the selected inference profile
  - `bedrock:InvokeModel` on the linked foundation-model ARNs with an inference-profile condition

### CloudWatch log group

- Name: `/aws/lambda/aws-cloud-ai-web-backend-handler`
- Retention: `7 days`

### Frontend S3 bucket

- Name: `aws-cloud-ai-web-herrerogusano-frontend`
- Website endpoint:
  - `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`
- Public access behavior:
  - Bucket policy makes object reads public
  - `BlockPublicAcls=true`
  - `IgnorePublicAcls=true`
  - `BlockPublicPolicy=false`
  - `RestrictPublicBuckets=false`
- Public note:
  - This bucket should contain only intentionally public assets

## Deployment Resources

### Bootstrap stack

- Name: `aws-cloud-ai-web-github-frontend-bootstrap`
- Status observed: `UPDATE_COMPLETE`
- Purpose: provision OIDC and repository-specific deployment roles outside the application stack

### GitHub OIDC provider

- Provider URL: `https://token.actions.githubusercontent.com`
- Audience: `sts.amazonaws.com`
- Shared note:
  - This is an account-level resource and may be reused by other repositories

### GitHub backend deploy role

- Name: `aws-cloud-ai-web-github-backend-deploy`
- Trust restriction:
  - `repo:herrerogusano/aws-cloud-ai-web:ref:refs/heads/main`
- Purpose:
  - Stack-scoped CloudFormation orchestration
  - SAM artifact upload
  - `iam:PassRole` to the CloudFormation execution role only

### CloudFormation execution role

- Name: `aws-cloud-ai-web-cloudformation-execution`
- Trust:
  - `cloudformation.amazonaws.com`
- Purpose:
  - Apply the application stack update with project-scoped permissions

### GitHub frontend deploy role

- Name: `aws-cloud-ai-web-github-frontend-deploy`
- Trust restriction:
  - `repo:herrerogusano/aws-cloud-ai-web:ref:refs/heads/main`
- Purpose:
  - Sync frontend files to the public bucket

## Confirmed Non-Resources

Checked on July 16, 2026 in `eu-west-1`:

- No EC2 instances
- No NAT gateways
- No RDS instances

Not created by this project:

- No API Gateway
- No CloudFront
- No Route 53
- No ECS services
- No database
- No separate Bedrock-managed resource created by the stack
