# Demo Script

This is a short live demo outline for a two-minute interview walkthrough.

## 0:00-0:20 Problem

- Explain that the project is a small serverless web app
- A user asks one question in a browser
- AWS Lambda sends that question to Amazon Bedrock and returns a real answer

## 0:20-0:50 Live Application

- Open the public website:
  - `http://aws-cloud-ai-web-herrerogusano-frontend.s3-website-eu-west-1.amazonaws.com`
- Enter one short question such as:
  - `What is AWS Lambda?`
- Click `Preguntar`
- Point out:
  - the loading state
  - the disabled submit button during the request
  - the real generated answer

## 0:50-1:20 Architecture

- Explain the runtime path:
  - `S3 static website -> Lambda Function URL -> AWS Lambda -> Amazon Bedrock`
- Mention:
  - serverless footprint
  - no external API key in the app
  - IAM role used by Lambda for Bedrock access

## 1:20-1:45 CI/CD

- Show the repository workflows
- Explain:
  - Pull Requests run CI only
  - merge to `main` triggers deployment
  - GitHub authenticates to AWS through OIDC
  - backend deploys with SAM before frontend sync

## 1:45-2:00 Trade-Offs and Learning

- Mention one or two trade-offs:
  - Function URL was simpler than API Gateway for this scope
  - S3 website hosting is simple but leaves the public frontend on HTTP
  - OIDC is safer than storing permanent AWS keys in GitHub

## Good Questions To Expect

- Why not API Gateway?
- Why not CloudFront?
- How would you harden it for production?
- How do you control costs and public exposure?
