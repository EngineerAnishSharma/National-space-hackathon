from operator import or_
from sqlite3 import IntegrityError
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from app.models_db import Item as DBItem, LogActionType, ItemStatus
from app.models_api import (SimulationRequest, SimulationResponse, SimulationChanges,
                            SimulationItemChange, SimulationItemUsedChange)
from .logging_service import create_log_entry
from datetime import datetime, timedelta
import logging

# Configure logging (you can customize this)
logging.basicConfig(level=logging.DEBUG)

# Global simulation time
_CURRENT_SIMULATION_TIME = datetime.utcnow()

def get_current_simulation_time() -> datetime:
    return _CURRENT_SIMULATION_TIME

def _set_current_simulation_time(new_time: datetime):
    global _CURRENT_SIMULATION_TIME
    _CURRENT_SIMULATION_TIME = new_time

def simulate_time_passage(db: Session, request_data: SimulationRequest, user_id: Optional[str] = None) -> SimulationResponse:
    global _CURRENT_SIMULATION_TIME
    start_sim_time = _CURRENT_SIMULATION_TIME

    # Determine end simulation time
    if request_data.numOfDays and request_data.numOfDays > 0:
        end_sim_time = start_sim_time + timedelta(days=request_data.numOfDays)
    elif request_data.toTimestamp and request_data.toTimestamp > start_sim_time:
        end_sim_time = request_data.toTimestamp
    else:
        raise ValueError("Either a valid numOfDays or future toTimestamp is required.")

    logging.debug(f"Simulating from {start_sim_time} to {end_sim_time}")

    items_used_changes: List[SimulationItemUsedChange] = []
    items_expired_changes: List[SimulationItemChange] = []
    items_depleted_changes: List[SimulationItemChange] = []

    # Optimize query: Fetch all relevant items at once
    item_filters = []
    for usage_request in request_data.itemsToBeUsedPerDay:
        if usage_request.itemId:
            item_filters.append(DBItem.itemId == usage_request.itemId)
        elif usage_request.name:
            item_filters.append(DBItem.name == usage_request.name)
    
    items_to_process = db.query(DBItem).filter(or_(*item_filters), DBItem.status == ItemStatus.ACTIVE).all()

    for current_day in range((end_sim_time - start_sim_time).days + 1):
        current_time = start_sim_time + timedelta(days=current_day)
        day_end = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Process item usage
        for item in items_to_process:
            if item.usageLimit is not None and item.currentUses < item.usageLimit:
                item.currentUses += 1
                remaining_uses = max(0, item.usageLimit - item.currentUses)
                if remaining_uses == 0:
                    item.status = ItemStatus.WASTE_DEPLETED
                    if not any(c.itemId == item.itemId for c in items_depleted_changes):
                        items_depleted_changes.append(SimulationItemChange(itemId=item.itemId, name=item.name))
                items_used_changes.append(SimulationItemUsedChange(itemId=item.itemId, name=item.name, remainingUses=remaining_uses))
                create_log_entry(db, LogActionType.SIMULATION_USE, item.itemId, current_time, {"remainingUses": remaining_uses})

        # Check for expired items
        expired_items = db.query(DBItem).filter(DBItem.status == ItemStatus.ACTIVE, DBItem.expiryDate <= day_end).all()
        for item in expired_items:
            item.status = ItemStatus.WASTE_EXPIRED
            if not any(c.itemId == item.itemId for c in items_expired_changes):
                items_expired_changes.append(SimulationItemChange(itemId=item.itemId, name=item.name))
            create_log_entry(db, LogActionType.SIMULATION_EXPIRED, item.itemId, day_end, {"reason": "Item expired"})

        # Commit daily changes
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            logging.error(f"Database commit error on day {current_day + 1}: {e}")
            raise ValueError("Simulation failed due to database error.")

    _set_current_simulation_time(end_sim_time)

    return SimulationResponse(success=True, newDate=end_sim_time, changes=SimulationChanges(
        itemsUsed=items_used_changes, itemsExpired=items_expired_changes, itemsDepletedToday=items_depleted_changes
    ))