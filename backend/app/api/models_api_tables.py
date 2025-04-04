# /app/models_api_tables.py

from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
import enum

# Import necessary enums from models_db
# Adjust path if needed
from app.models_db import ItemStatus

# --- Base Models for Pagination/Filtering ---

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    size: int = Field(10, ge=1, le=100, description="Number of items per page (1-100)")

class BaseFilterParams(BaseModel):
    search: Optional[str] = Field(None, description="Search term for relevant fields")

# --- Container Models ---

class ContainerApiSchema(BaseModel):
    id: str = Field(..., alias="containerId", description="Unique identifier of the container")
    zoneId: str = Field(..., alias="zone", description="Storage zone identifier")
    width: float
    depth: float
    height: float
    item_count: int = Field(..., description="Total number of items currently in the container")
    expired_item_count: int = Field(..., description="Number of expired items currently in the container")

    class Config:
        orm_mode = True # For Pydantic V1
        # from_attributes = True # For Pydantic V2+
        allow_population_by_field_name = True # Allow using 'containerId' and 'zone' during creation

class PaginatedContainerResponse(BaseModel):
    total: int = Field(..., description="Total number of containers matching the criteria")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    items: List[ContainerApiSchema] = Field(..., description="List of containers for the current page")

# --- Item Models ---

class ItemFilterParams(BaseFilterParams):
    status: Optional[ItemStatus] = Field(None, description="Filter by item status")
    preferred_zone: Optional[str] = Field(None, description="Filter by preferred storage zone")
    # Add other specific filters if needed

class ItemApiSchema(BaseModel):
    id: str = Field(..., alias="itemId", description="Unique identifier of the item")
    name: str
    # category: Optional[str] = None # Not in DB model, uncomment if added
    containerId: Optional[str] = Field(None, description="ID of the container holding the item, if placed")
    quantity: int = Field(1, description="Quantity of this specific item (always 1 based on model)")
    mass: float
    expirationDate: Optional[datetime] = Field(None, alias="expiryDate")
    width: float
    depth: float
    height: float
    priority: int
    usageLimit: Optional[int] = None
    currentUses: int
    preferredZone: Optional[str] = None
    currentZone: Optional[str] = Field(None, description="Current zone where the item is located, if placed")
    status: ItemStatus
    expired: bool = Field(..., description="True if status is WASTE_EXPIRED")
    depleted: bool = Field(..., description="True if status is WASTE_DEPLETED")

    class Config:
        from_attributes = True
        # from_attributes = True # For Pydantic V2+
        allow_population_by_field_name = True # Allow using 'itemId' and 'expiryDate'

class PaginatedItemResponse(BaseModel):
    total: int = Field(..., description="Total number of items matching the criteria")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    items: List[ItemApiSchema] = Field(..., description="List of items for the current page")