from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_ci_workflow_contains_pull_request_validation_and_no_oidc() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "pull_request:" in workflow
    assert "- main" in workflow
    assert "id-token: write" not in workflow
    assert "actions/setup-python@v6" in workflow
    assert "uv sync --frozen" in workflow
    assert "uv run ruff check ." in workflow
    assert "uv run ruff format --check ." in workflow
    assert "uv run mypy ." in workflow
    assert "uv run pytest" in workflow
    assert "sam validate" in workflow
    assert "sam build" in workflow


def test_frontend_deploy_workflow_uses_oidc_and_s3_sync() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "deploy-frontend.yml").read_text(
        encoding="utf-8"
    )

    assert "push:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "id-token: write" in workflow
    assert "group: production-frontend" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "aws-actions/configure-aws-credentials@v6.2.1" in workflow
    assert 'aws s3 sync frontend/ "s3://$AWS_FRONTEND_BUCKET" --delete' in workflow
    assert '--exclude "config.example.js"' in workflow
    assert "python scripts/check_frontend_website.py" in workflow


def test_bootstrap_template_restricts_trust_and_permissions() -> None:
    template = (REPO_ROOT / "bootstrap" / "github-frontend-deploy-iam.yaml").read_text(
        encoding="utf-8"
    )
    subject_restriction = (
        "token.actions.githubusercontent.com:sub: !Sub "
        "repo:${GitHubRepositoryOwner}/${GitHubRepositoryName}:ref:refs/heads/main"
    )

    assert "token.actions.githubusercontent.com:aud: sts.amazonaws.com" in template
    assert subject_restriction in template
    assert "RoleName: aws-cloud-ai-web-github-frontend-deploy" in template
    assert "- s3:ListBucket" in template
    assert "- s3:GetBucketLocation" in template
    assert "- s3:PutObject" in template
    assert "- s3:DeleteObject" in template
