import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import logging

from ingestion.base import BaseIngestionHandler
from schemas.source_metadata import SourceMetadata

logger = logging.getLogger(__name__)

class AzureDevOpsHandler(BaseIngestionHandler):
    """Handler for Azure DevOps bug work items."""
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize ADO handler.
        
        Args:
            api_token: ADO Personal Access Token (or from env)
        """
        self.api_token = api_token or os.getenv('ADO_API_TOKEN')
        if not self.api_token:
            logger.warning("No ADO API token provided - ADO ingestion will fail")
    
    def ingest(self, source: Dict[str, Any]) -> Tuple[str, SourceMetadata]:
        """
        Ingest from ADO bug work item.
        
        Args:
            source: ADO work item dict (from REST API response)
        
        Returns:
            Formatted text and metadata
        
        Expected ADO structure:
        {
            "id": "12345",
            "fields": {
                "System.Title": "Bug title",
                "System.Description": "Bug description",
                "Microsoft.VSTS.TCM.ReproSteps": "Repro steps",
                "System.State": "Active",
                ...
            }
        }
        """
        if not isinstance(source, dict):
            raise ValueError("ADO source must be a dictionary")
        
        work_item_id = source.get('id', 'unknown')
        fields = source.get('fields', {})
        
        # Extract relevant fields
        title = fields.get('System.Title', '')
        description = fields.get('System.Description', '')
        repro_steps = fields.get('Microsoft.VSTS.TCM.ReproSteps', '')
        acceptance_criteria = fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')
        
        # Format into structured text
        text_parts = []
        if title:
            text_parts.append(f"Title: {title}")
        if description:
            text_parts.append(f"\nDescription: {description}")
        if repro_steps:
            text_parts.append(f"\nReproduction Steps: {repro_steps}")
        if acceptance_criteria:
            text_parts.append(f"\nExpected Behavior: {acceptance_criteria}")
        
        text = '\n'.join(text_parts)
        
        # Strip HTML if present (ADO often includes HTML)
        text = self._strip_html(text)
        
        metadata = SourceMetadata(
            source_type="ado_bug",
            source_id=f"ado_{work_item_id}",
            ado_work_item_id=str(work_item_id),
            raw_text_length=len(text)
        )
        
        return text, metadata
    
    def _strip_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        import re
        # Simple HTML stripping (use html.parser or BeautifulSoup in production)
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = clean_text.replace('&nbsp;', ' ')
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        return clean_text.strip()
