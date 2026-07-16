# Teardown Notes

Status: ready for the deployed Phase 6 backend.

## Primary Teardown Command

```bash
sam delete --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

This is the preferred teardown path because the backend is managed through AWS SAM and CloudFormation.

## What Should Be Removed

- Lambda function `aws-cloud-ai-web-backend-handler`
- Lambda Function URL
- IAM execution role created for the function
- CloudWatch log group `/aws/lambda/aws-cloud-ai-web-backend-handler`
- CloudFormation stack `aws-cloud-ai-web-backend`

## What Stack Deletion Covers In This Phase

Deleting the stack should remove all Lambda and IAM configuration introduced by this phase, including:

- the Bedrock-related environment variables
- the scoped Bedrock IAM statements attached to the Lambda execution role
- the increased Lambda timeout

## Possible Manual Cleanup

SAM used a managed deployment bucket for artifacts:

- `aws-sam-cli-managed-default-samclisourcebucket-tptpcw2u9y7f`

This bucket is SAM-managed and may be shared with future SAM deployments in the same account and region. Do not delete it casually unless you are sure nothing else needs it.

## Additional Account-Level Review

Stack deletion does not necessarily remove all Bedrock account-level state.

Review separately whether the AWS account still has:

- model access settings the user enabled manually
- Marketplace subscriptions the user accepted manually
- billing or budget settings related to future testing

## Verification After Deletion

Check that the stack is gone:

```bash
aws cloudformation describe-stacks --stack-name aws-cloud-ai-web-backend
```

Check that the Lambda is gone:

```bash
aws lambda get-function --function-name aws-cloud-ai-web-backend-handler
```

Check that the log group is gone:

```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/aws-cloud-ai-web-backend-handler"
```

Check that the Function URL is no longer available:

```bash
curl -X POST "https://oekibadklbb4mlie5jlchwgc7a0iweyl.lambda-url.eu-west-1.on.aws/" -H "Content-Type: application/json" -d '{"question":"test"}'
```

## Notes

- CloudWatch logs may incur small ongoing cost while retained
- The current log retention is 7 days
- No persistent data store exists in this phase
- Bedrock usage charges are request-driven and stop once the endpoint is no longer invoked
