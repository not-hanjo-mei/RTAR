"""
URL parser for extracting media IDs from REALITY App URLs.
"""

import re
from typing import Optional


class URLParser:
    """Parser for REALITY App URLs to extract media IDs."""
    
    URL_PATTERNS = [
        r'https?://REALITY\.app/viewer/(\d+)',
        r'REALITY\.app/viewer/(\d+)',
        r'/viewer/(\d+)',
        r'(\d+)'
    ]
    
    @classmethod
    def extract_media_id(cls, text: str) -> Optional[str]:
        """
        Extract media ID from text (URL or plain ID).
        
        Args:
            text: URL or media ID string
            
        Returns:
            Extracted media ID or None if not found
        """
        if not text or not text.strip():
            return None
        
        text = text.strip()
        
        # Try URL patterns first
        for pattern in cls.URL_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        # Check if it's a plain numeric ID
        if text.isdigit():
            return text
        
        return None
    
    @classmethod
    def is_valid_url(cls, text: str) -> bool:
        """Check if text contains a valid REALITY App URL."""
        return cls.extract_media_id(text) is not None
    
    @classmethod
    def build_url(cls, media_id: str) -> str:
        """Build full REALITY App URL from media ID."""
        return f"https://REALITY.app/viewer/{media_id}"
    
    @classmethod
    def normalize_media_id(cls, media_id: str) -> Optional[str]:
        """Normalize media ID to string format."""
        if not media_id:
            return None
        
        # Remove any non-numeric characters
        cleaned = re.sub(r'\D', '', str(media_id))
        
        if cleaned:
            return cleaned
        
        return None