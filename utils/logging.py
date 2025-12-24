
import logging
import json
from datetime import datetime
from typing import Any, Dict


class StructuredLogger:
    """Structured logging for observability."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Add structured handler if not present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(self._get_formatter())
            self.logger.addHandler(handler)
    
    def _get_formatter(self):
        """Get JSON formatter for structured logging."""
        return logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
    
    def log_extraction(
        self,
        field_name: str,
        confidence: float,
        source: str,
        success: bool
    ):
        """Log extraction attempt."""
        self.logger.info(
            json.dumps({
                "event": "field_extraction",
                "field": field_name,
                "confidence": confidence,
                "source": source,
                "success": success,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
    
    def log_pipeline_metrics(
        self,
        bug_id: str,
        source_type: str,
        overall_confidence: float,
        regex_fields: int,
        nlp_fields: int,
        processing_time_ms: float
    ):
        """Log pipeline metrics."""
        self.logger.info(
            json.dumps({
                "event": "pipeline_complete",
                "bug_id": bug_id,
                "source_type": source_type,
                "overall_confidence": overall_confidence,
                "regex_fields": regex_fields,
                "nlp_fields": nlp_fields,
                "processing_time_ms": processing_time_ms,
                "timestamp": datetime.utcnow().isoformat()
            })
        )

