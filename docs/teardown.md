# Teardown Notes

Status: ready for the deployed Phase 4 backend.

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

## Possible Manual Cleanup

SAM used a managed deployment bucket for artifacts:

- `aws-sam-cli-managed-default-samclisourcebucket-tptpcw2u9y7f`

This bucket is SAM-managed and may be shared with future SAM deployments in the same account and region. Do not delete it casually unless you are sure nothing else needs it.

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
