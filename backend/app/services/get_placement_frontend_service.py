from typing import List, Dict, Any, Tuple
from ..models_db import Container, Item, Placement
from app.api.models_api_frontend import ContainerFrontendResponse, ItemFrontendResponse, PlacementFrontendResponse

class PlacementFrontendService:
    """Service for retrieving placement information formatted for the frontend."""
    
    @staticmethod
    def get_all_placements_frontend(db_session) -> PlacementFrontendResponse:
        """
        Get all containers and their placed items in a format matching the frontend CSV.
        
        Args:
            db_session: Database session
            
        Returns:
            PlacementFrontendResponse: Object containing containers and items in frontend format
        """
        # Get all containers
        containers = db_session.query(Container).all()
        
        # Get all items with placements
        items_with_placements = (
            db_session.query(Item, Placement, Container)
            .join(Placement, Item.itemId == Placement.itemId_fk)
            .join(Container, Placement.containerId_fk == Container.containerId)
            .all()
        )
        
        # Format containers for response
        container_responses = []
        for container in containers:
            container_responses.append(
                ContainerFrontendResponse(
                    id=container.containerId,
                    name=container.containerId,  # Using containerId as name
                    zoneId=container.zone,
                    width=container.width,
                    depth=container.depth,
                    height=container.height,
                    # Adding default spatial coordinates
                    start_width=0.0,
                    start_depth=0.0,
                    start_height=0.0,
                    end_width=container.width,
                    end_depth=container.depth,
                    end_height=container.height
                )
            )
        
        # Format items for response
        item_responses = []
        for item, placement, container in items_with_placements:
            item_responses.append(
                ItemFrontendResponse(
                    id=item.itemId,
                    name=item.name,
                    containerId=container.containerId,
                    mass=item.mass,
                    expirationDate=item.expiryDate,
                    width=item.width,
                    depth=item.depth,
                    height=item.height,
                    priority=item.priority,
                    usageLimit=item.usageLimit,
                    usageCount=item.currentUses,
                    preferredZone=item.preferredZone,
                    position_start_width=placement.start_w,
                    position_start_depth=placement.start_d,
                    position_start_height=placement.start_h,
                    position_end_width=placement.end_w,
                    position_end_depth=placement.end_d,
                    position_end_height=placement.end_h
                )
            )
        
        return PlacementFrontendResponse(
            containers=container_responses,
            items=item_responses
        )