# Teardown

This guide explains how to remove `aws-cloud-ai-web` safely without accidentally deleting shared IAM infrastructure.

Do not run teardown if you still want the live portfolio demo to remain available.

## Safe Order

1. Confirm the AWS account and region.
2. Confirm whether the public site must remain live.
3. Disable or remove automatic deployment triggers if you are decommissioning the repository.
4. Empty the frontend bucket.
5. Delete the application CloudFormation stack.
6. Confirm Lambda and Function URL deletion.
7. Confirm stack-managed IAM and logs are gone.
8. Review SAM deployment artifacts.
9. Delete the repository bootstrap stack if it is no longer needed.
10. Remove repository variables from GitHub.
11. Decide whether the GitHub OIDC provider should remain because of other repositories.
12. Confirm no project resources remain.
13. Review billing after teardown.

## Step 1: Confirm Context

Check the stack:

```bash
aws cloudformation describe-stacks --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

Check the bootstrap stack:

```bash
aws cloudformation describe-stacks --stack-name aws-cloud-ai-web-github-frontend-bootstrap --region eu-west-1
```

## Step 2: Empty the Frontend Bucket

```bash
aws s3 rm s3://aws-cloud-ai-web-herrerogusano-frontend --recursive
```

This is required before CloudFormation can delete the bucket cleanly.

## Step 3: Delete the Application Stack

Preferred command:

```bash
sam delete --stack-name aws-cloud-ai-web-backend --region eu-west-1
```

This should remove:

- Lambda function
- Lambda Function URL
- Lambda execution role
- CloudWatch log group
- Frontend S3 bucket
- Frontend bucket policy

## Step 4: Verify Application Resource Removal

Check the Lambda:

```bash
aws lambda get-function --function-name aws-cloud-ai-web-backend-handler --region eu-west-1
```

Check the log group:

```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/aws-cloud-ai-web-backend-handler" --region eu-west-1
```

Check the frontend bucket:

```bash
aws s3api head-bucket --bucket aws-cloud-ai-web-herrerogusano-frontend
```

Check the website endpoint:

```bash
curl http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com
```

## Step 5: Review SAM Artifact Storage

Artifact bucket currently used:

- `aws-sam-cli-managed-default-samclisourcebucket-tptpcw2u9y7f`

Important note:

- This bucket may be shared with other SAM projects in the same account and region.
- Do not delete it casually unless you have confirmed it is no longer needed.

## Step 6: Remove GitHub Deployment Bootstrap

If this repository will no longer deploy anything:

```bash
aws cloudformation delete-stack --stack-name aws-cloud-ai-web-github-frontend-bootstrap --region eu-west-1
```

Verify deletion:

```bash
aws cloudformation describe-stacks --stack-name aws-cloud-ai-web-github-frontend-bootstrap --region eu-west-1
```

This removes the repository-specific deployment roles if they are managed only by that bootstrap stack.

## Step 7: Remove GitHub Repository Variables

Delete:

- `AWS_REGION`
- `AWS_BACKEND_DEPLOY_ROLE_ARN`
- `AWS_CLOUDFORMATION_EXECUTION_ROLE_ARN`
- `AWS_FRONTEND_DEPLOY_ROLE_ARN`
- `AWS_FRONTEND_BUCKET`
- `SAM_ARTIFACT_BUCKET`
- `SAM_STACK_NAME`

## Step 8: Review Shared IAM

The GitHub OIDC provider is account-level:

- `arn:aws:iam::344774635844:oidc-provider/token.actions.githubusercontent.com`

Keep it if:

- another repository uses GitHub OIDC in the same AWS account

Remove it only if:

- you have confirmed no repository depends on it

## Step 9: Review Bedrock Account-Level State

Deleting the application stack does not necessarily undo:

- model access approvals
- Marketplace subscriptions
- account-level budget settings

Those require separate review in AWS.

## Final Verification Checklist

- The application stack no longer exists
- The frontend bucket no longer exists
- The Function URL no longer responds
- The Lambda no longer exists
- The log group no longer exists
- Repository deployment variables are removed
- The bootstrap stack is removed if not needed
- The OIDC provider is retained only if intentionally shared

## Billing Follow-Up

After teardown:

- Review Cost Explorer
- Review AWS Budgets
- Confirm no unexpected Bedrock, Lambda, S3, or CloudWatch usage remains
