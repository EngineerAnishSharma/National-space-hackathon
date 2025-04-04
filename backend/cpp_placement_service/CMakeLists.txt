cmake_minimum_required(VERSION 3.15) # Use a reasonably modern version

project(PlacementService LANGUAGES CXX)

# --- Compiler Settings ---
set(CMAKE_CXX_STANDARD 17) # Require C++17
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF) # Prefer not to use compiler-specific extensions

# --- Find Dependencies ---

# Find the PostgreSQL C++ library (libpqxx)
# This might need adjustment based on how/where libpqxx was installed
find_package(PostgreSQL REQUIRED) # Finds libpq first
find_package(PkgConfig REQUIRED)
pkg_check_modules(PQXX REQUIRED libpqxx)

# --- Project Configuration ---

# Tell CMake where to find our header files
include_directories(include)

# --- Define Executable ---
add_executable(placement_worker
    src/main.cpp
    src/placement_logic.cpp
)

# --- Link Libraries ---
target_link_libraries(placement_worker PRIVATE
    ${PostgreSQL_LIBRARIES}   # Link libpq
    ${PQXX_LIBRARIES}       # Link libpqxx
)

# Optional: Add include directories from dependencies if needed (often handled by pkg-config)
# target_include_directories(placement_worker PRIVATE
#     ${PostgreSQL_INCLUDE_DIRS}
#     ${PQXX_INCLUDE_DIRS}
# )


# --- Installation (Optional) ---
# install(TARGETS placement_worker DESTINATION bin)

# --- Output ---
message(STATUS "Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "Using libpq include dirs: ${PostgreSQL_INCLUDE_DIRS}")
message(STATUS "Using libpq libraries: ${PostgreSQL_LIBRARIES}")
message(STATUS "Using libpqxx include dirs: ${PQXX_INCLUDE_DIRS}")
message(STATUS "Using libpqxx libraries: ${PQXX_LIBRARIES}")