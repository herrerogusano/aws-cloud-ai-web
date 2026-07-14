# ADR 0005: Use S3 For Static Frontend Hosting

## Status

Accepted

## Context

The project frontend will be a simple static site built with plain HTML, CSS, and JavaScript. It does not need a dynamic application server.

## Decision

Use Amazon S3 as the planned static frontend hosting solution.

## Alternatives Considered

- Vercel
- Netlify
- AWS Amplify Hosting

## Consequences

- The hosting path remains aligned with the AWS-focused portfolio goal.
- Deployment can later be implemented as static asset synchronization.
- Additional CDN decisions can be evaluated later if the project needs them.
