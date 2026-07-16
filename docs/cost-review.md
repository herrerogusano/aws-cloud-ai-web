# Cost Review

This review summarizes the likely cost drivers for `aws-cloud-ai-web` and what was checked during project closure.

Review date:

- July 16, 2026

## Main Cost Sources

### Amazon Bedrock

- Each real answer consumes model inference usage
- This is the most important variable cost for interactive use
- Costs depend on model pricing, tokens, and request volume

Current control points:

- Conservative generation settings
- Low manual test volume
- No automated repeated Bedrock integration test in CI
- Deployment smoke checks avoid sending paid prompts

### AWS Lambda

- Charged by invocations and duration beyond free-tier eligibility
- Current function size is small and runtime duration is short for simple requests

Observed example:

- One checked request completed in about `2777 ms` according to CloudWatch logs

### Amazon S3

- Public frontend bucket stores static files
- Costs come from storage plus GET and PUT requests

### CloudWatch Logs

- Backend logs are retained for 7 days
- Storage cost should remain small at low volume

### SAM Artifact Bucket

- Stores deployment artifacts
- Usually small, but worth reviewing over time if many builds accumulate

## Cost-Related Checks Performed

Verified on July 16, 2026 in `eu-west-1`:

- No EC2 instances
- No NAT gateways
- No RDS instances
- No API Gateway added by this project
- No ECS service introduced by this project

These checks matter because those services often create higher or less obvious baseline cost than this serverless footprint.

## Current Usage Profile

Reasonable expectation for this project:

- Low-volume manual demos
- Low-volume personal validation
- No load testing
- No background workers
- No continuous Bedrock polling

This should stay inexpensive, but it is not guaranteed to remain free.

## Recommended Cost Hygiene

- Review AWS Budgets
- Review the AWS Billing dashboard
- Use Cost Explorer if usage grows
- Keep CloudWatch retention short unless longer history is needed
- Avoid repeated manual Bedrock tests when not necessary
- Delete the project when it is no longer needed

## Cost Risk Summary

Main risk:

- repeated public Bedrock usage against the unauthenticated Function URL

Main mitigations currently missing because they are out of scope:

- authentication
- rate limiting
- WAF or abuse controls
- budget alarms managed in infrastructure
