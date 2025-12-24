from typing import Tuple
import logging

from ingestion.base import BaseIngestionHandler
from schemas.source_metadata import SourceMetadata

logger = logging.getLogger(__name__)

class FreeTextHandler(BaseIngestionHandler):
    """Handler for user-provided free text descriptions."""
    
    MAX_TEXT_LENGTH = 10000
    
    def ingest(self, source: str) -> Tuple[str, SourceMetadata]:
        """
        Ingest free text input.
        
        Args:
            source: User-provided text string
        
        Returns:
            Sanitized text and metadata
        """
        if not isinstance(source, str):
            raise ValueError("Source must be a string")
        
        if len(source) > self.MAX_TEXT_LENGTH:
            raise ValueError(
                f"Text length ({len(source)}) exceeds maximum "
                f"({self.MAX_TEXT_LENGTH})"
            )
        
        # Basic sanitization
        text = source.strip()
        
        # Remove null bytes and control characters (except newlines/tabs)
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        metadata = SourceMetadata(
            source_type="freetext",
            source_id=f"freetext_{hash(text)}",
            raw_text_length=len(text)
        )
        
        return text, metadata
