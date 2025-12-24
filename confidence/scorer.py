from schemas.normalized_bug import ExtractionSource, NormalizedBug


class ConfidenceScorer:
    """
    Deterministic confidence scoring system.
    
    Scoring factors:
    1. Extractor strength (strict > loose)
    2. Evidence multiplicity
    3. Field completeness
    4. Source reliability
    """
    
    # Source reliability weights
    SOURCE_WEIGHTS = {
        ExtractionSource.ADO_API: 1.0,
        ExtractionSource.REGEX_STRICT: 0.95,
        ExtractionSource.RULE_BASED: 0.85,
        ExtractionSource.REGEX_LOOSE: 0.70,
        ExtractionSource.USER_PROVIDED: 0.60,
        ExtractionSource.NLP_ENRICHED: 0.50,
    }
    
    # Confidence thresholds
    THRESHOLD_HIGH = 0.8
    THRESHOLD_MEDIUM = 0.5
    
    @classmethod
    def score_field(
        cls,
        base_confidence: float,
        source: ExtractionSource,
        has_evidence: bool = False,
        value_length: int = 0
    ) -> float:
        """
        Calculate final confidence for a field.
        
        Args:
            base_confidence: Initial confidence from extractor
            source: Extraction source
            has_evidence: Whether raw evidence exists
            value_length: Length of extracted value
        
        Returns:
            Final confidence score [0.0, 1.0]
        """
        # Apply source reliability weight
        confidence = base_confidence * cls.SOURCE_WEIGHTS.get(source, 0.5)
        
        # Boost for evidence
        if has_evidence:
            confidence = min(confidence + 0.05, 1.0)
        
        # Penalize very short values (likely incomplete)
        if 0 < value_length < 5:
            confidence *= 0.8
        
        return round(confidence, 3)
    
    @classmethod
    def should_enrich_field(cls, confidence: float, threshold: float = None) -> bool:
        """Determine if field needs NLP enrichment."""
        threshold = threshold or cls.THRESHOLD_MEDIUM
        return confidence < threshold
    
    @classmethod
    def calculate_completeness(cls, normalized_bug: NormalizedBug) -> float:
        """Calculate structural completeness score."""
        core_fields = [
            normalized_bug.error_type,
            normalized_bug.component_module,
            normalized_bug.trigger_repro_steps,
            normalized_bug.observed_behavior,
            normalized_bug.expected_behavior
        ]
        
        filled_count = sum(1 for f in core_fields if f.value is not None)
        return filled_count / len(core_fields)
