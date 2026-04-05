"""Unit tests for support agent."""

import pytest


@pytest.mark.unit
class TestSupportRouting:
    def test_how_to_question_handled(self):
        """How-to questions should be answered directly at high confidence."""
        # TODO: Implement with mock Claude
        pass

    def test_compliance_question_escalated(self):
        """TTB/compliance questions should always escalate."""
        # TODO: Implement
        pass

    def test_low_confidence_escalated(self):
        """Responses below 0.75 confidence should escalate."""
        # TODO: Implement
        pass


@pytest.mark.unit
class TestSupportContext:
    def test_customer_context_loaded(self):
        """Customer context should be loaded before every response."""
        # TODO: Implement
        pass

    def test_no_pii_in_logs(self):
        """Customer PII should never appear in log output."""
        # TODO: Implement
        pass


@pytest.mark.unit
class TestSupportEscalation:
    def test_legal_always_escalates(self):
        """Legal questions should always escalate regardless of confidence."""
        # TODO: Implement
        pass

    def test_pricing_always_escalates(self):
        """Pricing questions should always escalate."""
        # TODO: Implement
        pass

    def test_cancellation_always_escalates(self):
        """Cancellation requests should always escalate."""
        # TODO: Implement
        pass
