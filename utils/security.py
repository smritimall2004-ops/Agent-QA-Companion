from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Security validation utilities for input sanitization."""
    
    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.sh', '.ps1', '.dll', '.so',
        '.app', '.cmd', '.com', '.msi', '.scr'
    }
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """
        Validate file path for security concerns.
        
        Args:
            file_path: Path to validate
        
        Returns:
            True if safe, False otherwise
        """
        path = Path(file_path)
        
        # Check for path traversal
        try:
            path.resolve().relative_to(Path.cwd())
        except ValueError:
            logger.warning(f"Path traversal detected: {file_path}")
            return False
        
        # Check extension
        if path.suffix.lower() in SecurityValidator.DANGEROUS_EXTENSIONS:
            logger.warning(f"Dangerous file extension: {path.suffix}")
            return False
        
        return True
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 100000) -> str:
        """
        Sanitize text input.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
        
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
            logger.warning(f"Text truncated to {max_length} characters")
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def redact_pii(text: str) -> str:
        """
        Redact potential PII from text (for logging).
        
        Args:
            text: Text that may contain PII
        
        Returns:
            Text with PII redacted
        """
        import re
        
        # Email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Phone numbers (simple pattern)
        text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE]', text)
        
        # SSN pattern
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
        
        # Credit card patterns (simple)
        text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', text)
        
        return text


