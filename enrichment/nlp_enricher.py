from typing import Optional
import logging

from schemas.normalized_bug import NormalizedBug, ExtractionSource

logger = logging.getLogger(__name__)


class NLPEnricher:
    """
    Optional NLP-based enrichment for low-confidence fields.
    
    This is a pluggable component that can be:
    - Disabled completely
    - Swapped with different implementations
    - Gated by confidence thresholds
    
    IMPORTANT: Never overwrites high-confidence fields.
    """
    
    def __init__(self, enabled: bool = False, llm_endpoint: Optional[str] = None):
        """
        Initialize NLP enricher.
        
        Args:
            enabled: Whether enrichment is active
            llm_endpoint: Optional LLM API endpoint
        """
        self.enabled = enabled
        self.llm_endpoint = llm_endpoint
        
        if enabled and not llm_endpoint:
            logger.warning("NLP enrichment enabled but no endpoint provided")
    
    def enrich(
        self,
        normalized_bug: NormalizedBug,
        raw_text: str,
        confidence_threshold: float = 0.5
    ) -> NormalizedBug:
        """
        Enrich low-confidence fields using NLP.
        
        Args:
            normalized_bug: Partially filled normalized bug
            raw_text: Original input text
            confidence_threshold: Only enrich fields below this threshold
        
        Returns:
            Enriched normalized bug
        """
        if not self.enabled:
            logger.debug("NLP enrichment disabled - skipping")
            return normalized_bug
        
        # Identify fields needing enrichment
        low_conf_fields = normalized_bug.get_low_confidence_fields(confidence_threshold)
        
        if not low_conf_fields:
            logger.info("All fields meet confidence threshold - no enrichment needed")
            return normalized_bug
        
        logger.info(f"Enriching fields: {low_conf_fields}")
        
        # Enrich each low-confidence field
        for field_name in low_conf_fields:
            enriched_value = self._enrich_field(field_name, raw_text, normalized_bug)
            
            if enriched_value:
                # Get current field
                current_field = getattr(normalized_bug, field_name)
                
                # Only update if current value is None or confidence is low
                if current_field.value is None or current_field.confidence < confidence_threshold:
                    current_field.value = enriched_value
                    current_field.confidence = 0.5  # NLP enrichment baseline
                    current_field.source = ExtractionSource.NLP_ENRICHED
                    current_field.raw_evidence = raw_text[:500]
                    
                    normalized_bug.fields_enriched_by_nlp += 1
                    logger.info(f"Enriched {field_name} via NLP")
        
        normalized_bug.nlp_enrichment_applied = True
        return normalized_bug
    
    def _enrich_field(
        self,
        field_name: str,
        raw_text: str,
        context: NormalizedBug
    ) -> Optional[str]:
        """
        Use NLP to infer field value.
        
        In production, this would call an LLM API.
        For now, returns placeholder.
        """
        # Placeholder implementation
        # In production: Call LLM with structured prompt
        
        logger.debug(f"NLP enrichment for {field_name} (placeholder)")
        
        # Example: Infer expected behavior from observed behavior
        if field_name == "expected_behavior" and context.observed_behavior.value:
            return f"[NLP-inferred] System should not {context.observed_behavior.value}"
        
        return None
