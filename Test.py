import sqlite3

# Function to generate schema from SQLite database
def generate_schema(db_file):
    # Establish connection to SQLite database
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # Query SQLite master table for schema information
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Print schema information
    for table in tables:
        table_name = table[0]
        table_schema = table[1]
        print(f"Table: {table_name}")
        print(table_schema)
        print("\n")

    # Close the connection
    connection.close()

# Example usage
generate_schema('./working/working.db')
