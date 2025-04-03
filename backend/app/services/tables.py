# /app/services/tables.py

from sqlalchemy.orm import Session, contains_eager, subqueryload, aliased
from sqlalchemy import func, or_, and_, select, case
from typing import Optional, Tuple, List

# Import DB models and API schemas
from app.models_db import Item, Container, Placement, ItemStatus
from app.api.models_api_tables import (
    PaginationParams, BaseFilterParams, ItemFilterParams,
    ContainerApiSchema, ItemApiSchema
)

def get_containers_service(
    db: Session,
    pagination: PaginationParams,
    filters: BaseFilterParams
) -> Tuple[List[ContainerApiSchema], int]:
    """
    Fetches a paginated list of containers with counts, applying search filters.
    """
    # Base query
    query = db.query(Container)

    # --- Search ---
    if filters.search:
        search_term = f"%{filters.search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Container.containerId).ilike(search_term),
                func.lower(Container.zone).ilike(search_term)
                # Add more searchable fields if needed (e.g., name, type if added)
            )
        )

    # --- Total Count (before pagination) ---
    total_count = query.count()

    # --- Pagination ---
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)

    # --- Fetch Containers ---
    containers_db = query.all()

    # --- Prepare Response DTOs ---
    # We need counts per container. This can be done efficiently with subqueries
    # or less efficiently by iterating and querying per container (avoid if possible).
    # Let's try getting counts more directly if the ORM/DB supports it well,
    # otherwise, we might iterate or use a more complex single query.

    # Alternative: Subqueries for counts (generally more efficient)
    results = []
    for container in containers_db:
        # Count total items in this container
        item_count = db.query(func.count(Placement.id)).filter(Placement.containerId_fk == container.containerId).scalar()

        # Count expired items in this container
        expired_item_count = db.query(func.count(Placement.id))\
            .join(Item, Placement.itemId_fk == Item.itemId)\
            .filter(Placement.containerId_fk == container.containerId, Item.status == ItemStatus.WASTE_EXPIRED)\
            .scalar()

        container_dto = ContainerApiSchema(
            containerId=container.containerId,
            zone=container.zone,
            width=container.width,
            depth=container.depth,
            height=container.height,
            item_count=item_count or 0,
            expired_item_count=expired_item_count or 0,
        )
        results.append(container_dto)

    return results, total_count


def get_items_service(
    db: Session,
    pagination: PaginationParams,
    filters: ItemFilterParams
) -> Tuple[List[ItemApiSchema], int]:
    """
    Fetches a paginated list of items, applying search and specific filters.
    Includes placement information if available.
    """
    # --- Base Query with Joins ---
    # We need info from Item, Placement (optional), and Container (optional)
    # Use outer join to include items that are not placed
    query = db.query(
        Item,
        Placement.containerId_fk,
        Container.zone.label("currentZone") # Alias Container.zone to avoid name clash if needed elsewhere
    ).outerjoin(
        Placement, Item.itemId == Placement.itemId_fk
    ).outerjoin(
        Container, Placement.containerId_fk == Container.containerId
    )

    # --- Filtering ---
    if filters.status:
        query = query.filter(Item.status == filters.status)
    if filters.preferred_zone:
        # Handle empty string search for preferred_zone if needed
        if filters.preferred_zone == "":
             query = query.filter(or_(Item.preferredZone == "", Item.preferredZone == None))
        else:
            query = query.filter(Item.preferredZone == filters.preferred_zone)


    # --- Search ---
    if filters.search:
        search_term = f"%{filters.search.lower()}%"
        # Search across Item fields and related Container fields
        query = query.filter(
            or_(
                func.lower(Item.itemId).ilike(search_term),
                func.lower(Item.name).ilike(search_term),
                func.lower(Item.preferredZone).ilike(search_term),
                # Search containerId and zone only if item is placed (via Placement/Container join)
                and_(Placement.containerId_fk != None, func.lower(Placement.containerId_fk).ilike(search_term)),
                and_(Container.zone != None, func.lower(Container.zone).ilike(search_term)),
                # Add Item.category search here if added to model
            )
        )

    # --- Total Count (before pagination) ---
    # Need to be careful with count() after joins, sometimes requires distinct
    # Using count on the primary key of the main table (Item) is safer
    count_query = db.query(func.count(Item.id)).select_from(Item)
    # Re-apply joins and filters for the count query
    count_query = count_query.outerjoin(
        Placement, Item.itemId == Placement.itemId_fk
    ).outerjoin(
        Container, Placement.containerId_fk == Container.containerId
    )
    if filters.status:
        count_query = count_query.filter(Item.status == filters.status)
    if filters.preferred_zone:
         if filters.preferred_zone == "":
             count_query = count_query.filter(or_(Item.preferredZone == "", Item.preferredZone == None))
         else:
            count_query = count_query.filter(Item.preferredZone == filters.preferred_zone)
    if filters.search:
        search_term = f"%{filters.search.lower()}%"
        count_query = count_query.filter(
             or_(
                func.lower(Item.itemId).ilike(search_term),
                func.lower(Item.name).ilike(search_term),
                func.lower(Item.preferredZone).ilike(search_term),
                and_(Placement.containerId_fk != None, func.lower(Placement.containerId_fk).ilike(search_term)),
                and_(Container.zone != None, func.lower(Container.zone).ilike(search_term)),
            )
        )

    total_count = count_query.scalar() or 0


    # --- Ordering (Optional - add if needed, e.g., by name or priority) ---
    # query = query.order_by(Item.name) # Example ordering

    # --- Pagination ---
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)

    # --- Fetch Data ---
    results_db = query.all() # Returns tuples: (Item, containerId_fk, currentZone)

    # --- Prepare Response DTOs ---
    items_dto: List[ItemApiSchema] = []
    for item_db, container_id_fk, current_zone in results_db:
        item_dto = ItemApiSchema(
            itemId=item_db.itemId,
            name=item_db.name,
            containerId=container_id_fk, # Directly from the query result
            quantity=1, # As per assumption
            mass=item_db.mass,
            expiryDate=item_db.expiryDate,
            width=item_db.width,
            depth=item_db.depth,
            height=item_db.height,
            priority=item_db.priority,
            usageLimit=item_db.usageLimit,
            currentUses=item_db.currentUses,
            preferredZone=item_db.preferredZone,
            currentZone=current_zone, # Directly from the query result alias
            status=item_db.status,
            expired=(item_db.status == ItemStatus.WASTE_EXPIRED),
            depleted=(item_db.status == ItemStatus.WASTE_DEPLETED),
            # category=item_db.category # Add if exists
        )
        items_dto.append(item_dto)

    return items_dto, total_count