# Teardown Notes

Status: placeholder only during project foundation.

## Current State

No AWS resources have been created for `aws-cloud-ai-web` yet, so there is nothing to tear down.

## Teardown Approach

As resources are introduced later, this document will record:

- what resource was created
- how it should be deleted
- what dependencies must be removed first
- how to verify deletion
- any cost or data-retention implications

## Future Coverage

Deletion guidance will be completed incrementally for:

- AWS SAM-managed backend resources
- Lambda Function URL configuration
- S3 frontend hosting resources
- any future CI/CD deployment dependencies that create cloud resources

## Important Constraint

No stack names, bucket names, ARNs, or account-specific identifiers are recorded here until they exist.
