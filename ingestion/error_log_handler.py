import os
from pathlib import Path
from typing import Tuple
import logging

from ingestion.base import BaseIngestionHandler
from schemas.source_metadata import SourceMetadata

logger = logging.getLogger(__name__)

class ErrorLogHandler(BaseIngestionHandler):
    """Handler for error log files (TXT, PDF, DOCX)."""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.log', '.pdf', '.doc', '.docx'}
    
    def ingest(self, source: str) -> Tuple[str, SourceMetadata]:
        """
        Ingest error log file.
        
        Args:
            source: File path to error log
        
        Returns:
            Extracted text and metadata
        """
        file_path = Path(source)
        
        if not file_path.exists():
            raise ValueError(f"File not found: {source}")
        
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        self._validate_file_size(str(file_path))
        
        # Extract text based on file type
        if file_path.suffix.lower() in {'.txt', '.log'}:
            text = self._extract_from_text(file_path)
        elif file_path.suffix.lower() == '.pdf':
            text = self._extract_from_pdf(file_path)
        else:  # .doc, .docx
            text = self._extract_from_doc(file_path)
        
        metadata = SourceMetadata(
            source_type="error_log",
            source_id=str(file_path),
            file_name=file_path.name,
            file_size_bytes=os.path.getsize(file_path),
            raw_text_length=len(text)
        )
        
        return text, metadata
    
    def _extract_from_text(self, file_path: Path) -> str:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read text file: {e}")
            raise
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF (placeholder - requires PyPDF2 or similar)."""
        # In production, use: PyPDF2, pdfplumber, or pdfminer
        logger.warning("PDF extraction not fully implemented - using placeholder")
        return f"[PDF content from {file_path.name}]"
    
    def _extract_from_doc(self, file_path: Path) -> str:
        """Extract text from DOC/DOCX (placeholder - requires python-docx)."""
        # In production, use: python-docx
        logger.warning("DOC extraction not fully implemented - using placeholder")
        return f"[DOC content from {file_path.name}]"
