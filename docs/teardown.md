# Teardown Notes

Status: ready for the deployed Phase 7 frontend and backend.

## Safe Teardown Order

1. Empty the frontend website bucket.
2. Delete the SAM stack.
3. Confirm the bucket and bucket policy are gone.
4. Confirm the website endpoint no longer serves content.
5. Confirm the Lambda, Function URL, IAM role, and log group are removed.
6. Review whether the SAM managed artifact bucket should remain.

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

## Additional Manual Review

SAM uses a managed deployment bucket for artifacts:

- `aws-sam-cli-managed-default-samclisourcebucket-tptpcw2u9y7f`

This bucket may be shared with future SAM deployments in the same account and region. Do not delete it casually unless you are sure nothing else needs it.

Stack deletion also does not necessarily remove all Bedrock account-level state. Review separately whether the AWS account still has:

- model access settings enabled manually
- Marketplace subscriptions accepted manually
- billing or budget settings related to future testing

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

## Notes

- the website bucket contains only public static assets in this phase
- CloudWatch logs may incur small ongoing cost while retained
- the current log retention is 7 days
- Bedrock usage charges are request-driven and stop once the endpoint is no longer invoked
