# /app/utils/geometry.py
from app.models_api import Position, Coordinates # Use API models for consistency here

def get_orientations(w: float, d: float, h: float):
    """Generates the 6 possible orientations (width, depth, height) of a cuboid."""
    return [
        (w, d, h), (w, h, d),
        (d, w, h), (d, h, w),
        (h, w, d), (h, d, w)
    ]

def check_overlap(pos1: Position, pos2: Position) -> bool:
    """
    Checks if two 3D bounding boxes defined by Pydantic Position models overlap.
    Assumes coordinates are relative to the same origin.
    """
    # Check for non-overlap along each axis
    no_overlap_w = pos1.endCoordinates.width <= pos2.startCoordinates.width or \
                   pos1.startCoordinates.width >= pos2.endCoordinates.width
    no_overlap_d = pos1.endCoordinates.depth <= pos2.startCoordinates.depth or \
                   pos1.startCoordinates.depth >= pos2.endCoordinates.depth
    no_overlap_h = pos1.endCoordinates.height <= pos2.startCoordinates.height or \
                   pos1.startCoordinates.height >= pos2.endCoordinates.height

    # If there is no overlap on ANY axis, the boxes do not overlap
    # Therefore, they overlap if there IS overlap on ALL axes
    return not (no_overlap_w or no_overlap_d or no_overlap_h)

def check_bounds(item_pos: Position, container_dims: Coordinates) -> bool:
    """Checks if the item position is fully within the container dimensions."""
    fits_w = item_pos.startCoordinates.width >= 0 and item_pos.endCoordinates.width <= container_dims.width
    fits_d = item_pos.startCoordinates.depth >= 0 and item_pos.endCoordinates.depth <= container_dims.depth
    fits_h = item_pos.startCoordinates.height >= 0 and item_pos.endCoordinates.height <= container_dims.height
    return fits_w and fits_d and fits_h

def calculate_volume(position: Position) -> float:
    """Calculates the volume of a bounding box."""
    width = position.endCoordinates.width - position.startCoordinates.width
    depth = position.endCoordinates.depth - position.startCoordinates.depth
    height = position.endCoordinates.height - position.startCoordinates.height
    return width * depth * height

def does_block(blocker_pos: Position, target_pos: Position) -> bool:
    """
    Checks if 'blocker_pos' blocks the direct retrieval path of 'target_pos'.
    Retrieval is straight out along the depth axis towards depth=0.
    The blocker blocks if it overlaps the target's footprint and is closer to the opening (smaller depth coordinates).
    """
    # 1. Check if they overlap in the Width and Height dimensions (footprint overlap)
    overlap_w = not (blocker_pos.endCoordinates.width <= target_pos.startCoordinates.width or
                     blocker_pos.startCoordinates.width >= target_pos.endCoordinates.width)
    overlap_h = not (blocker_pos.endCoordinates.height <= target_pos.startCoordinates.height or
                     blocker_pos.startCoordinates.height >= target_pos.endCoordinates.height)

    if not (overlap_w and overlap_h):
        return False # No footprint overlap, cannot block path

    # 2. Check if the blocker is positioned in front of the target (closer to depth=0)
    # The blocker must end at a depth less than or equal to the target's starting depth.
    is_in_front = blocker_pos.endCoordinates.depth <= target_pos.startCoordinates.depth

    return is_in_front