"""Pytest configuration for evals."""

from pathlib import Path

import pytest


@pytest.fixture
def eval_results_dir():
    """Path to the eval results directory."""
    return Path(__file__).parent / "results"
