"""Eval dataset for tray-discovery agent.

Add eval cases with recorded outputs to enable scoring.
See evals/datasets/data_harmonizer.py for the reference implementation.
"""

EVAL_CASES = [
    # Each case should have:
    # {
    #     "name": "case_id",
    #     "description": "What this case tests",
    #     "tags": ["tag1", "tag2"],
    #     "input": {
    #         "query": "the user request or trigger",
    #     },
    #     "expected": {
    #         "key_fields": ["field1", "field2"],  # fields that must be present
    #     },
    #     "recorded_output": {
    #         # Pre-recorded agent output to score against expectations.
    #         # Run the agent once, capture output, paste here.
    #     },
    # }
]
