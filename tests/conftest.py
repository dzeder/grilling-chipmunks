"""
Shared test fixtures for Ohanafy AI Ops.

See TESTING.md for fixture documentation and testing strategy.
"""

import os
import pytest


# --- Salesforce fixtures ---


@pytest.fixture(scope="session")
def sf_scratch_org():
    """Session-scoped SF scratch org connection.
    Skips if SF_CI_SCRATCH_ORG_URL is not set.
    """
    url = os.environ.get("SF_CI_SCRATCH_ORG_URL")
    if not url:
        pytest.skip("SF_CI_SCRATCH_ORG_URL not set — skipping SF scratch org tests")
    # TODO: Return authenticated SF client
    return {"url": url}


@pytest.fixture(scope="session")
def sf_sandbox():
    """Session-scoped SF sandbox connection.
    Skips if CI_ENV != staging.
    """
    if os.environ.get("CI_ENV") != "staging":
        pytest.skip("CI_ENV != staging — skipping SF sandbox tests")
    # TODO: Return authenticated SF client
    return {}


# --- AWS fixtures ---


@pytest.fixture
def localstack_s3():
    """Function-scoped boto3 S3 client pointed at LocalStack."""
    import boto3

    return boto3.client(
        "s3",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )


@pytest.fixture
def test_bucket(localstack_s3):
    """Create and tear down an S3 test bucket."""
    bucket_name = "ohanafy-test-bucket"
    localstack_s3.create_bucket(Bucket=bucket_name)
    yield bucket_name
    # Teardown: delete all objects then the bucket
    response = localstack_s3.list_objects_v2(Bucket=bucket_name)
    for obj in response.get("Contents", []):
        localstack_s3.delete_object(Bucket=bucket_name, Key=obj["Key"])
    localstack_s3.delete_bucket(Bucket=bucket_name)


# --- Claude fixtures ---


@pytest.fixture
def mock_claude(mocker):
    """Patch anthropic.Anthropic to return canned responses."""
    mock_client = mocker.patch("anthropic.Anthropic")
    mock_instance = mock_client.return_value
    mock_response = mocker.MagicMock()
    mock_response.content = [mocker.MagicMock(text="Mocked Claude response")]
    mock_instance.messages.create.return_value = mock_response
    return mock_instance


@pytest.fixture(scope="session")
def real_anthropic_client():
    """Session-scoped real Anthropic client.
    Skips if ANTHROPIC_API_KEY is not set.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set — skipping real Claude tests")
    import anthropic

    return anthropic.Anthropic(api_key=api_key)
