
import re
from typing import Pattern, List, Tuple, Dict


class PatternRegistry:
    """
    Versioned registry of RegEx patterns for extraction.
    
    Patterns are classified by strength:
    - STRICT: High precision, low recall
    - LOOSE: Higher recall, lower precision
    
    Supports multiple log formats:
    - Server logs: [timestamp] LEVEL [service-name] message
    - Java exceptions: ExceptionType at package.Class.method
    - Bug reports: Structured text with repro steps
    """
    
    VERSION = "2.0.0"
    
    # ==========================================================================
    # ERROR TYPE PATTERNS
    # ==========================================================================
    
    ERROR_TYPE_STRICT: List[Tuple[Pattern, float]] = [
        # Java/Python Exceptions (original patterns)
        (re.compile(r'\b(NullPointerException|NPE)\b', re.IGNORECASE), 0.95),
        (re.compile(r'\b(IndexOutOfBoundsException)\b', re.IGNORECASE), 0.95),
        (re.compile(r'\b(SQLException)\b', re.IGNORECASE), 0.95),
        (re.compile(r'\b(TimeoutException)\b', re.IGNORECASE), 0.95),
        (re.compile(r'\b(ConnectionRefusedException)\b', re.IGNORECASE), 0.95),
        (re.compile(r'\b(FileNotFoundException)\b', re.IGNORECASE), 0.95),
        (re.compile(r'\b(OutOfMemoryError|Out of memory)\b', re.IGNORECASE), 0.95),
        (re.compile(r'\b(StackOverflowError)\b', re.IGNORECASE), 0.95),
        
        # HTTP/API Error Codes
        (re.compile(r'\b(5\d{2})\s+(?:Gateway\s+)?(?:Timeout|Error|Internal Server Error)\b', re.IGNORECASE), 0.95),
        (re.compile(r'\b(4\d{2})\s+(?:Not Found|Unauthorized|Forbidden|Bad Request)\b', re.IGNORECASE), 0.90),
        
        # Infrastructure/DevOps Errors
        (re.compile(r'(Connection\s+pool\s+exhausted)', re.IGNORECASE), 0.95),
        (re.compile(r'(Connection\s+timeout)', re.IGNORECASE), 0.95),
        (re.compile(r'(Circuit\s+breaker\s+triggered)', re.IGNORECASE), 0.95),
        (re.compile(r'(Service\s+(?:dependency\s+)?(?:unavailable|unresponsive))', re.IGNORECASE), 0.95),
        (re.compile(r'(Memory\s+usage\s+critical)', re.IGNORECASE), 0.95),
        (re.compile(r'(Memory\s+leak\s+detected)', re.IGNORECASE), 0.95),
        (re.compile(r'(Cascade\s+failure)', re.IGNORECASE), 0.95),
        (re.compile(r'(Database\s+connection\s+(?:error|failed|timeout))', re.IGNORECASE), 0.95),
        (re.compile(r'(endpoint\s+timeouts?\s+detected)', re.IGNORECASE), 0.95),
        (re.compile(r'(Request\s+processing\s+failed)', re.IGNORECASE), 0.90),
        (re.compile(r'(health\s+(?:status\s+)?(?:degraded|changed\s+to\s+DEGRADED))', re.IGNORECASE), 0.90),
        (re.compile(r'(queue\s+overflow)', re.IGNORECASE), 0.90),
        
        # Generic with ERROR/CRITICAL prefix (capture the message after)
        (re.compile(r'CRITICAL\s+\[[^\]]+\]\s+(.+?)(?:\n|$)', re.IGNORECASE), 0.92),
    ]
    
    ERROR_TYPE_LOOSE: List[Tuple[Pattern, float]] = [
        # Error patterns from log format: ERROR [service] message
        (re.compile(r'ERROR\s+\[[^\]]+\]\s+([^:\n]+)', re.IGNORECASE), 0.70),
        
        # Generic error indicators
        (re.compile(r'(error\s+rate\s+exceeded\s+threshold[^.]*)', re.IGNORECASE), 0.65),
        (re.compile(r'(failed\s+to\s+[^.:\n]+)', re.IGNORECASE), 0.60),
        (re.compile(r'(unable\s+to\s+[^.:\n]+)', re.IGNORECASE), 0.60),
        (re.compile(r'\b(timeout|timed?\s*out)\b', re.IGNORECASE), 0.55),
        (re.compile(r'\b(failure|failed|crash(?:ed)?)\b', re.IGNORECASE), 0.50),
        (re.compile(r'\b(degraded|unavailable|unresponsive)\b', re.IGNORECASE), 0.50),
    ]
    
    # ==========================================================================
    # COMPONENT/MODULE PATTERNS  
    # ==========================================================================
    
    COMPONENT_STRICT: List[Tuple[Pattern, float]] = [
        # Server log format: [service-name] - extract service name from brackets
        (re.compile(r'ERROR\s+\[([a-zA-Z][\w-]*(?:-[a-zA-Z][\w-]*)*)\]', re.IGNORECASE), 0.95),
        (re.compile(r'CRITICAL\s+\[([a-zA-Z][\w-]*(?:-[a-zA-Z][\w-]*)*)\]', re.IGNORECASE), 0.95),
        (re.compile(r'WARN\s+\[([a-zA-Z][\w-]*(?:-[a-zA-Z][\w-]*)*)\]', re.IGNORECASE), 0.90),
        
        # Service references in error messages
        (re.compile(r'(?:unavailable|unresponsive)[:\s]+([a-zA-Z][\w-]*-service)', re.IGNORECASE), 0.92),
        (re.compile(r'([a-zA-Z][\w-]*-service)\s+(?:unavailable|unresponsive|status)', re.IGNORECASE), 0.92),
        (re.compile(r'services?\s+degraded[:\s]+([a-zA-Z][\w-]*(?:-[a-zA-Z][\w-]*)*)', re.IGNORECASE), 0.90),
        
        # Java-style package.Class patterns
        (re.compile(r'in\s+module\s+["\']?([A-Za-z0-9_.]+)["\']?', re.IGNORECASE), 0.90),
        (re.compile(r'at\s+([A-Za-z0-9_.]+)\.([A-Za-z0-9_]+)\(', re.IGNORECASE), 0.88),
        (re.compile(r'in\s+(?:the\s+)?([A-Z][A-Za-z]+(?:Service|Module|Controller|Manager|Handler))', re.IGNORECASE), 0.90),
        (re.compile(r'component[:\s]+["\']?([A-Za-z0-9_.-]+)["\']?', re.IGNORECASE), 0.90),
    ]
    
    COMPONENT_LOOSE: List[Tuple[Pattern, float]] = [
        # Kebab-case service names (common in microservices)
        (re.compile(r'\b([a-z]+-[a-z]+(?:-[a-z]+)*-?service)\b', re.IGNORECASE), 0.70),
        (re.compile(r'\b([a-z]+-[a-z]+(?:-[a-z]+)*)\b(?=\s+(?:status|unavailable|degraded|error))', re.IGNORECASE), 0.65),
        
        # CamelCase service names
        (re.compile(r'\b([A-Z][A-Za-z]*Service)\b'), 0.65),
        (re.compile(r'\b([A-Z][A-Za-z]*Controller)\b'), 0.65),
        (re.compile(r'\b([A-Z][A-Za-z]*Manager)\b'), 0.60),
        (re.compile(r'\b([A-Z][A-Za-z]*Handler)\b'), 0.60),
        
        # Generic service references
        (re.compile(r'(?:backend|upstream)\s+service[:\s]+([a-zA-Z][\w-]+)', re.IGNORECASE), 0.70),
    ]
    
    # ==========================================================================
    # REPRO STEPS PATTERNS
    # ==========================================================================
    
    REPRO_STRICT: List[Tuple[Pattern, float]] = [
        # Explicit repro steps headers
        (re.compile(r'(?:steps?\s+to\s+reproduce|reproduction\s+steps?|repro\s+steps?)[:\s]+(.*?)(?:\n\n|expected|actual|$)', re.IGNORECASE | re.DOTALL), 0.95),
        (re.compile(r'(?:how\s+to\s+reproduce|to\s+reproduce)[:\s]+(.*?)(?:\n\n|expected|actual|$)', re.IGNORECASE | re.DOTALL), 0.90),
        (re.compile(r'(?:repro)[:\s]+(.*?)(?:\n\n|expected|$)', re.IGNORECASE | re.DOTALL), 0.85),
        
        # Numbered steps
        (re.compile(r'((?:^|\n)\s*1[\.\)]\s+.+(?:\n\s*\d[\.\)]\s+.+)+)', re.MULTILINE), 0.85),
    ]
    
    REPRO_LOOSE: List[Tuple[Pattern, float]] = [
        # User action descriptions
        (re.compile(r'(?:when\s+(?:I|user|you|clicking|accessing))\s+([^.\n]+)', re.IGNORECASE), 0.55),
        (re.compile(r'(?:(?:click|navigate|go\s+to|open|access|visit)(?:ing|ed)?)\s+([^.\n]+)', re.IGNORECASE), 0.50),
        (re.compile(r'(?:if\s+you)[:\s]+([^.\n]+)', re.IGNORECASE), 0.45),
        
        # Log sequence (for server logs - show the sequence of events)
        (re.compile(r'((?:\[\d{4}-[^\]]+\]\s+(?:ERROR|WARN|INFO)[^\n]+\n?){2,})', re.IGNORECASE), 0.60),
    ]
    
    # ==========================================================================
    # OBSERVED BEHAVIOR PATTERNS
    # ==========================================================================
    
    OBSERVED_STRICT: List[Tuple[Pattern, float]] = [
        # Explicit observed/actual headers
        (re.compile(r'(?:actual\s+(?:behavior|result)|what\s+happened|observed(?:\s+behavior)?|current\s+behavior)[:\s]+(.*?)(?:\n\n|expected|$)', re.IGNORECASE | re.DOTALL), 0.95),
        (re.compile(r'(?:result|outcome)[:\s]+(.*?)(?:\n\n|$)', re.IGNORECASE | re.DOTALL), 0.85),
        
        # Customer/User impact statements
        (re.compile(r'((?:customer|user)\s+impact[:\s]+[^\n]+)', re.IGNORECASE), 0.90),
        (re.compile(r'(\d+\s+users?\s+affected[^\n]*)', re.IGNORECASE), 0.90),
    ]
    
    OBSERVED_LOOSE: List[Tuple[Pattern, float]] = [
        # Error descriptions from logs
        (re.compile(r'(?:ERROR|CRITICAL)[^\]]*\]\s+([^:\n]+(?:failed|error|timeout|unavailable)[^.\n]*)', re.IGNORECASE), 0.65),
        
        # Consequence descriptions
        (re.compile(r'(?:but|instead|however)[:\s]+([^.\n]+)', re.IGNORECASE), 0.55),
        (re.compile(r'(?:shows?|displays?|returns?|gives?)[:\s]+([^.\n]+)', re.IGNORECASE), 0.50),
        (re.compile(r'(application\s+crash(?:es|ed)?[^.\n]*)', re.IGNORECASE), 0.60),
        (re.compile(r'(service\s+(?:is\s+)?(?:down|unavailable|unresponsive)[^.\n]*)', re.IGNORECASE), 0.60),
    ]
    
    # ==========================================================================
    # EXPECTED BEHAVIOR PATTERNS
    # ==========================================================================
    
    EXPECTED_STRICT: List[Tuple[Pattern, float]] = [
        # Explicit expected headers
        (re.compile(r'(?:expected\s+(?:behavior|result|outcome)|should\s+(?:be|have|work))[:\s]+(.*?)(?:\n\n|$)', re.IGNORECASE | re.DOTALL), 0.95),
        (re.compile(r'(?:acceptance\s+criteria|expected)[:\s]+(.*?)(?:\n\n|$)', re.IGNORECASE | re.DOTALL), 0.90),
    ]
    
    EXPECTED_LOOSE: List[Tuple[Pattern, float]] = [
        # Should statements
        (re.compile(r'(?:should|must|needs?\s+to)\s+((?:be|have|show|display|work|complete|return|process)[^.\n]+)', re.IGNORECASE), 0.60),
        (re.compile(r'(?:want|need|expect(?:ing)?)[:\s]+([^.\n]+)', re.IGNORECASE), 0.50),
        
        # Normal/correct behavior descriptions  
        (re.compile(r'(?:normally|correctly|properly|successfully)[,\s]+([^.\n]+)', re.IGNORECASE), 0.55),
        
        # Threshold/SLA references (implied expected behavior)
        (re.compile(r'(?:threshold|SLA|limit)[:\s]+(\d+[^.\n]*)', re.IGNORECASE), 0.55),
    ]
    
    @classmethod
    def get_all_patterns(cls) -> Dict[str, Dict[str, List[Tuple[Pattern, float]]]]:
        """Return all patterns organized by field and strictness."""
        return {
            "error_type": {
                "strict": cls.ERROR_TYPE_STRICT,
                "loose": cls.ERROR_TYPE_LOOSE
            },
            "component_module": {
                "strict": cls.COMPONENT_STRICT,
                "loose": cls.COMPONENT_LOOSE
            },
            "trigger_repro_steps": {
                "strict": cls.REPRO_STRICT,
                "loose": cls.REPRO_LOOSE
            },
            "observed_behavior": {
                "strict": cls.OBSERVED_STRICT,
                "loose": cls.OBSERVED_LOOSE
            },
            "expected_behavior": {
                "strict": cls.EXPECTED_STRICT,
                "loose": cls.EXPECTED_LOOSE
            }
        }
