# ADR 0011: Use Separate GitHub And CloudFormation Deployment Roles

## Status

Accepted

## Context

Phase 10 completes the deployment pipeline by automating AWS SAM deployment after merges to `main`.

GitHub Actions now needs enough access to:

- validate the project
- upload SAM deployment artifacts
- trigger CloudFormation updates for the existing stack
- synchronize the public frontend to the S3 website bucket

Expanding the existing frontend deployment role to include CloudFormation, Lambda, IAM, and stack-management permissions would blur responsibilities and weaken the security boundary that was introduced in the previous phase.

Giving the GitHub-assumed role direct permissions for all stack resources would also make it harder to prove that the repository automation cannot modify unrelated infrastructure or its own trust chain.

## Decision

Use separate roles for production deployment:

- `aws-cloud-ai-web-github-backend-deploy`
  - assumed by GitHub Actions through OIDC on pushes to `main`
  - limited to stack-level CloudFormation operations, SAM artifact-bucket access, and `iam:PassRole` only for the CloudFormation execution role
- `aws-cloud-ai-web-cloudformation-execution`
  - assumed by CloudFormation during `sam deploy`
  - limited to the known Lambda, IAM, CloudWatch Logs, and S3 resources managed by the project stack
- `aws-cloud-ai-web-github-frontend-deploy`
  - remains limited to frontend S3 synchronization only

The deployment workflow uses backend deployment first and then re-authenticates with the frontend role before running `aws s3 sync`.

## Alternatives Considered

- Expand the existing frontend deployment role to deploy both backend and frontend
- Give the GitHub backend deployment role direct permissions over Lambda, IAM, S3, and CloudFormation without a separate execution role

## Consequences

- The IAM model is more explicit and easier to audit
- GitHub Actions does not receive broad direct infrastructure permissions
- CloudFormation retains rollback behavior during stack updates
- The bootstrap IAM template becomes slightly more complex
- Repository variables must track separate backend, CloudFormation, and frontend role ARNs
