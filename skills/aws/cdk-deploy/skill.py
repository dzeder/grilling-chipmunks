"""CDK Deploy Skill -- Synth and deploy CDK stacks with Checkov scanning."""

from __future__ import annotations

from typing import Any

from schema import CdkDeployInput, CdkDeployOutput


async def run(input_data: CdkDeployInput) -> CdkDeployOutput:
    """Synthesize, scan, and deploy a CDK stack.

    Steps: cdk synth -> checkov scan -> cdk diff -> cdk deploy.
    """
    # TODO: Implement CDK deployment pipeline
    raise NotImplementedError("cdk-deploy skill not yet implemented")


async def synth(input_data: CdkDeployInput) -> str:
    """Run cdk synth and return the template path."""
    # TODO: Implement synth
    raise NotImplementedError


async def checkov_scan(template_dir: str) -> dict[str, Any]:
    """Run Checkov against synthesized CloudFormation templates."""
    # TODO: Implement Checkov scanning
    raise NotImplementedError


async def validate(input_data: CdkDeployInput) -> list[str]:
    """Pre-flight validation."""
    errors: list[str] = []
    if not input_data.stack_name.startswith("ohanafy-"):
        errors.append("Stack name must start with 'ohanafy-'.")
    return errors
