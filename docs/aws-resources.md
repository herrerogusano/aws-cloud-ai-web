# AWS Resource Inventory

Status: backend resources updated in `eu-west-1` for Phase 6.

## Current Inventory

| Resource Type | Identifier | Status | Notes |
| --- | --- | --- | --- |
| CloudFormation stack | `aws-cloud-ai-web-backend` | Created | IaC entry point for backend resources |
| Lambda function | `aws-cloud-ai-web-backend-handler` | Created | Calls Amazon Bedrock and returns generated answers |
| Lambda Function URL | Environment-specific URL | Created | Public unauthenticated endpoint for this learning phase |
| IAM execution role | Auto-created by SAM/CloudFormation | Created | Used for Lambda execution, CloudWatch logging, and scoped Bedrock invocation |
| CloudWatch log group | `/aws/lambda/aws-cloud-ai-web-backend-handler` | Created | 7-day retention configured |
| SAM managed artifact bucket | `aws-sam-cli-managed-default-samclisourcebucket-tptpcw2u9y7f` | Already present / used | Managed by SAM for deployment artifacts |

## Resource Notes

### CloudFormation stack

- Region: `eu-west-1`
- Created through IaC: yes
- Persistent data: no
- Removal: `sam delete --stack-name aws-cloud-ai-web-backend --region eu-west-1`

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
- Cost considerations: low for light usage, but invocations and Bedrock inference both consume billable usage beyond applicable allowances

### Lambda Function URL

- Region: `eu-west-1`
- Created through IaC: yes
- Authentication: none in this educational phase
- Cost considerations: public exposure may increase invocation count if shared broadly

### IAM execution role

- Region: `eu-west-1`
- Created through IaC: yes
- Purpose:
  - basic Lambda execution
  - CloudWatch logging
  - `bedrock:GetInferenceProfile` on the selected inference profile ARN
  - `bedrock:InvokeModel` on the selected inference profile ARN
  - `bedrock:InvokeModel` on the linked `amazon.nova-micro-v1:0` foundation-model ARNs with an inference-profile condition
- Persistent data: no

### CloudWatch log group

- Region: `eu-west-1`
- Created through IaC: yes
- Retention: 7 days
- Cost considerations: small logging charges may accumulate with repeated testing

### SAM managed artifact bucket

- Region: `eu-west-1`
- Created through IaC: managed automatically by SAM
- Persistent data: stores deployment artifacts
- Removal: only if no other SAM-managed deployments depend on it

## What Phase 6 Changed

- Updated the existing Lambda function code
- Updated the existing Lambda execution role policy
- Added Bedrock-related environment configuration to the function
- Increased the Lambda timeout from `10` to `20` seconds

## What Phase 6 Did Not Create

- No new CloudFormation stack
- No API Gateway
- No S3 frontend hosting resource
- No database
- No separate Bedrock resource owned by this stack

Important note:

- The application invokes an AWS-managed Bedrock inference profile and foundation model, but the stack does not create those Bedrock resources itself.
