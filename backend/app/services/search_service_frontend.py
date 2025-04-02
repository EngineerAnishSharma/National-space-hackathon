from typing import List, Dict, Any, Set
from app.models_db import Item, Container, Placement
from app.api.models_api_search import SearchResult, SearchGroupedResults, SearchResponse

class SearchService:
    """Service for searching items, containers and zones."""
    
    @staticmethod
    def search_items(db_session, query: str, limit: int = 20) -> SearchResponse:
        """
        Dynamically search for items, containers, and zones based on a partial query string.
        This supports incremental character-by-character searching for autocomplete functionality.
        
        Args:
            db_session: Database session
            query: Search query string (even partial characters)
            limit: Maximum number of results per category (default: 20)
            
        Returns:
            SearchResponse object with grouped results
        """
        if not query or len(query.strip()) == 0:
            # Return empty results for empty queries
            return SearchResponse(
                query=query,
                results=SearchGroupedResults(),
                total_count=0
            )
            
        # Normalize query for case-insensitive search
        search_term = f"%{query.lower()}%"
        
        # Search for items by id, name, category
        matching_items = (
            db_session.query(Item, Placement, Container)
            .outerjoin(Placement, Item.itemId == Placement.itemId_fk)  # outer join to include items without placement
            .outerjoin(Container, Placement.containerId_fk == Container.containerId)  # outer join to include items without container
            .filter(
                # Match any of these fields
                (Item.itemId.ilike(search_term)) |
                (Item.name.ilike(search_term)) |
                (Item.preferredZone.ilike(search_term))
            )
            .limit(limit)
            .all()
        )
        
        # Search for containers by id
        matching_containers = (
            db_session.query(Container)
            .filter(Container.containerId.ilike(search_term))
            .limit(limit)
            .all()
        )
        
        # Search for zones (distinct zones from both Items and Containers)
        zones_from_items = (
            db_session.query(Item.preferredZone)
            .filter(
                (Item.preferredZone.ilike(search_term)) &
                (Item.preferredZone.isnot(None))
            )
            .distinct()
            .limit(limit)
            .all()
        )
        
        zones_from_containers = (
            db_session.query(Container.zone)
            .filter(Container.zone.ilike(search_term))
            .distinct()
            .limit(limit)
            .all()
        )
        
        # Process item results
        item_results = []
        seen_item_ids = set()
        
        for item, placement, container in matching_items:
            if item.itemId in seen_item_ids:
                continue
                
            seen_item_ids.add(item.itemId)
            container_id = placement.containerId_fk if placement else None
            
            item_results.append(
                SearchResult(
                    id=item.itemId,
                    name=item.name,
                    category="Maintenance Tools",  # Default as specified in requirements
                    containerId=container_id,
                    preferredZone=item.preferredZone,
                    type="item"
                )
            )
        
        # Process container results
        container_results = []
        seen_container_ids = set()
        
        for container in matching_containers:
            if container.containerId in seen_container_ids:
                continue
                
            seen_container_ids.add(container.containerId)
            
            container_results.append(
                SearchResult(
                    id=container.containerId,
                    name=container.containerId,  # Using ID as name
                    preferredZone=container.zone,
                    type="container"
                )
            )
        
        # Process zone results (merge from both sources)
        all_zones = set()
        for zone_tuple in zones_from_items:
            all_zones.add(zone_tuple[0])
        
        for zone_tuple in zones_from_containers:
            all_zones.add(zone_tuple[0])
        
        zone_results = [
            SearchResult(
                id=zone,
                name=zone,
                type="zone"
            )
            for zone in all_zones
        ]
        
        # Create grouped results
        grouped_results = SearchGroupedResults(
            items=item_results,
            containers=container_results,
            zones=zone_results
        )
        
        # Calculate total count
        total_count = len(item_results) + len(container_results) + len(zone_results)
        
        # Return formatted response
        return SearchResponse(
            query=query,
            results=grouped_results,
            total_count=total_count
        )