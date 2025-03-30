import sqlite3
import os

# --- Configuration ---
db_filename = "iss_cargo.db"
db_filepath = os.path.join(os.getcwd(), db_filename) # Construct full path
# --- End Configuration ---

conn = None # Initialize connection variable

print(f"Attempting to connect to database file at: {db_filepath}")

if not os.path.exists(db_filepath):
    print(f"ERROR: Database file not found at '{db_filepath}'")
    exit() # Stop if the file doesn't exist

try:
    # Connect to the database
    conn = sqlite3.connect(db_filepath)
    cursor = conn.cursor()

    print("-" * 30)
    print("Inspecting Database Schema...")
    print("-" * 30)

    # 1. List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';") # Exclude internal sqlite tables
    tables = cursor.fetchall()

    if not tables:
        print("No user tables found in the database.")
    else:
        print("Tables found:", [table[0] for table in tables])
        print("-" * 30)

        # 2. For each table, get column information
        for table_tuple in tables:
            table_name = table_tuple[0]
            print(f"\nSchema for table: '{table_name}'")

            # Use PRAGMA table_info to get column details
            # PRAGMA doesn't typically support parameter substitution for the table name itself
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()

            if not columns:
                print("  (Could not retrieve column information)")
            else:
                # PRAGMA table_info returns tuples: (cid, name, type, notnull, dflt_value, pk)
                # cid: column id (0-based index)
                # name: column name
                # type: column data type (TEXT, INTEGER, REAL, etc.)
                # notnull: 1 if NOT NULL constraint exists, 0 otherwise
                # dflt_value: default value for the column
                # pk: 1 if this column is part of the primary key, 0 otherwise
                print(f"  Columns (Index, Name, Type, NotNull, DefaultValue, PrimaryKey):")
                for col in columns:
                    print(f"  - {col}")

except sqlite3.Error as e:
    print(f"\nAn error occurred: {e}")

finally:
    # Ensure the connection is closed even if errors occurred
    if conn:
        conn.close()
        print("\n" + "-" * 30)
        print("Database connection closed.")