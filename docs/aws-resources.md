# AWS Resource Inventory

Status: backend resources created in `eu-west-1` for Phase 4.

## Current Inventory

| Resource Type | Identifier | Status | Notes |
| --- | --- | --- | --- |
| CloudFormation stack | `aws-cloud-ai-web-backend` | Created | IaC entry point for backend resources |
| Lambda function | `aws-cloud-ai-web-backend-handler` | Created | Returns the fixed simulated backend response |
| Lambda Function URL | Environment-specific URL | Created | Public unauthenticated endpoint for this learning phase |
| IAM execution role | Auto-created by SAM/CloudFormation | Created | Used only for Lambda execution and CloudWatch logging |
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
- Cost considerations: low for light usage, but invocations still consume billable Lambda usage beyond applicable allowances

### Lambda Function URL

- Region: `eu-west-1`
- Created through IaC: yes
- Authentication: none in this educational phase
- Cost considerations: public exposure may increase invocation count if shared broadly

### IAM execution role

- Region: `eu-west-1`
- Created through IaC: yes
- Purpose: basic Lambda execution and logging only
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
