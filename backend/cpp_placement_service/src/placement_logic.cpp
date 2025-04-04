#include "placement_logic.h" // Include the header we just defined

#include <iostream> // For std::cerr, std::cout (debugging)
#include <vector>
#include <string>
#include <optional>
#include <cmath>      // For std::abs, std::round (maybe needed later)
#include <algorithm>  // For std::sort, std::find_if, etc.
#include <limits>     // For numeric limits
#include <set>        // Potentially useful for unique heights, etc.
#include <map>
#include <numeric>    // For std::accumulate (if needed)


namespace PlacementService {

// --- Helper Function Implementations ---

/**
 * @brief Checks if two 3D bounding boxes overlap.
 * @param pos1 Position of the first box.
 * @param pos2 Position of the second box.
 * @return True if the boxes overlap, false otherwise.
 */
bool boxes_overlap(const Position& pos1, const Position& pos2) {
    // Check for non-overlap along each axis using tolerance
    bool no_overlap_w = (pos1.endCoordinates.width <= pos2.startCoordinates.width + COORD_TOLERANCE) ||
                        (pos2.endCoordinates.width <= pos1.startCoordinates.width + COORD_TOLERANCE);

    bool no_overlap_d = (pos1.endCoordinates.depth <= pos2.startCoordinates.depth + COORD_TOLERANCE) ||
                        (pos2.endCoordinates.depth <= pos1.startCoordinates.depth + COORD_TOLERANCE);

    bool no_overlap_h = (pos1.endCoordinates.height <= pos2.startCoordinates.height + COORD_TOLERANCE) ||
                        (pos2.endCoordinates.height <= pos1.startCoordinates.height + COORD_TOLERANCE);

    // If there is no overlap along ANY axis, the boxes don't overlap overall
    return !(no_overlap_w || no_overlap_d || no_overlap_h);
}

/**
 * @brief Simplified stability check.
 * Checks if an item at the candidate position would be stable.
 * Rule: Must be on the floor (height ~ 0) OR the center of its base must be
 *       sufficiently supported by item(s) directly below it.
 *       (This is a basic check, a robust one needs % area calculation).
 * @param candidate_pos The position being checked.
 * @param container The container dimensions (for floor check).
 * @param current_placements_in_container Items already placed in the simulation.
 * @return True if considered stable, false otherwise.
 */
bool is_stable(const Position& candidate_pos,
               const ContainerData& container, // container might not be strictly needed if floor is always 0
               const std::vector<PlacementInfo>& current_placements_in_container)
{
    // Check if item is on the floor (start height is close to zero)
    if (std::abs(candidate_pos.startCoordinates.height) < COORD_TOLERANCE) {
        return true; // Stable if on the floor
    }

    // If not on the floor, check for support below
    bool supported = false;
    double candidate_base_center_w = candidate_pos.startCoordinates.width + (candidate_pos.endCoordinates.width - candidate_pos.startCoordinates.width) / 2.0;
    double candidate_base_center_d = candidate_pos.startCoordinates.depth + (candidate_pos.endCoordinates.depth - candidate_pos.startCoordinates.depth) / 2.0;

    for (const auto& existing_placement : current_placements_in_container) {
        // Is the top of the existing item directly below the candidate's base?
        if (std::abs(existing_placement.position.endCoordinates.height - candidate_pos.startCoordinates.height) < COORD_TOLERANCE) {
            // Does the center of the candidate's base lie horizontally within the bounds of the supporting item's top?
            bool center_within_w = (candidate_base_center_w >= existing_placement.position.startCoordinates.width - COORD_TOLERANCE) &&
                                   (candidate_base_center_w <= existing_placement.position.endCoordinates.width + COORD_TOLERANCE);
            bool center_within_d = (candidate_base_center_d >= existing_placement.position.startCoordinates.depth - COORD_TOLERANCE) &&
                                   (candidate_base_center_d <= existing_placement.position.endCoordinates.depth + COORD_TOLERANCE);

            if (center_within_w && center_within_d) {
                supported = true;
                 // Found at least one supporting item below the center.
                 // A real check would require significantly more overlap.
                break;
            }
        }
    }

    if (!supported) {
        // Optional: Add logging here if stability check fails often unexpectedly
        // std::cerr << "Stability check failed for item starting at height " << candidate_pos.startCoordinates.height << std::endl;
    }

    return supported; // Stable only if supported
}


// --- Placeholder for the main logic function (to be implemented next) ---
PlacementOutput suggest_placements_cpp(
    const std::vector<ItemData>& items_to_place,
    const std::vector<ContainerData>& containers,
    const std::map<std::string, std::vector<PlacementInfo>>& current_db_placements)
{
    std::cerr << "WARNING: suggest_placements_cpp is not fully implemented yet!" << std::endl;
    PlacementOutput output;
    output.success = false; // Mark as unsuccessful until implemented
    output.error = "Placement logic not implemented";

    // TODO: Implement the multi-phase placement logic here, similar to the Python version.
    // Phase 0: Initialize simulation state from current_db_placements
    // Phase 1: Attempt placement of items_to_place (high priority first) in preferred zones
    // Phase 2: Handle rearrangements for high-priority items that couldn't fit
    // Phase 3: Attempt final placement for any remaining items
    // Phase 4: Collate results into output.placements, output.rearrangements, output.failedItemIds

    return output;
}

// --- Placeholder for the single-item placement function (to be implemented next) ---
std::optional<std::tuple<Position, Orientation>> find_spot_in_container(
    const ItemData& item_req,
    const ContainerData& container,
    const std::vector<PlacementInfo>& current_placements_in_container,
    bool is_high_priority)
{
     std::cerr << "WARNING: find_spot_in_container is not fully implemented yet!" << std::endl;

    // TODO: Implement the logic to iterate through orientations and potential
    // start coordinates (w, d, h) within the container, checking for
    // boundaries, overlaps (using boxes_overlap), and stability (using is_stable).
    // Return the Position and Orientation if a valid spot is found.

    return std::nullopt; // Return empty optional if no spot found
}

bool boxes_overlap(const Position& pos1, const Position& pos2) {
    // Check for non-overlap along each axis using tolerance
    bool no_overlap_w = (pos1.endCoordinates.width <= pos2.startCoordinates.width + COORD_TOLERANCE) ||
                        (pos2.endCoordinates.width <= pos1.startCoordinates.width + COORD_TOLERANCE);

    bool no_overlap_d = (pos1.endCoordinates.depth <= pos2.startCoordinates.depth + COORD_TOLERANCE) ||
                        (pos2.endCoordinates.depth <= pos1.startCoordinates.depth + COORD_TOLERANCE);

    bool no_overlap_h = (pos1.endCoordinates.height <= pos2.startCoordinates.height + COORD_TOLERANCE) ||
                        (pos2.endCoordinates.height <= pos1.startCoordinates.height + COORD_TOLERANCE);

    // If there is no overlap along ANY axis, the boxes don't overlap overall
    return !(no_overlap_w || no_overlap_d || no_overlap_h);
}


bool is_stable(const Position& candidate_pos,
               const ContainerData& container, // container might not be strictly needed if floor is always 0
               const std::vector<PlacementInfo>& current_placements_in_container)
{
    // Check if item is on the floor (start height is close to zero)
    if (std::abs(candidate_pos.startCoordinates.height) < COORD_TOLERANCE) {
        return true; // Stable if on the floor
    }

    // If not on the floor, check for support below
    bool supported = false;
    // More robust check: Check if *any* part of the base is supported by something below
    // Simplified check from Python: Is the start height exactly matching the end height of *any* item below?
    // Let's stick to the simplified check for now, matching Python's apparent logic.

    for (const auto& existing_placement : current_placements_in_container) {
        // Is the top of the existing item directly below the candidate's base?
        if (std::abs(existing_placement.position.endCoordinates.height - candidate_pos.startCoordinates.height) < COORD_TOLERANCE) {
            // Check for *any* horizontal overlap (W-D plane)
             bool overlap_w = !(candidate_pos.endCoordinates.width <= existing_placement.position.startCoordinates.width + COORD_TOLERANCE ||
                                existing_placement.position.endCoordinates.width <= candidate_pos.startCoordinates.width + COORD_TOLERANCE);
             bool overlap_d = !(candidate_pos.endCoordinates.depth <= existing_placement.position.startCoordinates.depth + COORD_TOLERANCE ||
                                existing_placement.position.endCoordinates.depth <= candidate_pos.startCoordinates.depth + COORD_TOLERANCE);

            if (overlap_w && overlap_d) {
                supported = true;
                // Found at least one supporting item with some overlap.
                break; // Sufficient support found
            }
        }
    }
    return supported; // Stable only if on floor or supported
}

// --- Implementation of find_spot_in_container ---

/**
 * @brief Tries to find a valid placement spot for an item within a container.
 * Iterates through orientations and potential starting points.
 * @param item_req The item to place.
 * @param container The container to place into.
 * @param current_placements_in_container Simulation state of items already in this container.
 * @param is_high_priority Hint for placement strategy (front-low depth vs back-high depth).
 * @return Optional containing the found Position and Orientation, or std::nullopt if no spot found.
 */
std::optional<std::tuple<Position, Orientation>> find_spot_in_container(
    const ItemData& item_req,
    const ContainerData& container,
    const std::vector<PlacementInfo>& current_placements_in_container,
    bool is_high_priority)
{
    // Possible orientations (width, depth, height) - 6 permutations
    const std::vector<Orientation> orientations = {
        {item_req.width, item_req.depth, item_req.height}, {item_req.width, item_req.height, item_req.depth},
        {item_req.depth, item_req.width, item_req.height}, {item_req.depth, item_req.height, item_req.width},
        {item_req.height, item_req.width, item_req.depth}, {item_req.height, item_req.depth, item_req.width},
    };

    // Determine search grid granularity (adjust these for performance/accuracy trade-off)
    // Smaller increments = more thorough but slower.
    const double width_increment = std::max(container.width / 25.0, 0.02); // e.g., 2cm or 1/25th width
    const double depth_increment = std::max(container.depth / 25.0, 0.02);
    const int num_w_steps = static_cast<int>(container.width / width_increment) + 2;
    const int num_d_steps = static_cast<int>(container.depth / depth_increment) + 2;

    // Define possible base heights: floor (0.0) and tops of existing items
    std::set<double> base_height_set;
    base_height_set.insert(0.0);
    for(const auto& placed_item : current_placements_in_container) {
        // Use a tolerance when inserting heights to avoid near-duplicates
        bool found_close = false;
        for(double h : base_height_set) {
            if (std::abs(placed_item.position.endCoordinates.height - h) < COORD_TOLERANCE * 10) {
                found_close = true;
                break;
            }
        }
        if (!found_close) {
             base_height_set.insert(placed_item.position.endCoordinates.height);
        }
    }
    // Convert set to sorted vector for ordered iteration
    std::vector<double> possible_base_heights(base_height_set.begin(), base_height_set.end());
    // Sort is guaranteed by set, but explicit sort doesn't hurt if set wasn't used
    // std::sort(possible_base_heights.begin(), possible_base_heights.end());


    // --- Iterate through orientations ---
    for (const auto& orientation : orientations) {
        double item_w = std::get<0>(orientation);
        double item_d = std::get<1>(orientation);
        double item_h = std::get<2>(orientation);

        // Basic check: Does this orientation fit within the container *at all*?
        if (item_w > container.width + COORD_TOLERANCE ||
            item_d > container.depth + COORD_TOLERANCE ||
            item_h > container.height + COORD_TOLERANCE) {
            continue; // Try next orientation
        }

        // --- Iterate through potential starting points (Height -> Depth -> Width) ---

        // 1. Iterate through possible base heights (floor first)
        for (double start_h : possible_base_heights) {
            // Check height boundary early
            if (start_h + item_h > container.height + COORD_TOLERANCE) {
                continue; // Item won't fit vertically from this base height
            }

            // 2. Iterate through depth positions
            for (int d_idx = 0; d_idx < num_d_steps; ++d_idx) {
                // Adjust depth iteration order based on priority
                double start_d = (is_high_priority)
                               ? (d_idx * depth_increment) // High priority: try front first
                               : (container.depth - (d_idx + 1) * depth_increment); // Low priority: try back first

                // Clamp start_d to valid range [0, container.depth - item_d]
                 start_d = std::max(0.0, std::min(start_d, container.depth - item_d));
                 if (start_d + item_d > container.depth + COORD_TOLERANCE) continue; // Check depth boundary


                // 3. Iterate through width positions
                for (int w_idx = 0; w_idx < num_w_steps; ++w_idx) {
                    double start_w = w_idx * width_increment;

                     // Clamp start_w to valid range [0, container.width - item_w]
                     start_w = std::max(0.0, std::min(start_w, container.width - item_w));
                     if (start_w + item_w > container.width + COORD_TOLERANCE) continue; // Check width boundary

                    // --- Candidate Spot Found - Validate ---
                    Position candidate_pos;
                    candidate_pos.startCoordinates = {start_w, start_d, start_h};
                    candidate_pos.endCoordinates = {start_w + item_w, start_d + item_d, start_h + item_h};

                    // 1. Precise Boundary Check (Redundant due to clamping/checks above, but good sanity check)
                    if (candidate_pos.endCoordinates.width > container.width + COORD_TOLERANCE ||
                        candidate_pos.endCoordinates.depth > container.depth + COORD_TOLERANCE ||
                        candidate_pos.endCoordinates.height > container.height + COORD_TOLERANCE) {
                        continue;
                    }

                    // 2. Overlap Check (compare against ALL other items currently placed)
                    bool overlaps = false;
                    for (const auto& existing_placement : current_placements_in_container) {
                        if (boxes_overlap(candidate_pos, existing_placement.position)) {
                            overlaps = true;
                            break; // No need to check further items if overlap found
                        }
                    }
                    if (overlaps) {
                        continue; // Try the next potential spot
                    }

                    // 3. Stability Check
                    if (!is_stable(candidate_pos, container, current_placements_in_container)) {
                        continue; // Skip unstable positions
                    }

                    // --- All Checks Passed: Valid Spot Found! ---
                    // std::cout << "  Found spot for " << item_req.itemId << " in " << container.containerId
                    //           << " Ori(" << item_w << "," << item_d << "," << item_h << ")"
                    //           << " at (" << std::fixed << std::setprecision(3) << start_w << "," << start_d << "," << start_h << ")" << std::endl;
                    return std::make_tuple(candidate_pos, orientation);

                } // End width loop
            } // End depth loop
        } // End height loop
    } // End orientation loop

    // No suitable spot found in this container for any orientation/position
    // std::cout << "  No spot found for " << item_req.itemId << " in " << container.containerId << std::endl;
    return std::nullopt;
}


// --- Implementation of suggest_placements_cpp ---

PlacementOutput suggest_placements_cpp(
    const std::vector<ItemData>& items_to_place_input, // Items from the specific job request
    const std::vector<ContainerData>& containers_input, // Containers from the specific job request
    // Map: ContainerID -> Vector of items currently placed in it (read from LIVE placements table)
    const std::map<std::string, std::vector<PlacementInfo>>& current_db_placements)
{
    PlacementOutput output;
    output.success = true; // Assume success unless something fails

    // --- Phase 0: Initialization & Data Loading ---
    std::cout << "--- Phase 0: Initializing C++ Placement ---" << std::endl;

    // Copy input items and sort by priority (descending)
    std::vector<ItemData> sorted_incoming_items = items_to_place_input;
    std::sort(sorted_incoming_items.begin(), sorted_incoming_items.end(),
              [](const ItemData& a, const ItemData& b) {
                  return a.priority > b.priority; // Higher priority first
              });

    // Create easy lookup for container data
    std::map<std::string, ContainerData> containers_map;
    std::vector<std::string> container_ids; // Keep order or just for iteration
    for(const auto& c : containers_input) {
        containers_map[c.containerId] = c;
        container_ids.push_back(c.containerId);
    }

    // Initialize the in-memory simulation state from the current DB state
    // Map: ContainerID -> Vector of PlacementInfo for items in that container
    std::map<std::string, std::vector<PlacementInfo>> simulation_placements = current_db_placements;

    // Keep track of items processed (placed or failed)
    std::set<std::string> processed_item_ids;
    // Keep track of the final state of placements for the response (includes moves)
    // Map: ItemID -> PlacementResult
    std::map<std::string, PlacementResult> final_placements_map;

    // Add existing items from DB to the initial final_placements_map
     for(const auto& pair : current_db_placements) {
        const std::string& container_id = pair.first;
        for(const auto& placement_info : pair.second) {
             final_placements_map[placement_info.itemId] = {
                placement_info.itemId,
                container_id,
                placement_info.position
            };
        }
    }


    std::vector<ItemData> items_requiring_placement_pass_2; // Items needing non-preferred or rearrangement


    // --- Phase 1: Initial Placement Attempt (Preferred Zones First) ---
    std::cout << "--- Phase 1: Attempting Preferred Zone Placements ---" << std::endl;

    for (const auto& item_req : sorted_incoming_items) {
        if (processed_item_ids.count(item_req.itemId)) continue; // Skip if already handled

        std::cout << "Processing Item (Phase 1): " << item_req.itemId << " (Prio: " << item_req.priority << ")" << std::endl;
        bool placed_in_phase1 = false;
        bool is_high_prio = item_req.priority >= 75; // Define your high priority threshold

        if (item_req.preferredZone.has_value()) {
            const std::string& pref_zone = item_req.preferredZone.value();
            // Find containers in the preferred zone
            for (const std::string& container_id : container_ids) {
                const auto& container = containers_map[container_id];
                if (container.zone == pref_zone) {
                    // Get current items in this simulation container
                    const std::vector<PlacementInfo>& current_in_container = simulation_placements[container_id]; // operator[] creates if not exists

                    // Try to find a spot
                    auto spot_result = find_spot_in_container(item_req, container, current_in_container, is_high_prio);

                    if (spot_result.has_value()) {
                        const auto& [found_pos, found_ori] = spot_result.value();

                        // Update Simulation State
                        simulation_placements[container_id].push_back({
                            item_req.itemId,
                            container_id, // Add container ID here
                            found_pos,
                            item_req.priority // Add priority here
                        });

                        // Update Final Placements Map
                        final_placements_map[item_req.itemId] = {item_req.itemId, container_id, found_pos};

                        processed_item_ids.insert(item_req.itemId);
                        std::cout << "  SUCCESS (Phase 1): Placed " << item_req.itemId << " in preferred " << container_id << std::endl;
                        placed_in_phase1 = true;
                        break; // Placed in preferred zone, move to next item
                    }
                }
            }
        } // End if has preferredZone

        if (!placed_in_phase1) {
             std::cout << "  INFO (Phase 1): Could not place " << item_req.itemId << " in preferred zone. Queued for later." << std::endl;
            items_requiring_placement_pass_2.push_back(item_req);
        }
    } // End Phase 1 loop


    // --- Phase 2: Rearrangement Simulation (Placeholder) ---
    std::cout << "--- Phase 2: Evaluating Rearrangements (Simplified/Placeholder) ---" << std::endl;
    // TODO: Implement detailed rearrangement logic. This is complex.
    // - Identify high-priority items from items_requiring_placement_pass_2.
    // - For each, check preferred containers again.
    // - If still no space, identify lower-priority items in the way within those containers.
    // - Try to find alternative spots for the lower-priority items in *other* containers.
    // - If successful, record the moves in output.rearrangements and update simulation_placements.
    // - Then, place the high-priority item in the freed spot.
    // - Update final_placements_map for all moved/placed items.
    // - Add any items that still couldn't be placed (even after trying rearrangement) to items_requiring_placement_pass_3.

    // For now, just move all Phase 2 items directly to Phase 3 list
    std::vector<ItemData> items_requiring_placement_pass_3 = items_requiring_placement_pass_2;
    items_requiring_placement_pass_2.clear(); // Clear the intermediate list

    if (!items_requiring_placement_pass_3.empty()) {
         std::cout << "  INFO (Phase 2): Skipping complex rearrangement logic for now. Items moved to final pass." << std::endl;
    }


    // --- Phase 3: Final Placement Attempt (Anywhere) ---
    std::cout << "--- Phase 3: Final Placement Attempt (Anywhere) ---" << std::endl;

    for (const auto& item_req : items_requiring_placement_pass_3) {
         if (processed_item_ids.count(item_req.itemId)) continue; // Should have been handled if placed in Phase 2

         std::cout << "Processing Item (Phase 3): " << item_req.itemId << std::endl;
         bool placed_in_phase3 = false;
         bool is_high_prio = item_req.priority >= 75;

         // Try placing in *any* container
         for (const std::string& container_id : container_ids) {
             const auto& container = containers_map[container_id];
             const std::vector<PlacementInfo>& current_in_container = simulation_placements[container_id];

             auto spot_result = find_spot_in_container(item_req, container, current_in_container, is_high_prio);

             if (spot_result.has_value()) {
                 const auto& [found_pos, found_ori] = spot_result.value();

                 // Update Simulation State
                 simulation_placements[container_id].push_back({
                     item_req.itemId,
                     container_id,
                     found_pos,
                     item_req.priority
                 });

                 // Update Final Placements Map
                 final_placements_map[item_req.itemId] = {item_req.itemId, container_id, found_pos};

                 processed_item_ids.insert(item_req.itemId);
                 std::cout << "  SUCCESS (Phase 3): Placed " << item_req.itemId << " in non-preferred " << container_id << std::endl;
                 placed_in_phase3 = true;
                 break; // Placed, move to next item
             }
         } // End container loop for Phase 3

         if (!placed_in_phase3) {
             std::cerr << "  !!! PLACEMENT FAILED COMPLETELY for item " << item_req.itemId << " !!!" << std::endl;
             output.failedItemIds.push_back(item_req.itemId);
             processed_item_ids.insert(item_req.itemId); // Mark as processed (failed)
             output.success = false; // Overall success is false if any item fails
             if (!output.error.has_value()) {
                 output.error = "Placement failed for one or more items.";
             }
         }
    } // End Phase 3 loop


    // --- Phase 4: Format Output ---
    std::cout << "--- Phase 4: Formatting Output ---" << std::endl;

    // Populate final placements from the map
    output.placements.reserve(final_placements_map.size());
    for(const auto& pair : final_placements_map) {
        // Only include items that didn't fail completely
        bool failed = false;
        for(const auto& failed_id : output.failedItemIds) {
            if (pair.first == failed_id) {
                failed = true;
                break;
            }
        }
        if (!failed) {
            output.placements.push_back(pair.second);
        }
    }

    // TODO: Populate output.rearrangements when Phase 2 is implemented

    if (!output.failedItemIds.empty()) {
         std::string error_msg = "Placement incomplete. Failed items: ";
         for(size_t i = 0; i < output.failedItemIds.size(); ++i) {
             error_msg += output.failedItemIds[i] + (i == output.failedItemIds.size() - 1 ? "" : ", ");
         }
         output.error = error_msg;
         std::cerr << "WARNING: " << error_msg << std::endl;
    }

    std::cout << "--- C++ Placement Calculation Finished ---" << std::endl;
    return output;
}


} // namespace PlacementService