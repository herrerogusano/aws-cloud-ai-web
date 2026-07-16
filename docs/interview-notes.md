# Interview Notes

## Why Lambda?

It matched the scope well: one request in, one response out, no server management, small operational footprint, and easy integration with AWS-native IAM and Bedrock.

## Why Function URL instead of API Gateway?

It kept the project simpler. The app only needed one public endpoint, so a Function URL reduced configuration and moving parts. For production I would likely re-evaluate API Gateway for stronger routing, throttling, auth, and policy control.

## Why S3?

The frontend is static. S3 static website hosting was the smallest AWS-native option to publish HTML, CSS, and JavaScript without adding a build system or extra hosting layer.

## Why AWS SAM?

It gave a concise way to define Lambda, the Function URL, IAM, log retention, and the S3 website bucket in one deployable stack while still using CloudFormation underneath.

## Why Bedrock?

The project goal included a real AWS-native LLM integration. Bedrock fit that directly and kept authentication inside AWS IAM instead of introducing a separate external API key flow.

## Why boto3?

The app only needed a thin AWS SDK client, not a framework. `boto3` kept the integration small and close to the actual Bedrock API surface.

## Why OIDC?

It avoids storing permanent AWS keys in GitHub. GitHub Actions can obtain short-lived AWS credentials only for approved workflows and only for the configured repository and branch.

## What does CI validate?

Formatting, linting, type checking, tests, SAM template validation, and SAM build. It validates code quality and packaging without deploying or calling Bedrock.

## What does CD deploy?

The production workflow validates the repo again, deploys the backend stack through SAM and CloudFormation, retrieves outputs, smoke-checks the backend, then syncs the frontend bucket and smoke-checks the website.

## How does IAM work here?

Lambda has its own execution role for CloudWatch and Bedrock. GitHub Actions has one role for backend orchestration and another for frontend sync. CloudFormation gets a third execution role to apply stack changes with narrower permissions than a general admin role.

## How are costs controlled?

By keeping the architecture serverless and small, using conservative model settings, avoiding automated Bedrock calls in CI, and keeping manual inference tests limited.

## What are the main security limitations?

The frontend is public and HTTP-only, the Function URL is public and unauthenticated, and there is no rate limiting or abuse protection. Those are accepted portfolio trade-offs, not production standards.

## What would change for production?

I would add HTTPS through CloudFront, replace or front the Function URL with a stronger API edge, add authentication, introduce rate limiting or WAF controls, and improve monitoring and rollback confidence.

## How would the application scale?

The static frontend scales easily through S3, and Lambda can scale with request volume. The main scaling constraints would be Bedrock throughput, public endpoint abuse, and cost control.

## How would rollback work?

Use Git as the source of truth: identify the last good commit, revert or redeploy it through the same workflow, and let the pipeline update backend and frontend in order.

## What was the hardest problem?

Not the Bedrock call itself. The harder parts were IAM boundaries, CORS, and getting a credible GitHub-to-AWS deployment flow that did not rely on permanent keys.

## What did you learn?

That the difficult part of a small AI web app is often not generating text. It is shaping the deployment path, the permissions, the public surface, and the documentation so the system is reproducible and explainable.
