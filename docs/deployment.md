# Deployment Notes

Status: placeholder only during project foundation. No deployment has been performed.

## Intended Deployment Targets

- Backend: AWS Lambda deployed through AWS SAM
- Public backend endpoint: Lambda Function URL
- Frontend: Amazon S3

## Prerequisites

- AWS CLI installed locally
- AWS SAM CLI installed locally
- An AWS account with permission to deploy the required resources
- A configured AWS profile or equivalent credential source
- Amazon Bedrock model access enabled later when Phase 6 starts
- A remote GitHub repository before CI/CD automation is introduced

## Planned Inputs

These values will be documented when they truly exist:

- Stack names
- Bucket names
- Lambda function name
- Deployment environment names
- GitHub Actions secrets or OIDC configuration
- Public URLs

## Current State

- No AWS resources have been created for this project
- No `sam deploy` command has been run
- No IAM configuration has been modified for this project

## Future Deployment Checklist

This section will be completed when deployment work begins:

1. Validate the SAM template.
2. Confirm AWS credentials and region.
3. Confirm Bedrock access requirements.
4. Deploy backend resources.
5. Publish frontend assets.
6. Record resulting resources in `docs/aws-resources.md`.
