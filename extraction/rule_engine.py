
from typing import Optional, List, Tuple, Dict, Pattern
import logging

from schemas.normalized_bug import ExtractionSource
from extraction.pattern_registry import PatternRegistry

logger = logging.getLogger(__name__)


class ExtractionResult:
    """Result from a single extraction attempt."""
    
    def __init__(
        self,
        field_name: str,
        value: Optional[str] = None,
        confidence: float = 0.0,
        source: ExtractionSource = ExtractionSource.REGEX_LOOSE,
        raw_evidence: Optional[str] = None,
        matched_pattern: Optional[str] = None
    ):
        self.field_name = field_name
        self.value = value
        self.confidence = confidence
        self.source = source
        self.raw_evidence = raw_evidence
        self.matched_pattern = matched_pattern


class RuleBasedExtractor:
    """
    Core extraction engine using RegEx patterns and rules.
    
    Principles:
    - Try strict patterns first
    - Fall back to loose patterns
    - Never overwrite high-confidence matches
    - Record all extraction metadata
    """
    
    def __init__(self, pattern_registry: PatternRegistry = None):
        self.registry = pattern_registry or PatternRegistry()
        self.patterns = self.registry.get_all_patterns()
    
    def extract_field(self, text: str, field_name: str) -> ExtractionResult:
        """
        Extract a single field from text using patterns.
        
        Args:
            text: Input text to extract from
            field_name: Field to extract (must exist in registry)
        
        Returns:
            ExtractionResult with best match or empty result
        """
        if field_name not in self.patterns:
            logger.warning(f"Unknown field: {field_name}")
            return ExtractionResult(field_name=field_name)
        
        field_patterns = self.patterns[field_name]
        
        # Try strict patterns first
        result = self._try_patterns(text, field_patterns["strict"], ExtractionSource.REGEX_STRICT)
        if result.value:
            logger.info(f"Extracted {field_name} with strict pattern (conf: {result.confidence:.2f})")
            return result
        
        # Fall back to loose patterns
        result = self._try_patterns(text, field_patterns["loose"], ExtractionSource.REGEX_LOOSE)
        if result.value:
            logger.info(f"Extracted {field_name} with loose pattern (conf: {result.confidence:.2f})")
            return result
        
        logger.debug(f"No pattern matched for {field_name}")
        return ExtractionResult(field_name=field_name)
    
    def _try_patterns(
        self,
        text: str,
        patterns: List[Tuple[Pattern, float]],
        source: ExtractionSource
    ) -> ExtractionResult:
        """Try all patterns and return best match."""
        best_match = None
        best_confidence = 0.0
        best_evidence = None
        
        for pattern, base_confidence in patterns:
            matches = pattern.findall(text)
            if matches:
                # Handle tuple matches (groups)
                if isinstance(matches[0], tuple):
                    value = ' '.join(str(m) for m in matches[0] if m).strip()
                else:
                    value = str(matches[0]).strip()
                
                # Skip empty matches
                if not value:
                    continue
                
                # Boost confidence if multiple occurrences
                occurrence_boost = min(0.1 * (len(matches) - 1), 0.2)
                confidence = min(base_confidence + occurrence_boost, 1.0)
                
                if confidence > best_confidence:
                    best_match = value
                    best_confidence = confidence
                    # Find position and extract evidence with context
                    pos = text.find(value)
                    if pos >= 0:
                        start = max(0, pos - 50)
                        end = min(len(text), pos + len(value) + 50)
                        best_evidence = text[start:end]
                    else:
                        best_evidence = value[:200]
                    
                    # Truncate evidence to max 497 chars (leave room for "...")
                    if best_evidence and len(best_evidence) > 497:
                        best_evidence = best_evidence[:497] + "..."
        
        if best_match:
            # Also truncate the value if it's too long
            if len(best_match) > 1000:
                best_match = best_match[:997] + "..."
            
            return ExtractionResult(
                field_name="",  # Set by caller
                value=best_match,
                confidence=best_confidence,
                source=source,
                raw_evidence=best_evidence
            )
        
        return ExtractionResult(field_name="")
    
    def extract_all_fields(self, text: str) -> Dict[str, ExtractionResult]:
        """Extract all known fields from text."""
        results = {}
        
        for field_name in self.patterns.keys():
            results[field_name] = self.extract_field(text, field_name)
        
        return results
