from dataclasses import dataclass
from typing import Optional


@dataclass
class PipelineConfig:
    """Configuration for ingestion pipeline."""
    
    # Feature flags
    enable_nlp_enrichment: bool = False
    enable_ado_integration: bool = True
    enable_pdf_extraction: bool = True
    
    # Confidence thresholds
    confidence_threshold_high: float = 0.8
    confidence_threshold_medium: float = 0.5
    nlp_enrichment_threshold: float = 0.5
    
    # Size limits
    max_file_size_mb: int = 50
    max_text_length: int = 100000
    max_evidence_length: int = 500
    
    # API configuration
    ado_api_url: Optional[str] = None
    ado_api_token: Optional[str] = None
    llm_api_endpoint: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    enable_structured_logging: bool = True
    redact_pii: bool = True
    
    # Pattern registry
    pattern_registry_version: str = "1.0.0"
    
    @classmethod
    def from_env(cls) -> 'PipelineConfig':
        """Load configuration from environment variables."""
        import os
        
        return cls(
            enable_nlp_enrichment=os.getenv('ENABLE_NLP', 'false').lower() == 'true',
            ado_api_url=os.getenv('ADO_API_URL'),
            ado_api_token=os.getenv('ADO_API_TOKEN'),
            llm_api_endpoint=os.getenv('LLM_API_ENDPOINT'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
        )

