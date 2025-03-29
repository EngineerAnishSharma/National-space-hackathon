# app/models.py
from pydantic import BaseModel
from datetime import date
from typing import Optional, Dict, List

# Item Model
class Item(BaseModel):
    itemId: str
    name: str
    width: float
    depth: float
    height: float
    mass: float
    priority: int
    expiryDate: Optional[date] = None
    usageLimit: Optional[int] = None
    preferredZone: str

# Container Model
class Container(BaseModel):
    containerId: str
    zone: str
    width: float
    depth: float
    height: float

# Placement Models
class Coordinates(BaseModel):
    width: float
    depth: float
    height: float

class Position(BaseModel):
    startCoordinates: Coordinates
    endCoordinates: Coordinates

class Placement(BaseModel):
    itemId: str
    containerId: str
    position: Position

class RearrangementStep(BaseModel):
    step: int
    action: str  # "move", "remove", "place"
    itemId: str
    fromContainer: str
    fromPosition: Position
    toContainer: str
    toPosition: Position

class PlacementResponse(BaseModel):
    success: bool
    placements: list[Placement]
    rearrangements: list[RearrangementStep]

# Retrieval Models
class RetrievalStep(BaseModel):
    step: int
    action: str  # "remove", "setAside", "retrieve", "placeBack"
    itemId: str
    itemName: str

class RetrievalResponse(BaseModel):
    success: bool
    found: bool
    item: dict  # Can be made more specific with an Item model
    retrievalSteps: list[RetrievalStep]

# Waste Management Models
class WasteItem(BaseModel):
    itemId: str
    name: str
    reason: str  # "Expired", "Out of Uses"
    containerId: str
    width: float
    depth: float
    height: float

class ReturnManifestItem(BaseModel):
    itemId: str
    name: str
    reason: str

class ReturnManifest(BaseModel):
    undockingContainerId: str
    undockingDate: str
    returnItems: list[ReturnManifestItem]
    totalVolume: float
    totalWeight: float

class WasteReturnPlanResponse(BaseModel):
    success: bool
    returnPlan: list[dict]  # Can be made more specific
    retrievalSteps: list[dict]  # Can be made more specific
    returnManifest: ReturnManifest

class WasteItemsResponse(BaseModel):
    success: bool
    wasteItems: list[WasteItem]

class CompleteUndockingResponse(BaseModel):
    success: bool
    itemsRemoved: int

# Log Models
class LogEntry(BaseModel):
    timestamp: str
    userId: Optional[str] = None
    actionType: str  # "placement", "retrieval", "rearrangement", "disposal"
    itemId: str
    details: dict  # Details specific to the action type

class LogResponse(BaseModel):
    logs: list[LogEntry]