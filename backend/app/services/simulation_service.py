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

# Global variable to store the current simulation time (In-memory approach)
_CURRENT_SIMULATION_TIME = datetime.utcnow()

def get_current_simulation_time() -> datetime:
    """Gets the current simulated time."""
    global _CURRENT_SIMULATION_TIME
    return _CURRENT_SIMULATION_TIME

def _set_current_simulation_time(new_time: datetime):
    """Sets the current simulated time."""
    global _CURRENT_SIMULATION_TIME
    _CURRENT_SIMULATION_TIME = new_time

def simulate_time_passage(db: Session, request_data: SimulationRequest, user_id: Optional[str] = None) -> SimulationResponse:
    """
    Simulates the passage of time, updating item statuses and usage counts.
    """
    global _CURRENT_SIMULATION_TIME
    start_sim_time = _CURRENT_SIMULATION_TIME

    # Determine end time
    if request_data.numOfDays is not None:
        if request_data.numOfDays <= 0:
            raise ValueError("numOfDays must be positive.")
        end_sim_time = start_sim_time + timedelta(days=request_data.numOfDays)
        days_to_simulate = request_data.numOfDays
    elif request_data.toTimestamp is not None:
        if request_data.toTimestamp <= start_sim_time:
            raise ValueError("toTimestamp must be after the current simulation time.")
        end_sim_time = request_data.toTimestamp
        days_to_simulate = (end_sim_time - start_sim_time).days
        days_to_simulate += 1
    else:
        # Should be caught by Pydantic validation
        raise ValueError("Either numOfDays or toTimestamp is required.")

    logging.debug(f"Simulating from {start_sim_time.isoformat()} to {end_sim_time.isoformat()} ({days_to_simulate} days)")

    items_used_changes: List[SimulationItemUsedChange] = []
    items_expired_changes: List[SimulationItemChange] = []
    items_depleted_changes: List[SimulationItemChange] = []

    # --- Simulate day by day ---
    current_day_processing = start_sim_time
    for day_index in range(days_to_simulate):
        current_day_processing = start_sim_time + timedelta(days=day_index)
        day_start = current_day_processing.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1) - timedelta(microseconds=1)

        logging.debug(f"--- Simulating Day {day_index + 1}: {day_start.date()} ---")

        # 1. Process Items Used Today
        used_today_ids = set()
        items_to_use_query = [] # Collect item IDs/names to query efficiently
        for usage_request in request_data.itemsToBeUsedPerDay:
            if usage_request.itemId:
                items_to_use_query.append(DBItem.itemId == usage_request.itemId)
            elif usage_request.name:
                items_to_use_query.append(DBItem.name == usage_request.name)

        if items_to_use_query:
            from sqlalchemy import or_
            items_to_process_today = db.query(DBItem).filter(
                or_(*items_to_use_query),
                DBItem.status == ItemStatus.ACTIVE # Only use active items
            ).all()

            for item in items_to_process_today:
                if item.itemId in used_today_ids: continue # Prevent double counting if requested by ID and name

                remaining_uses = None
                was_depleted_this_step = False
                if item.usageLimit is not None:
                    item.currentUses += 1
                    remaining_uses = item.usageLimit - item.currentUses
                    if remaining_uses < 0: remaining_uses = 0 # Cap

                    if remaining_uses == 0 and item.status == ItemStatus.ACTIVE:
                        item.status = ItemStatus.WASTE_DEPLETED
                        was_depleted_this_step = True
                        depleted_change = SimulationItemChange(itemId=item.itemId, name=item.name)
                        # Avoid duplicates if depleted multiple times in simulation? Check if already added.
                        if not any(c.itemId == item.itemId for c in items_depleted_changes):
                            items_depleted_changes.append(depleted_change)

                        # Log depletion
                        create_log_entry(
                            db=db,
                            actionType=LogActionType.SIMULATION_DEPLETED,
                            itemId=item.itemId,
                            timestamp=current_day_processing, # Time within the day it happened
                            details={"reason": "Usage limit reached during simulation"}
                        )

                # Add to used list (even if depleted this step)
                used_change = SimulationItemUsedChange(
                    itemId=item.itemId, name=item.name, remainingUses=remaining_uses
                )
                # Avoid duplicates if used multiple times in simulation? Append always for now.
                items_used_changes.append(used_change)
                used_today_ids.add(item.itemId)

                # Log usage
                create_log_entry(
                    db=db,
                    actionType=LogActionType.SIMULATION_USE,
                    itemId=item.itemId,
                    timestamp=current_day_processing,
                    details={"remainingUses": remaining_uses, "status_after": item.status.value}
                )

        # 2. Check for Expiry Today (at the end of the simulated day)
        newly_expired_items = db.query(DBItem).filter(
            DBItem.status == ItemStatus.ACTIVE,
            DBItem.expiryDate != None,
            DBItem.expiryDate <= day_end # If expiry date is today or earlier
        ).all()

        for item in newly_expired_items:
            item.status = ItemStatus.WASTE_EXPIRED
            expired_change = SimulationItemChange(itemId=item.itemId, name=item.name)
            # Avoid duplicates if expired multiple times? Check if already added.
            if not any(c.itemId == item.itemId for c in items_expired_changes):
                items_expired_changes.append(expired_change)

            # Log expiry
            create_log_entry(
                db=db,
                actionType=LogActionType.SIMULATION_EXPIRED,
                itemId=item.itemId,
                timestamp=day_end, # Mark as expired at end of day
                details={"reason": f"Expiry date {item.expiryDate} reached during simulation"}
            )

        # Commit changes for the day
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logging.error(f"Error committing changes during simulation day {day_index + 1}: {e}", exc_info=True)
            raise ValueError(f"Simulation failed during day {day_index + 1}: {e}")

    # Update global simulation time *after* loop finishes successfully
    _set_current_simulation_time(end_sim_time)

    changes = SimulationChanges(
        itemsUsed=items_used_changes,
        itemsExpired=items_expired_changes,
        itemsDepletedToday=items_depleted_changes # Renamed from API spec for clarity
    )

    return SimulationResponse(
        success=True,
        newDate=end_sim_time, # Return the final simulation time
        changes=changes
    )