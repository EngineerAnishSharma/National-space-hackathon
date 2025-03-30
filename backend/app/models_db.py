# /app/models_db.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class ItemStatus(str, enum.Enum):
    ACTIVE = "active"
    WASTE_EXPIRED = "expired"
    WASTE_DEPLETED = "depleted"
    DISPOSED = "disposed" # Item has been removed via undocking

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    itemId = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    width = Column(Float, nullable=False)
    depth = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    mass = Column(Float, nullable=False)
    priority = Column(Integer, nullable=False) # 0-100
    expiryDate = Column(DateTime, nullable=True) # Store as DateTime objects
    usageLimit = Column(Integer, nullable=True) # Max uses
    currentUses = Column(Integer, default=0, nullable=False) # Uses consumed
    preferredZone = Column(String, nullable=True)
    status = Column(Enum(ItemStatus), default=ItemStatus.ACTIVE, nullable=False)

    # Relationship to Placement (one-to-one or one-to-many if item can be in multiple places?)
    # Assuming one item instance exists in only one place at a time
    placement = relationship("Placement", back_populates="item", uselist=False, cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="item") # Item can have multiple log entries

class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    containerId = Column(String, unique=True, index=True, nullable=False)
    zone = Column(String, index=True, nullable=False)
    width = Column(Float, nullable=False)
    depth = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    # Could add max_weight, current_weight if needed later

    placements = relationship("Placement", back_populates="container", cascade="all, delete-orphan")

class Placement(Base):
    __tablename__ = "placements"

    id = Column(Integer, primary_key=True, index=True)
    itemId_fk = Column(String, ForeignKey("items.itemId"), nullable=False, unique=True) # Foreign key using the string itemId
    containerId_fk = Column(String, ForeignKey("containers.containerId"), nullable=False) # Foreign key using the string containerId

    # Store coordinates relative to the container's origin (bottom-left of open face)
    # These represent the placed orientation and position
    start_w = Column(Float, nullable=False) # Position along width axis
    start_d = Column(Float, nullable=False) # Position along depth axis
    start_h = Column(Float, nullable=False) # Position along height axis
    end_w = Column(Float, nullable=False)   # start_w + effective width in this orientation
    end_d = Column(Float, nullable=False)   # start_d + effective depth in this orientation
    end_h = Column(Float, nullable=False)   # start_h + effective height in this orientation

    item = relationship("Item", back_populates="placement")
    container = relationship("Container", back_populates="placements")

class LogActionType(str, enum.Enum):
    PLACEMENT = "placement"
    REARRANGEMENT = "rearrangement"
    RETRIEVAL = "retrieval" # Includes decrementing use count
    UPDATE_LOCATION = "update_location" # When astronaut places item back via /api/place
    DISPOSAL_PLAN = "disposal_plan" # Item added to a waste return plan
    DISPOSAL_COMPLETE = "disposal_complete" # Item removed after undocking
    SIMULATION_USE = "simulation_use"
    SIMULATION_EXPIRED = "simulation_expired"
    SIMULATION_DEPLETED = "simulation_depleted"
    IMPORT = "import"
    EXPORT = "export"


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    userId = Column(String, nullable=True, index=True) # Optional, as some actions are system-triggered
    actionType = Column(Enum(LogActionType), nullable=False, index=True)
    itemId_fk = Column(String, ForeignKey("items.itemId"), nullable=True, index=True) # Can be null for container import etc.
    details_json = Column(Text, nullable=True) # Store complex details as JSON string

    item = relationship("Item", back_populates="logs")

    # Example details structure (to be stored in details_json):
    # placement: {"containerId": "...", "position": {...}}
    # retrieval: {"containerId": "...", "position": {...}, "remainingUses": ...}
    # update_location: {"fromContainer": "...", "fromPosition": {...}, "toContainer": "...", "toPosition": {...}}
    # disposal_plan: {"undockingContainerId": "..."}
    # disposal_complete: {"undockingContainerId": "..."}
    # import: {"fileType": "items/containers", "count": N, "errors": M}
    # simulation_*: {"reason": "...", "relatedItemId": "..."}