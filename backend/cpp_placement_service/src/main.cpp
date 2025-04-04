#include <iostream>
#include <string>
#include <vector>
#include <chrono>       // For std::chrono::seconds
#include <thread>       // For std::this_thread::sleep_for
#include <pqxx/pqxx>    // PostgreSQL C++ library
#include <stdexcept>    // For standard exceptions
#include <cstdlib>      // For std::getenv

// Include our project headers
#include "json.hpp"
#include "placement_logic.h"

// Use our namespace and json alias
using json = nlohmann::json;
using namespace PlacementService;

// --- Database Connection Configuration ---
// BEST PRACTICE: Read these from environment variables or a config file
//              Avoid hardcoding credentials in source code.
std::string get_db_connection_string() {
    const char* db_host = std::getenv("DB_HOST");
    const char* db_port = std::getenv("DB_PORT");
    const char* db_name = std::getenv("DB_NAME");
    const char* db_user = std::getenv("DB_USER");
    const char* db_pass = std::getenv("DB_PASSWORD"); // Be careful with passwords

    std::string connection_string = "";
    if (db_host) connection_string += "host=" + std::string(db_host) + " ";
    if (db_port) connection_string += "port=" + std::string(db_port) + " ";
    if (db_name) connection_string += "dbname=" + std::string(db_name) + " ";
    if (db_user) connection_string += "user=" + std::string(db_user) + " ";
    if (db_pass) connection_string += "password=" + std::string(db_pass) + " ";

    // Fallback to default if environment variables aren't set (for basic testing)
    if (connection_string.empty()) {
         std::cerr << "WARNING: DB connection environment variables (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD) not set. Using potentially insecure defaults." << std::endl;
        return "dbname=placement_db user=placement_user password=secret host=localhost port=5432";
    }
     // Remove trailing space if present
    if (!connection_string.empty() && connection_string.back() == ' ') {
        connection_string.pop_back();
    }
    return connection_string;
}


// --- Helper Function to Fetch Current Placements ---
std::map<std::string, std::vector<PlacementInfo>> fetch_current_placements(
    pqxx::work& txn, // Use existing transaction
    const std::vector<ContainerData>& relevant_containers)
{
    std::map<std::string, std::vector<PlacementInfo>> current_placements;
    if (relevant_containers.empty()) {
        return current_placements; // Nothing to fetch
    }

    std::cout << "  Fetching current placements for relevant containers..." << std::endl;

    // Construct IN clause string safely
    std::string container_id_list;
    for (size_t i = 0; i < relevant_containers.size(); ++i) {
        container_id_list += txn.quote(relevant_containers[i].containerId);
        if (i < relevant_containers.size() - 1) {
            container_id_list += ",";
        }
    }

    // Query to get placements AND the priority of the placed items
    // JOIN with items table to get priority. Assumes placement uses itemId_fk.
    std::string sql = R"(
        SELECT
            p.containerId_fk, p.itemId_fk,
            p.start_w, p.start_d, p.start_h,
            p.end_w, p.end_d, p.end_h,
            COALESCE(i.priority, 50) as priority -- Default priority if item somehow missing?
        FROM placements p
        LEFT JOIN items i ON p.itemId_fk = i.itemId
        WHERE p.containerId_fk IN ()" + container_id_list + R"();
    )";


    pqxx::result rows = txn.exec(sql);

    for (const auto& row : rows) {
        std::string container_id = row["containerId_fk"].as<std::string>();
        PlacementInfo info;
        info.itemId = row["itemId_fk"].as<std::string>();
        info.containerId = container_id; // Store container ID within PlacementInfo
        info.position.startCoordinates = {
            row["start_w"].as<double>(),
            row["start_d"].as<double>(),
            row["start_h"].as<double>()
        };
        info.position.endCoordinates = {
            row["end_w"].as<double>(),
            row["end_d"].as<double>(),
            row["end_h"].as<double>()
        };
        info.priority = row["priority"].as<int>();

        current_placements[container_id].push_back(info);
    }

    std::cout << "  Fetched " << rows.size() << " existing placement records." << std::endl;
    return current_placements;
}

// --- Helper Function to Store Results ---
void store_placement_results(
    pqxx::work& txn, // Use existing transaction
    const std::string& job_id,
    const PlacementOutput& results)
{
    std::cout << "  Storing results for job " << job_id << "..." << std::endl;

    // 1. Clear any previous results for this job (in case of retry)
     txn.exec0("DELETE FROM job_results_placements WHERE job_id = " + txn.quote(job_id));
     txn.exec0("DELETE FROM job_results_rearrangements WHERE job_id = " + txn.quote(job_id));


    // 2. Insert new placement results
    if (!results.placements.empty()) {
        std::string insert_placements_sql = R"(
            INSERT INTO job_results_placements (
                job_id, item_id_fk, container_id_fk,
                start_w, start_d, start_h, end_w, end_d, end_h
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);
        )";
        txn.prepare("insert_placement", insert_placements_sql);

        for (const auto& p : results.placements) {
            txn.exec_prepared("insert_placement",
                job_id, p.itemId, p.containerId,
                p.position.startCoordinates.width, p.position.startCoordinates.depth, p.position.startCoordinates.height,
                p.position.endCoordinates.width, p.position.endCoordinates.depth, p.position.endCoordinates.height
            );
        }
         std::cout << "    Stored " << results.placements.size() << " placement results." << std::endl;
    } else {
         std::cout << "    No successful placements to store." << std::endl;
    }

    // 3. Insert new rearrangement results
    if (!results.rearrangements.empty()) {
         std::string insert_rearrangements_sql = R"(
            INSERT INTO job_results_rearrangements (
                job_id, step, action, item_id,
                from_container,
                from_pos_start_w, from_pos_start_d, from_pos_start_h,
                from_pos_end_w, from_pos_end_d, from_pos_end_h,
                to_container,
                to_pos_start_w, to_pos_start_d, to_pos_start_h,
                to_pos_end_w, to_pos_end_d, to_pos_end_h
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18);
        )";
        txn.prepare("insert_rearrangement", insert_rearrangements_sql);

        for (const auto& r : results.rearrangements) {
            // Handle optional from_container and from_position
            std::optional<double> from_sw, from_sd, from_sh, from_ew, from_ed, from_eh;
             if (r.fromPosition.has_value()) {
                from_sw = r.fromPosition.value().startCoordinates.width;
                from_sd = r.fromPosition.value().startCoordinates.depth;
                from_sh = r.fromPosition.value().startCoordinates.height;
                from_ew = r.fromPosition.value().endCoordinates.width;
                from_ed = r.fromPosition.value().endCoordinates.depth;
                from_eh = r.fromPosition.value().endCoordinates.height;
            }

            txn.exec_prepared("insert_rearrangement",
                job_id, r.step, r.action, r.itemId,
                r.fromContainer, // Use optional directly (libpqxx handles null)
                from_sw, from_sd, from_sh, from_ew, from_ed, from_eh, // Optionals for position parts
                r.toContainer,
                r.toPosition.startCoordinates.width, r.toPosition.startCoordinates.depth, r.toPosition.startCoordinates.height,
                r.toPosition.endCoordinates.width, r.toPosition.endCoordinates.depth, r.toPosition.endCoordinates.height
            );
        }
         std::cout << "    Stored " << results.rearrangements.size() << " rearrangement steps." << std::endl;
    } else {
         std::cout << "    No rearrangement steps to store." << std::endl;
    }
}


// --- Main Processing Loop ---
int main() {
    std::cout << "Starting C++ Placement Service Worker..." << std::endl;

    std::string conn_string = get_db_connection_string();
    std::cout << "Connecting to database..." << std::endl; // Don't print password part of conn_string

    try {
        pqxx::connection conn(conn_string);
        std::cout << "Database connection successful: " << conn.dbname() << "@" << conn.hostname() << ":" << conn.port() << std::endl;

        while (true) { // Main polling loop
            std::string current_job_id;
            std::string request_data_str;
            bool job_found = false;

            try {
                // Use a single transaction for finding and processing a job
                pqxx::work txn(conn);

                // Query for one pending job, locking it to prevent other workers
                // Use FOR UPDATE SKIP LOCKED for better concurrency
                 std::cout << "\nPolling for pending jobs..." << std::endl;
                 pqxx::result res = txn.exec(R"(
                    SELECT job_id, request_data::text
                    FROM placement_jobs
                    WHERE status = 'PENDING'
                    ORDER BY created_at ASC
                    LIMIT 1
                    FOR UPDATE SKIP LOCKED;
                )");


                if (!res.empty()) {
                    current_job_id = res[0]["job_id"].as<std::string>();
                    request_data_str = res[0]["request_data"].as<std::string>();
                    job_found = true;
                    std::cout << "Found pending job: " << current_job_id << std::endl;

                    // Update status to PROCESSING immediately
                     txn.exec0(
                        "UPDATE placement_jobs SET status = 'PROCESSING', updated_at = NOW() WHERE job_id = " +
                        txn.quote(current_job_id)
                    );
                     std::cout << "  Marked job " << current_job_id << " as PROCESSING." << std::endl;

                } else {
                    std::cout << "No pending jobs found." << std::endl;
                }

                // Commit the status update (or the fact that no job was found)
                 txn.commit(); // Commit early after finding/updating status

            } catch (const std::exception& e) {
                 std::cerr << "ERROR during job polling/status update: " << e.what() << std::endl;
                 // Avoid hammering DB on persistent connection errors
                 std::this_thread::sleep_for(std::chrono::seconds(10));
                 continue; // Go back to start of loop
            }


            if (job_found) {
                PlacementOutput placement_results;
                bool processing_error = false;
                std::string error_message;

                try {
                     // Start a new transaction for the actual processing and result storage
                     pqxx::work process_txn(conn);

                     std::cout << "  Processing job " << current_job_id << "..." << std::endl;

                    // 1. Parse Request JSON
                     std::cout << "    Parsing request data..." << std::endl;
                     json request_json = json::parse(request_data_str);
                     std::vector<ItemData> request_items = request_json["items"].get<std::vector<ItemData>>();
                     std::vector<ContainerData> request_containers = request_json["containers"].get<std::vector<ContainerData>>();
                     std::cout << "    Parsed " << request_items.size() << " items and " << request_containers.size() << " containers from request." << std::endl;


                    // 2. Fetch Current State from DB
                     std::map<std::string, std::vector<PlacementInfo>> current_placements =
                         fetch_current_placements(process_txn, request_containers);


                    // 3. Call Core Placement Logic
                    std::cout << "    Calling suggest_placements_cpp..." << std::endl;
                    placement_results = suggest_placements_cpp(
                        request_items,
                        request_containers,
                        current_placements
                    );
                     std::cout << "    Placement calculation finished. Success: " << (placement_results.success ? "Yes" : "No") << std::endl;

                    // 4. Store Results in Job Result Tables
                    store_placement_results(process_txn, current_job_id, placement_results);


                    // 5. Update Job Status to COMPLETED or FAILED
                    std::string final_status = placement_results.success ? "COMPLETED" : "FAILED";
                     std::string update_sql = "UPDATE placement_jobs SET status = $1, error_message = $2, updated_at = NOW() WHERE job_id = $3";

                     // Use optional error message from results
                     std::optional<std::string> db_error_msg = placement_results.error;
                     process_txn.exec_params(update_sql, final_status, db_error_msg, current_job_id);

                     std::cout << "  Marked job " << current_job_id << " as " << final_status << "." << std::endl;

                    // 6. Commit the processing transaction
                     process_txn.commit();
                     std::cout << "  Committed results for job " << current_job_id << "." << std::endl;

                } catch (const json::parse_error& e) {
                    processing_error = true;
                    error_message = "JSON Parsing Error: " + std::string(e.what());
                    std::cerr << "ERROR processing job " << current_job_id << ": " << error_message << std::endl;
                } catch (const pqxx::sql_error& e) {
                     processing_error = true;
                     error_message = "Database SQL Error: " + std::string(e.what()) + " (Query: " + e.query() + ")";
                     std::cerr << "ERROR processing job " << current_job_id << ": " << error_message << std::endl;
                 } catch (const std::exception& e) {
                    processing_error = true;
                    error_message = "Generic Error: " + std::string(e.what());
                    std::cerr << "ERROR processing job " << current_job_id << ": " << error_message << std::endl;
                }

                // If an error occurred *during* processing, update the job status to FAILED outside the failed transaction
                 if (processing_error) {
                     try {
                         pqxx::work fail_txn(conn);
                         std::string update_sql = "UPDATE placement_jobs SET status = 'FAILED', error_message = $1, updated_at = NOW() WHERE job_id = $2";
                         fail_txn.exec_params(update_sql, error_message, current_job_id);
                         fail_txn.commit();
                         std::cerr << "  Marked job " << current_job_id << " as FAILED due to processing error." << std::endl;
                     } catch (const std::exception& db_e) {
                         std::cerr << "CRITICAL ERROR: Failed to even mark job " << current_job_id << " as FAILED in DB: " << db_e.what() << std::endl;
                         // Job might remain stuck in PROCESSING state
                     }
                 }
            } else {
                 // No job found, wait before polling again
                 std::this_thread::sleep_for(std::chrono::seconds(5)); // Adjust sleep time as needed
            }

        } // End while(true) loop

    } catch (const pqxx::broken_connection& e) {
        std::cerr << "FATAL: Database connection broken: " << e.what() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "FATAL: An unexpected error occurred: " << e.what() << std::endl;
        return 1;
    }

    std::cout << "Placement Service Worker shutting down." << std::endl;
    return 0;
}