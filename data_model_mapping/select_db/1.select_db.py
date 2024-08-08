import psycopg2
import pandas as pd

# Function to read the db connection info
def read_db_connection_info(filename="../db_connection_info.txt"):
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
            # SQL query to select data with ships_idx between 1000 and 1999
            query = """
                SELECT * FROM data_mapping
                WHERE ships_idx BETWEEN 1000 AND 1999
            """
            # Execute the query
            cursor.execute(query)
            # Fetch all the results
            results = cursor.fetchall()
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            # Create a DataFrame from the results
            df = pd.DataFrame(results, columns=columns)
            # Save the DataFrame to a CSV file
            df.to_csv('select_db/data_mapping.csv', index=False, encoding='utf-8-sig')

    print("Data exported successfully to 'select_db/data_mapping.csv'")

except (Exception, psycopg2.DatabaseError) as error:
    print(f"An error occurred: {error}")
finally:
    if conn is not None:
        conn.close()
