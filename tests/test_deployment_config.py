from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_template_defines_s3_frontend_resources_and_cors_origins() -> None:
    template = (REPO_ROOT / "template.yaml").read_text(encoding="utf-8")

    assert "FrontendWebsiteBucket:" in template
    assert "FrontendWebsiteBucketPolicy:" in template
    assert "WebsiteConfiguration:" in template
    assert "BucketName: aws-cloud-ai-web-herrerogusano-frontend" in template
    assert "http://localhost:8000" in template
    assert "s3-website-${AWS::Region}.amazonaws.com" in template


def test_template_outputs_frontend_bucket_and_website_url() -> None:
    template = (REPO_ROOT / "template.yaml").read_text(encoding="utf-8")

    assert "FrontendWebsiteBucketName:" in template
    assert "FrontendWebsiteUrl:" in template
