# Lessons Learned

This document captures the durable technical lessons from building `aws-cloud-ai-web`.

## 1. Serverless architecture is simple only when the boundaries stay simple

What was initially unclear:

- It is easy to underestimate the operational edge around a "small" serverless app.

What problem appeared:

- Even with one frontend and one Lambda, the project still needed CORS decisions, IAM scope, logging choices, deployment order, and rollback thinking.

What the project taught:

- Serverless removes server management, not system design.

What I would do differently:

- I would define runtime flow and deployment flow diagrams even earlier.

## 2. Lambda Function URLs are fast to adopt but come with public-surface trade-offs

What was initially unclear:

- A Function URL looked like the fastest way to expose one endpoint.

What problem appeared:

- The simplicity is real, but so are the limitations: public exposure, weaker edge controls than API Gateway, and the need to stay disciplined about CORS and error handling.

What the project taught:

- Function URLs are a strong fit for narrow portfolio scope, but they should be a deliberate trade-off.

What I would do differently:

- For a production-oriented version I would revisit API Gateway or another controlled edge.

## 3. Bedrock integration is straightforward; Bedrock operations are not automatic

What was initially unclear:

- The code path to call `converse` is fairly small, but the operational details matter.

What problem appeared:

- Model access, pricing awareness, inference-profile choice, and IAM permission scope all needed explicit review.

What the project taught:

- Small provider integrations still need model validation, cost awareness, and defensive response parsing.

What I would do differently:

- I would keep model selection notes and cost assumptions documented from day one.

## 4. IAM shape matters more than almost any line of app code

What was initially unclear:

- It is tempting to use broad roles just to get a pipeline working.

What problem appeared:

- A proper production flow needed a split between GitHub backend orchestration, CloudFormation execution, and frontend sync.

What the project taught:

- Least-privilege design becomes much easier to defend when each actor has one narrow responsibility.

What I would do differently:

- I would bootstrap deployment identities earlier instead of treating them as cleanup after the app works.

## 5. OIDC is worth the setup cost

What was initially unclear:

- Using GitHub OIDC requires more initial IAM work than saving access keys once.

What problem appeared:

- The account needed a provider, trust conditions, and repository variables before deployment would work cleanly.

What the project taught:

- The setup cost is justified because it removes long-lived secrets from GitHub and makes trust rules explicit.

What I would do differently:

- I would standardize the bootstrap pattern sooner for future projects.

## 6. CORS becomes clearer when treated as part of the architecture, not as a patch

What was initially unclear:

- At first CORS can look like a small frontend annoyance.

What problem appeared:

- The real public website origin had to be allowed explicitly, and local development still had to keep working.

What the project taught:

- CORS is part of the deployed interface contract.

What I would do differently:

- I would document deployed origins as soon as the first real hosting target is chosen.

## 7. S3 static website hosting is great for simplicity, but the HTTP limitation is real

What was initially unclear:

- S3 static website hosting solved the hosting problem quickly.

What problem appeared:

- The public site is served over HTTP, which is acceptable for a portfolio exercise but clearly below production expectations.

What the project taught:

- Simplicity is useful, but visible limitations should be documented honestly.

What I would do differently:

- I would plan the CloudFront migration path earlier even if I do not implement it yet.

## 8. Deployment troubleshooting often comes from configuration interaction, not code bugs

What was initially unclear:

- A pipeline can look correct while still failing because of the interaction between defaults and explicit flags.

What problem appeared:

- The production workflow failed because `samconfig.toml` enabled `resolve_s3` while the workflow also passed `--s3-bucket`.

What the project taught:

- Deployment configuration needs the same scrutiny as application code.

What I would do differently:

- I would add explicit assertions for deployment flags earlier and document local-versus-CI differences sooner.

## 9. Documentation is part of the system

What was initially unclear:

- Working infrastructure can still be hard to explain or maintain if the docs lag behind.

What problem appeared:

- Once the app, Bedrock integration, S3 hosting, and CI/CD all existed, the repo needed a real closure pass to become portfolio-grade.

What the project taught:

- Architecture docs, teardown steps, cost notes, and interview notes are not "extra"; they are part of leaving a project reusable.

What I would do differently:

- I would keep portfolio-facing docs evolving during the build instead of clustering them at the end.
