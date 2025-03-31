# /app/models_api.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import iso8601 # Use a robust parser

# --- Coordinate and Position Models ---

class Coordinates(BaseModel):
    width: float = Field(..., ge=0)
    depth: float = Field(..., ge=0)
    height: float = Field(..., ge=0)

class Position(BaseModel):
    startCoordinates: Coordinates
    endCoordinates: Coordinates

# --- Item Models ---

class ItemBase(BaseModel):
    itemId: str
    name: str
    width: float = Field(..., gt=0)
    depth: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    mass: float = Field(..., gt=0)
    priority: int = Field(..., ge=0, le=100)
    expiryDate: Optional[datetime] = None # Accept ISO string, convert to datetime
    usageLimit: Optional[int] = Field(None, ge=0)
    preferredZone: Optional[str] = None

    @validator('expiryDate', pre=True, always=True)
    def parse_expiry_date(cls, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            # Use iso8601 library for robust parsing
            return iso8601.parse_date(value)
        except iso8601.ParseError as e:
            raise ValueError(f"Invalid ISO 8601 date format: {value}. Error: {e}")
        except Exception as e:
             raise ValueError(f"Error parsing date '{value}': {e}")


class ItemCreate(ItemBase):
    pass # Inherits all fields

class ItemResponse(ItemBase):
    currentUses: int
    status: str # Use the string representation of the enum

    class Config:
        orm_mode = True # To allow creating from ORM objects

# --- Container Models ---

class ContainerBase(BaseModel):
    containerId: str
    zone: str
    width: float = Field(..., gt=0)
    depth: float = Field(..., gt=0)
    height: float = Field(..., gt=0)

class ContainerCreate(ContainerBase):
    pass

class ContainerResponse(ContainerBase):
    id: Optional[int] # Maybe not needed for API response?

    class Config:
        orm_mode = True

# --- Placement Models ---

class PlacementResponseItem(BaseModel):
    itemId: str
    containerId: str
    position: Position

class RearrangementStep(BaseModel):
    step: int
    action: str # "move", "remove", "place"
    itemId: str
    fromContainer: Optional[str] = None # Null if placing a new item initially in rearrangement
    fromPosition: Optional[Position] = None
    toContainer: str
    toPosition: Position

class PlacementRequest(BaseModel):
    items: List[ItemCreate]
    containers: List[ContainerCreate] # API expects full container details

class PlacementResponse(BaseModel):
    success: bool
    error: Optional[str] = None # Add error field for better reporting
    placements: List[PlacementResponseItem] # Use PlacementResponseItem here
    rearrangements: List[RearrangementStep]
    details: Optional[Dict] = None # Keep details for validation errors

# --- Search/Retrieval Models ---

class RetrievalStep(BaseModel):
    step: int
    action: str # "remove", "setAside", "retrieve", "placeBack"
    itemId: str
    itemName: str

class SearchResponseItem(BaseModel):
    itemId: str
    name: str
    containerId: str
    zone: str
    position: Position

class SearchResponse(BaseModel):
    success: bool
    found: bool
    item: Optional[SearchResponseItem] = None
    retrievalSteps: List[RetrievalStep] = []

class RetrieveRequest(BaseModel):
    itemId: str
    userId: Optional[str] = None
    timestamp: Optional[datetime] = None # Accept ISO string, convert to datetime

    @validator('timestamp', pre=True, always=True)
    def parse_timestamp(cls, value):
        if value is None:
            return datetime.utcnow() # Default to now if not provided
        if isinstance(value, datetime):
            return value
        try:
            return iso8601.parse_date(value)
        except iso8601.ParseError as e:
             raise ValueError(f"Invalid ISO 8601 timestamp format: {value}. Error: {e}")
        except Exception as e:
             raise ValueError(f"Error parsing timestamp '{value}': {e}")


class PlaceUpdateRequest(BaseModel):
    itemId: str
    userId: Optional[str] = None
    timestamp: Optional[datetime] = None # Accept ISO string, convert to datetime
    containerId: str
    position: Position

    @validator('timestamp', pre=True, always=True)
    def parse_timestamp(cls, value):
        if value is None:
            return datetime.utcnow() # Default to now if not provided
        if isinstance(value, datetime):
            return value
        try:
            return iso8601.parse_date(value)
        except iso8601.ParseError as e:
             raise ValueError(f"Invalid ISO 8601 timestamp format: {value}. Error: {e}")
        except Exception as e:
             raise ValueError(f"Error parsing timestamp '{value}': {e}")


class SuccessResponse(BaseModel):
    success: bool

# --- Waste Models ---

class WasteItemResponse(BaseModel):
    itemId: str
    name: str
    reason: str # "Expired", "Out of Uses"
    containerId: str
    position: Position

class WasteIdentifyResponse(BaseModel):
    success: bool
    wasteItems: List[WasteItemResponse]

class WasteReturnPlanRequest(BaseModel):
    undockingContainerId: str
    undockingDate: datetime # Expect ISO format
    maxWeight: float = Field(..., gt=0)

    @validator('undockingDate', pre=True, always=True)
    def parse_undocking_date(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return iso8601.parse_date(value)
        except iso8601.ParseError as e:
             raise ValueError(f"Invalid ISO 8601 date format: {value}. Error: {e}")
        except Exception as e:
             raise ValueError(f"Error parsing date '{value}': {e}")


class WasteReturnPlanStep(BaseModel):
    step: int
    itemId: str
    itemName: str
    fromContainer: str
    toContainer: str # Should always be the undockingContainerId

class WasteReturnManifestItem(BaseModel):
    itemId: str
    name: str
    reason: str

class WasteReturnManifest(BaseModel):
    undockingContainerId: str
    undockingDate: datetime # Return as datetime object
    returnItems: List[WasteReturnManifestItem]
    totalVolume: float
    totalWeight: float

class WasteReturnPlanResponse(BaseModel):
    success: bool
    returnPlan: List[WasteReturnPlanStep]
    retrievalSteps: List[RetrievalStep] # Steps to get the waste items out
    returnManifest: WasteReturnManifest

class WasteCompleteUndockingRequest(BaseModel):
    undockingContainerId: str
    timestamp: Optional[datetime] = None # Expect ISO format

    @validator('timestamp', pre=True, always=True)
    def parse_timestamp(cls, value):
        if value is None:
            return datetime.utcnow() # Default to now
        if isinstance(value, datetime):
            return value
        try:
            return iso8601.parse_date(value)
        except iso8601.ParseError as e:
             raise ValueError(f"Invalid ISO 8601 timestamp format: {value}. Error: {e}")
        except Exception as e:
             raise ValueError(f"Error parsing timestamp '{value}': {e}")

class WasteCompleteUndockingResponse(BaseModel):
    success: bool
    itemsRemoved: int

# --- Simulation Models ---

class SimulationItemUsage(BaseModel):
    itemId: Optional[str] = None
    name: Optional[str] = None

    @validator('name')
    def check_id_or_name(cls, name, values):
        if not values.get('itemId') and not name:
            raise ValueError('Either itemId or name must be provided for itemsToBeUsedPerDay')
        return name

class SimulationRequest(BaseModel):
    numOfDays: Optional[int] = Field(None, ge=1)
    toTimestamp: Optional[datetime] = None # Expect ISO format
    itemsToBeUsedPerDay: List[SimulationItemUsage] = []

    @validator('toTimestamp', pre=True, always=True)
    def parse_to_timestamp(cls, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return iso8601.parse_date(value)
        except iso8601.ParseError as e:
             raise ValueError(f"Invalid ISO 8601 timestamp format: {value}. Error: {e}")
        except Exception as e:
             raise ValueError(f"Error parsing timestamp '{value}': {e}")


    @validator('toTimestamp')
    def check_days_or_timestamp(cls, toTimestamp, values):
        if not values.get('numOfDays') and not toTimestamp:
            raise ValueError('Either numOfDays or toTimestamp must be provided')
        if values.get('numOfDays') and toTimestamp:
            raise ValueError('Provide either numOfDays or toTimestamp, not both')
        return toTimestamp

class SimulationItemChange(BaseModel):
    itemId: str
    name: str

class SimulationItemUsedChange(SimulationItemChange):
     remainingUses: Optional[int] # None if usageLimit was null

class SimulationChanges(BaseModel):
    itemsUsed: List[SimulationItemUsedChange]
    itemsExpired: List[SimulationItemChange]
    itemsDepletedToday: List[SimulationItemChange]

class SimulationResponse(BaseModel):
    success: bool
    newDate: datetime # Return current simulated date as datetime
    changes: SimulationChanges

# --- Import/Export Models ---

class ImportErrorDetail(BaseModel):
    row: Optional[int] = None # Row number in CSV (if applicable)
    message: str

class ImportResponse(BaseModel):
    success: bool
    itemsImported: Optional[int] = None # For items import
    containersImported: Optional[int] = None # For containers import
    errors: List[ImportErrorDetail]

# --- Logging Models ---

class LogDetail(BaseModel):
    fromContainer: Optional[str] = None
    toContainer: Optional[str] = None
    position: Optional[Position] = None
    fromPosition: Optional[Position] = None
    toPosition: Optional[Position] = None
    reason: Optional[str] = None
    remainingUses: Optional[int] = None
    fileType: Optional[str] = None
    count: Optional[int] = None
    errors: Optional[int] = None
    undockingContainerId: Optional[str] = None
    # Add any other specific details needed per action type

class LogResponseItem(BaseModel):
    timestamp: datetime
    userId: Optional[str] = None
    actionType: str # Enum value as string
    itemId: Optional[str] = None # Changed from itemId_fk
    details: Optional[Dict[str, Any]] = None # Keep as dict for flexibility, validate on creation

    class Config:
        orm_mode = True
        # Handle potential JSON string in details_json
        # json_encoders = {
        #     dict: lambda v: json.dumps(v) if isinstance(v, dict) else v,
        # }

class LogsResponse(BaseModel):
    logs: List[LogResponseItem]