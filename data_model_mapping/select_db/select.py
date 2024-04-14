import psycopg2

# Function to read the db connection info
def read_db_connection_info(filename="../../db_connection_info.txt"):
    connection_info = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                connection_info[key] = value
    except Exception as e:
        print(f"Failed to read database connection info: {e}")
        raise
    return connection_info

# Load the connection info
connection_info = read_db_connection_info()

try:
    # Connect to the database
    conn = psycopg2.connect(
        host=connection_info["host"],
        user=connection_info["user"],
        password=connection_info["password"],
        dbname=connection_info["database"],
        port=connection_info["port"]
    )
    # This ensures that resources are cleaned up properly
    with conn:
        with conn.cursor() as cursor:
            # SQL to copy the entire data_mapping table to a CSV file
            query = "COPY data_mapping TO STDOUT WITH CSV HEADER"
            # Path and name of the CSV file where the data will be saved
            with open('data_mapping.csv', 'w') as f:
                cursor.copy_expert(query, f)

    print("Data exported successfully to 'data_mapping.csv'")

except (Exception, psycopg2.DatabaseError) as error:
    print(f"An error occurred: {error}")
finally:
    if conn is not None:
        conn.close()

