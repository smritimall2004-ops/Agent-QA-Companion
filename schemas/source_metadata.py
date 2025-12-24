from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import uuid

class SourceMetadata(BaseModel):
    """Metadata about the input source."""
    source_type: Literal["error_log", "freetext", "ado_bug"]
    source_id: str
    ingestion_timestamp: datetime = Field(default_factory=datetime.utcnow)
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    ado_work_item_id: Optional[str] = None
    raw_text_length: int = 0