
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import uuid

from schemas.source_metadata import SourceMetadata


class ConfidenceLevel(str, Enum):
    """Confidence classification for extracted fields."""
    HIGH = "high"      # >= 0.8
    MEDIUM = "medium"  # 0.5 - 0.79
    LOW = "low"        # < 0.5


class ExtractionSource(str, Enum):
    """Source of extracted information."""
    REGEX_STRICT = "regex_strict"
    REGEX_LOOSE = "regex_loose"
    RULE_BASED = "rule_based"
    ADO_API = "ado_api"
    NLP_ENRICHED = "nlp_enriched"
    USER_PROVIDED = "user_provided"


class FieldWithConfidence(BaseModel):
    """Generic field with confidence metadata."""
    value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    source: ExtractionSource
    raw_evidence: Optional[str] = Field(default=None, max_length=500)
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('raw_evidence')
    def truncate_evidence(cls, v):
        """Truncate evidence to prevent bloat."""
        if v and len(v) > 500:
            return v[:497] + "..."
        return v
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Classify confidence into discrete levels."""
        if self.confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif self.confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW





class NormalizedBug(BaseModel):
    """
    Canonical normalized bug schema.
    
    All inputs normalize to this structure regardless of source.
    Each field includes confidence metadata for downstream decision-making.
    """
    
    # Identity
    bug_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = "1.0.0"
    
    # Source metadata
    source_metadata: SourceMetadata
    
    # Core extracted fields
    error_type: FieldWithConfidence
    component_module: FieldWithConfidence
    trigger_repro_steps: FieldWithConfidence
    observed_behavior: FieldWithConfidence
    expected_behavior: FieldWithConfidence
    
    # Optional enriched fields
    severity: Optional[FieldWithConfidence] = None
    environment: Optional[FieldWithConfidence] = None
    failure_classification: Optional[FieldWithConfidence] = None
    
    # Aggregated metrics
    overall_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    fields_extracted_by_regex: int = 0
    fields_enriched_by_nlp: int = 0
    total_extractable_fields: int = 5  # Core fields
    
    # Processing metadata
    processing_timestamp: datetime = Field(default_factory=datetime.utcnow)
    nlp_enrichment_applied: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "bug_id": "123e4567-e89b-12d3-a456-426614174000",
                "schema_version": "1.0.0",
                "error_type": {
                    "value": "NullPointerException",
                    "confidence": 0.95,
                    "source": "regex_strict",
                    "raw_evidence": "java.lang.NullPointerException at..."
                },
                "overall_confidence": 0.82
            }
        }
    
    def calculate_overall_confidence(self) -> float:
        """Calculate aggregate confidence across all core fields."""
        core_fields = [
            self.error_type,
            self.component_module,
            self.trigger_repro_steps,
            self.observed_behavior,
            self.expected_behavior
        ]
        
        confidences = [f.confidence for f in core_fields if f.value is not None]
        
        if not confidences:
            return 0.0
        
        # Weighted average with completeness penalty
        avg_confidence = sum(confidences) / len(confidences)
        completeness_factor = len(confidences) / len(core_fields)
        
        return avg_confidence * completeness_factor
    
    def get_low_confidence_fields(self, threshold: float = 0.5) -> List[str]:
        """Identify fields needing enrichment."""
        low_conf_fields = []
        
        field_map = {
            "error_type": self.error_type,
            "component_module": self.component_module,
            "trigger_repro_steps": self.trigger_repro_steps,
            "observed_behavior": self.observed_behavior,
            "expected_behavior": self.expected_behavior
        }
        
        for name, field in field_map.items():
            if field.value is None or field.confidence < threshold:
                low_conf_fields.append(name)
        
        return low_conf_fields
