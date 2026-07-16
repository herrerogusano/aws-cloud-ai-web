# Teardown Notes

Status: ready for the deployed frontend and backend, with separate teardown notes for the GitHub Actions frontend deployment bootstrap.

## Safe Teardown Order

1. Disable or remove GitHub frontend deployment configuration if it is no longer needed.
2. Empty the frontend website bucket.
3. Delete the SAM stack.
4. Delete the GitHub frontend bootstrap stack if this repository no longer needs automated frontend deployment.
5. Confirm the bucket and bucket policy are gone.
6. Confirm the website endpoint no longer serves content.
7. Confirm the Lambda, Function URL, IAM role, and log group are removed.
8. Review whether the SAM managed artifact bucket and GitHub OIDC provider should remain.

Do not start teardown now if the frontend is still needed for later phases.

## Empty The Frontend Bucket First

Empty the public website bucket before deleting the stack:

```bash
aws s3 rm s3://aws-cloud-ai-web-herrerogusano-frontend --recursive
```

Versioning is not enabled in this phase, so no version cleanup is required.

## Primary Stack Deletion Command

```bash
sam delete --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

This is the preferred teardown path because the frontend and backend are managed through AWS SAM and CloudFormation.

## What Should Be Removed

- S3 website bucket `aws-cloud-ai-web-herrerogusano-frontend`
- S3 bucket policy for that bucket
- Lambda function `aws-cloud-ai-web-backend-handler`
- Lambda Function URL
- IAM execution role created for the function
- CloudWatch log group `/aws/lambda/aws-cloud-ai-web-backend-handler`
- CloudFormation stack `aws-cloud-ai-web-backend`
- GitHub repository variables:
  - `AWS_REGION`
  - `AWS_BACKEND_DEPLOY_ROLE_ARN`
  - `AWS_CLOUDFORMATION_EXECUTION_ROLE_ARN`
  - `AWS_FRONTEND_DEPLOY_ROLE_ARN`
  - `AWS_FRONTEND_BUCKET`
  - `SAM_ARTIFACT_BUCKET`
  - `SAM_STACK_NAME`
- CloudFormation bootstrap stack `aws-cloud-ai-web-github-frontend-bootstrap`
- GitHub frontend deployment role `aws-cloud-ai-web-github-frontend-deploy` if no other project needs it
- GitHub backend deployment role `aws-cloud-ai-web-github-backend-deploy` if no other project needs it
- CloudFormation execution role `aws-cloud-ai-web-cloudformation-execution` if no other stack needs it

## Additional Manual Review

SAM uses a managed deployment bucket for artifacts:

- `aws-sam-cli-managed-default-samclisourcebucket-tptpcw2u9y7f`

This bucket may be shared with future SAM deployments in the same account and region. Do not delete it casually unless you are sure nothing else needs it.

Stack deletion also does not necessarily remove all Bedrock account-level state. Review separately whether the AWS account still has:

- model access settings enabled manually
- Marketplace subscriptions accepted manually
- billing or budget settings related to future testing

The GitHub OIDC provider is an account-level IAM resource and may be shared by other repositories. Do not remove it automatically just because this project is being torn down. Check first whether any other repository or workflow still relies on:

- `arn:aws:iam::344774635844:oidc-provider/token.actions.githubusercontent.com`

## Removing The GitHub Frontend Bootstrap Stack

If this repository no longer needs automatic frontend deployment, remove the bootstrap stack:

```bash
aws cloudformation delete-stack --stack-name aws-cloud-ai-web-github-frontend-bootstrap --region eu-west-1
```

Then confirm it is gone:

```bash
aws cloudformation describe-stacks --stack-name aws-cloud-ai-web-github-frontend-bootstrap --region eu-west-1
```

If the OIDC provider is shared with another bootstrap stack or another repository, keep it in place and only remove the repository-specific role and GitHub variables.

## Verification After Deletion

Check that the stack is gone:

```bash
aws cloudformation describe-stacks --stack-name aws-cloud-ai-web-backend
```

Check that the frontend bucket is gone:

```bash
aws s3api head-bucket --bucket aws-cloud-ai-web-herrerogusano-frontend
```

Check that the website URL no longer serves content:

```bash
curl http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com
```

Check that the Lambda is gone:

```bash
aws lambda get-function --function-name aws-cloud-ai-web-backend-handler
```

Check that the log group is gone:

```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/aws-cloud-ai-web-backend-handler"
```

Check that the GitHub repository variables were removed:

- `AWS_REGION`
 - `AWS_BACKEND_DEPLOY_ROLE_ARN`
 - `AWS_CLOUDFORMATION_EXECUTION_ROLE_ARN`
 - `AWS_FRONTEND_DEPLOY_ROLE_ARN`
- `AWS_FRONTEND_BUCKET`
- `SAM_ARTIFACT_BUCKET`
- `SAM_STACK_NAME`

## Notes

- the website bucket contains only public static assets in this phase
- CloudWatch logs may incur small ongoing cost while retained
- the current log retention is 7 days
- Bedrock usage charges are request-driven and stop once the endpoint is no longer invoked
- the GitHub OIDC provider may outlive this project intentionally if other repositories use it
