from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SearchResult(BaseModel):
    """Individual search result item."""
    id: str
    name: str
    category: Optional[str] = None
    containerId: Optional[str] = None
    preferredZone: Optional[str] = None
    
    # Additional fields for UI rendering/filtering
    type: str = "item"  # Used to differentiate between item/container/zone in UI

class SearchGroupedResults(BaseModel):
    """Grouped search results by type."""
    items: List[SearchResult] = []
    containers: List[SearchResult] = []
    zones: List[SearchResult] = []
    
    def __bool__(self):
        """Returns True if any results exist."""
        return bool(self.items or self.containers or self.zones)

class SearchResponse(BaseModel):
    """Response format for search API."""
    success: bool = True
    query: str
    results: SearchGroupedResults
    total_count: int = 0
    error: Optional[str] = None
    
    def dict(self, *args, **kwargs):
        """Override dict method to include total count calculation."""
        result = super().dict(*args, **kwargs)
        if self.total_count == 0 and self.results:
            result["total_count"] = (
                len(self.results.items) + 
                len(self.results.containers) + 
                len(self.results.zones)
            )
        return result