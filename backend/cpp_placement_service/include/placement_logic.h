#ifndef PLACEMENT_LOGIC_H
#define PLACEMENT_LOGIC_H

#include <vector>
#include <string>
#include <optional>
#include <tuple>
#include <map>
#include <chrono> // For time points if needed
#include "json.hpp" // nlohmann/json

// Use nlohmann::json for convenience
using json = nlohmann::json;

namespace PlacementService {

// --- Constants ---
const double COORD_TOLERANCE = 1e-6; // Tolerance for floating point comparisons

// --- Data Structures (Mirroring Python API/DB Models) ---

struct Coordinates {
    double width = 0.0;
    double depth = 0.0;
    double height = 0.0;

    // For JSON serialization/deserialization with nlohmann/json
    NLOHMANN_DEFINE_TYPE_INTRUSIVE(Coordinates, width, depth, height)

    bool operator==(const Coordinates& other) const {
        return std::abs(width - other.width) < COORD_TOLERANCE &&
               std::abs(depth - other.depth) < COORD_TOLERANCE &&
               std::abs(height - other.height) < COORD_TOLERANCE;
    }
     bool operator!=(const Coordinates& other) const {
        return !(*this == other);
    }
};

struct Position {
    Coordinates startCoordinates;
    Coordinates endCoordinates;

    NLOHMANN_DEFINE_TYPE_INTRUSIVE(Position, startCoordinates, endCoordinates)

     bool operator==(const Position& other) const {
        return startCoordinates == other.startCoordinates &&
               endCoordinates == other.endCoordinates;
    }
    bool operator!=(const Position& other) const {
        return !(*this == other);
    }
};

// Represents an item's definition (from request or DB)
struct ItemData {
    std::string itemId;
    std::string name;
    double width = 0.0;
    double depth = 0.0;
    double height = 0.0;
    double mass = 0.0;
    int priority = 50;
    // Store dates as strings initially for simpler JSON parsing, convert if needed
    std::optional<std::string> expiryDate;
    std::optional<int> usageLimit;
    std::optional<std::string> preferredZone;
    // Add status, currentUses if needed by logic here

    // Basic JSON mapping (add other fields as needed)
    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(ItemData, itemId, name, width, depth, height, mass, priority, expiryDate, usageLimit, preferredZone)
};

// Represents a container's definition
struct ContainerData {
    std::string containerId;
    std::string zone;
    double width = 0.0; // Internal dimensions
    double depth = 0.0;
    double height = 0.0;

    NLOHMANN_DEFINE_TYPE_INTRUSIVE(ContainerData, containerId, zone, width, depth, height)
};

// Represents an item currently placed (read from DB or during simulation)
struct PlacementInfo {
    std::string itemId;
    std::string containerId;
    Position position;
    int priority = 50; // Keep priority handy for rearrangement logic
};

// Represents a proposed placement result to be written to DB
struct PlacementResult {
    std::string itemId;
    std::string containerId;
    Position position;
     NLOHMANN_DEFINE_TYPE_INTRUSIVE(PlacementResult, itemId, containerId, position) // For potential JSON logging
};

// Represents a rearrangement step result to be written to DB
struct RearrangementStep {
    int step = 0;
    std::string action; // e.g., "move"
    std::string itemId;
    std::optional<std::string> fromContainer;
    std::optional<Position> fromPosition;
    std::string toContainer;
    Position toPosition;
    // Define intrusive for potential JSON logging/debugging
    NLOHMANN_DEFINE_TYPE_INTRUSIVE(RearrangementStep, step, action, itemId, fromContainer, fromPosition, toContainer, toPosition)
};

// Final output of the placement calculation for a job
struct PlacementOutput {
    bool success = false;
    std::optional<std::string> error;
    std::vector<PlacementResult> placements;        // Placements for *all* items handled (new + moved)
    std::vector<RearrangementStep> rearrangements;  // Steps needed to achieve the placements
    std::vector<std::string> failedItemIds;         // Items that couldn't be placed at all
};

// Represents the dimensions (w, d, h) being used for an item in a specific orientation
using Orientation = std::tuple<double, double, double>;


// --- Core Logic Function Signature ---

PlacementOutput suggest_placements_cpp(
    const std::vector<ItemData>& items_to_place, // Items from the specific job request
    const std::vector<ContainerData>& containers, // Containers from the specific job request
    // Map: ContainerID -> Vector of items currently placed in it (read from LIVE placements table)
    const std::map<std::string, std::vector<PlacementInfo>>& current_db_placements
);


// --- Helper Function Signatures (Internal to placement logic) ---

bool boxes_overlap(const Position& pos1, const Position& pos2);

bool is_stable(const Position& candidate_pos,
               const ContainerData& container,
               const std::vector<PlacementInfo>& current_placements_in_container);

// Tries to find a spot for one item in one container, given current state
std::optional<std::tuple<Position, Orientation>> find_spot_in_container(
    const ItemData& item_req,
    const ContainerData& container,
    // Current simulation state for *this* container
    const std::vector<PlacementInfo>& current_placements_in_container,
    bool is_high_priority // Hint for placement strategy (e.g., front vs back)
);

} // namespace PlacementService

#endif // PLACEMENT_LOGIC_H