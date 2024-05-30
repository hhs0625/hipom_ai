import pandas as pd
import psycopg2
import os

# Function to read the db connection info
def read_db_connection_info(filename="../db_connection_info.txt"):
    connection_info = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            connection_info[key] = value
    return connection_info

# Load the connection info
connection_info = read_db_connection_info()

# Define the output CSV file path
output_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_model_master_export.csv')

# Connect to the database and export data to CSV
try:
    conn = psycopg2.connect(
        host=connection_info["host"],
        user=connection_info["user"],
        password=connection_info["password"],
        dbname=connection_info["database"],
        port=connection_info["port"]
    )
    cursor = conn.cursor()
    
    # Execute the query to fetch all data from data_model_master
    query = "SELECT * FROM data_model_master"
    cursor.execute(query)
    
    # Fetch all rows and get column names
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    
    # Convert to a pandas DataFrame
    df = pd.DataFrame(rows, columns=colnames)
    
    # Save the DataFrame to a CSV file
    df.to_csv(output_csv_path, index=False)

    # Close the cursor and connection
    cursor.close()
    conn.close()
    
    print(f"Data from data_model_master has been exported to {output_csv_path}")
    
except Exception as e:
    print(f"An error occurred: {e}")
