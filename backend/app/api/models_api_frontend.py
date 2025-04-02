from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ContainerFrontendResponse(BaseModel):
    """Container model matching the CSV format expected by the frontend."""
    id: str
    name: str  # Using containerId as name since original model doesn't have a name field
    type: str = "Supply Container"  # Default value, adjust as needed
    zoneId: str
    capacity: int = 0  # Default value, not in original model
    width: float
    depth: float
    height: float
    maxWeight: float = 0.0  # Default value, not in original model
    currentWeight: float = 0.0  # Default value, not in original model
    start_width: Optional[float] = None
    start_depth: Optional[float] = None
    start_height: Optional[float] = None
    end_width: Optional[float] = None
    end_depth: Optional[float] = None
    end_height: Optional[float] = None

class ItemFrontendResponse(BaseModel):
    """Item model matching the CSV format expected by the frontend."""
    id: str
    name: str
    category: str = "Maintenance Tools"  # Default value, not in original model
    containerId: str
    quantity: int = 1  # Default value, not in original model
    mass: float
    expirationDate: Optional[datetime] = None
    width: float
    depth: float
    height: float
    priority: int
    usageLimit: Optional[int] = None
    usageCount: int = 0
    preferredZone: Optional[str] = None
    position_start_width: float
    position_start_depth: float
    position_start_height: float
    position_end_width: float
    position_end_depth: float
    position_end_height: float

class PlacementFrontendResponse(BaseModel):
    """Response model for frontend that matches the CSV format."""
    containers: List[ContainerFrontendResponse]
    items: List[ItemFrontendResponse]