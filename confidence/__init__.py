__all__ = [
    # Core pipeline
    'IngestionNormalizationPipeline',
    
    # Schema
    'NormalizedBug',
    'FieldWithConfidence',
    'SourceMetadata',
    'ConfidenceLevel',
    'ExtractionSource',
    
    # Ingestion handlers
    'ErrorLogHandler',
    'FreeTextHandler',
    'AzureDevOpsHandler',
    
    # Extraction
    'RuleBasedExtractor',
    'PatternRegistry',
    'ExtractionResult',
    
    # Confidence
    'ConfidenceScorer',
    
    # Enrichment
    'NLPEnricher',
    
    # Configuration
    'PipelineConfig',
    
    # Utilities
    'SecurityValidator',
    'StructuredLogger',
]

__version__ = '1.0.0'
__author__ = 'AI Systems Architecture Team'