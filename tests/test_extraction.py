"""
Unit tests for extraction and confidence scoring.

Run with: pytest tests/
"""

import unittest

from extraction.pattern_registry import PatternRegistry
from confidence.scorer import ConfidenceScorer
from orchestration.pipeline import IngestionNormalizationPipeline


class TestPatternRegistry(unittest.TestCase):
    """Test RegEx pattern matching."""
    
    def setUp(self):
        self.registry = PatternRegistry()
        self.pipeline = IngestionNormalizationPipeline()
        self.scorer = ConfidenceScorer()
    
    def test_schema_consistency(self):
        """Test that different input types produce same schema."""
        text1 = "NullPointerException in PaymentService"
        bug1 = self.pipeline.process_freetext(text1)
        
        ado_bug = {
            "id": "123",
            "fields": {
                "System.Title": "NullPointerException in PaymentService",
                "System.Description": "Payment fails"
            }
        }
        bug2 = self.pipeline.process_ado_bug(ado_bug)
        
        # Both should have same schema structure
        self.assertEqual(type(bug1), type(bug2))
        self.assertIsNotNone(bug1.error_type)
        self.assertIsNotNone(bug2.error_type)
    
    def test_confidence_calculation(self):
        """Test overall confidence calculation."""
        text = """
        Error: NullPointerException in UserService
        Steps to reproduce: Click login button
        Observed: App crashes
        Expected: Should login successfully
        """
        bug = self.pipeline.process_freetext(text)
        
        # Should have positive confidence
        self.assertGreater(bug.overall_confidence, 0.0)
        
        # Should reflect completeness
        completeness = self.scorer.calculate_completeness(bug)
        self.assertGreater(completeness, 0.0)
