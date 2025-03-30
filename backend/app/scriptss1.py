import sqlite3

conn = sqlite3.connect("./iss_cargo.db")  # Ensure correct path
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:", tables)