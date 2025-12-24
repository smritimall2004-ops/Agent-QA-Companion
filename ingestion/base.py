from abc import ABC, abstractmethod
import os
from pathlib import Path
from typing import Tuple, Any
import logging

from schemas.source_metadata import SourceMetadata

logger = logging.getLogger(__name__)


class BaseIngestionHandler(ABC):
    """Base interface for all ingestion handlers."""
    
    MAX_FILE_SIZE_MB = 50
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    
    @abstractmethod
    def ingest(self, source: Any) -> Tuple[str, SourceMetadata]:
        """
        Ingest from source and return (raw_text, metadata).
        
        Args:
            source: Source-specific input (file path, text, API response)
        
        Returns:
            Tuple of (extracted_text, source_metadata)
        
        Raises:
            ValueError: If input is invalid or too large
        """
        pass
    
    def _validate_file_size(self, file_path: str) -> None:
        """Validate file size is within limits."""
        file_size = os.path.getsize(file_path)
        if file_size > self.MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds "
                f"maximum allowed ({self.MAX_FILE_SIZE_MB} MB)"
            )