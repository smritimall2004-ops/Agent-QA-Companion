from typing import Optional, Dict, Any
import logging

from ingestion.error_log_handler import ErrorLogHandler
from ingestion.freetext_handler import FreeTextHandler
from ingestion.ado_handler import AzureDevOpsHandler

from extraction.rule_engine import RuleBasedExtractor, ExtractionResult
from confidence.scorer import ConfidenceScorer
from enrichment.nlp_enricher import NLPEnricher

from schemas.normalized_bug import NormalizedBug, FieldWithConfidence, SourceMetadata, ExtractionSource

logger = logging.getLogger(__name__)


class IngestionNormalizationPipeline:
    """
    Main orchestration pipeline.
    
    Coordinates:
    1. Source-specific ingestion
    2. RegEx/rule-based extraction
    3. Confidence scoring
    4. Optional NLP enrichment
    5. Output normalization
    """
    
    def __init__(
        self,
        enable_nlp_enrichment: bool = False,
        confidence_threshold: float = 0.5,
        llm_endpoint: Optional[str] = None
    ):
        """
        Initialize pipeline.
        
        Args:
            enable_nlp_enrichment: Enable NLP enrichment
            confidence_threshold: Threshold for NLP enrichment
            llm_endpoint: Optional LLM API endpoint
        """
        # Initialize components
        self.error_log_handler = ErrorLogHandler()
        self.freetext_handler = FreeTextHandler()
        self.ado_handler = AzureDevOpsHandler()
        
        self.extractor = RuleBasedExtractor()
        self.scorer = ConfidenceScorer()
        self.enricher = NLPEnricher(enable_nlp_enrichment, llm_endpoint)
        
        self.confidence_threshold = confidence_threshold
        
        logger.info(
            f"Pipeline initialized (NLP enrichment: {enable_nlp_enrichment}, "
            f"threshold: {confidence_threshold})"
        )
    
    def process_error_log(self, file_path: str) -> NormalizedBug:
        """Process error log file."""
        text, metadata = self.error_log_handler.ingest(file_path)
        return self._process_text(text, metadata)
    
    def process_freetext(self, user_text: str) -> NormalizedBug:
        """Process user free text."""
        text, metadata = self.freetext_handler.ingest(user_text)
        return self._process_text(text, metadata)
    
    def process_ado_bug(self, ado_work_item: Dict[str, Any]) -> NormalizedBug:
        """Process Azure DevOps work item."""
        text, metadata = self.ado_handler.ingest(ado_work_item)
        return self._process_text(text, metadata)
    
    def _process_text(self, text: str, metadata: SourceMetadata) -> NormalizedBug:
        """
        Core processing logic (source-agnostic).
        
        Steps:
        1. Extract all fields using regex/rules
        2. Score confidence
        3. Optionally enrich with NLP
        4. Calculate overall metrics
        5. Return normalized bug
        """
        logger.info(f"Processing {metadata.source_type} (length: {len(text)})")
        
        # Step 1: Extract all fields
        extraction_results = self.extractor.extract_all_fields(text)
        
        # Step 2: Build normalized bug with confidence scoring
        normalized_bug = self._build_normalized_bug(extraction_results, metadata, text)
        
        # Step 3: Optional NLP enrichment
        if self.enricher.enabled:
            normalized_bug = self.enricher.enrich(
                normalized_bug,
                text,
                self.confidence_threshold
            )
        
        # Step 4: Calculate final metrics
        normalized_bug.overall_confidence = normalized_bug.calculate_overall_confidence()
        
        completeness = self.scorer.calculate_completeness(normalized_bug)
        logger.info(
            f"Normalized bug created: overall_confidence={normalized_bug.overall_confidence:.2f}, "
            f"completeness={completeness:.2f}"
        )
        
        return normalized_bug
    
    def _build_normalized_bug(
        self,
        extraction_results: Dict[str, ExtractionResult],
        metadata: SourceMetadata,
        raw_text: str
    ) -> NormalizedBug:
        """Build NormalizedBug from extraction results."""
        
        def create_field(result: ExtractionResult) -> FieldWithConfidence:
            """Convert ExtractionResult to FieldWithConfidence."""
            if not result.value:
                return FieldWithConfidence(
                    value=None,
                    confidence=0.0,
                    source=ExtractionSource.REGEX_LOOSE,
                    raw_evidence=None
                )
            
            # Score confidence
            final_confidence = self.scorer.score_field(
                base_confidence=result.confidence,
                source=result.source,
                has_evidence=result.raw_evidence is not None,
                value_length=len(result.value)
            )
            
            return FieldWithConfidence(
                value=result.value,
                confidence=final_confidence,
                source=result.source,
                raw_evidence=result.raw_evidence
            )
        
        # Count regex extractions
        regex_count = sum(
            1 for r in extraction_results.values()
            if r.value and r.source in [ExtractionSource.REGEX_STRICT, ExtractionSource.REGEX_LOOSE]
        )
        
        bug = NormalizedBug(
            source_metadata=metadata,
            error_type=create_field(extraction_results.get("error_type", ExtractionResult("error_type"))),
            component_module=create_field(extraction_results.get("component_module", ExtractionResult("component_module"))),
            trigger_repro_steps=create_field(extraction_results.get("trigger_repro_steps", ExtractionResult("trigger_repro_steps"))),
            observed_behavior=create_field(extraction_results.get("observed_behavior", ExtractionResult("observed_behavior"))),
            expected_behavior=create_field(extraction_results.get("expected_behavior", ExtractionResult("expected_behavior"))),
            fields_extracted_by_regex=regex_count
        )
        
        return bug
