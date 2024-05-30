import pandas as pd
import psycopg2
import os
import re

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

# Define the paths
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_desc_post.csv')

# Read the CSV file
df = pd.read_csv(csv_path)

# Connect to the database
try:
    conn = psycopg2.connect(
        host=connection_info["host"],
        user=connection_info["user"],
        password=connection_info["password"],
        dbname=connection_info["database"],
        port=connection_info["port"]
    )
    cursor = conn.cursor()
    
    not_found_entries = []

    # Iterate over each row in the dataframe
    for index, row in df.iterrows():
        thing = row['thing']
        property = row['property']
        desc = row['desc']
        
        # Check if the row exists
        cursor.execute("SELECT COUNT(*) FROM data_model_master WHERE thing = %s AND property = %s", (thing, property))
        count = cursor.fetchone()[0]

        if count == 0:
            not_found_entries.append((thing, property))
        else:
            # Update the database with the new desc value where thing and property match
            update_query = """
            UPDATE data_model_master
            SET data_desc = %s
            WHERE thing = %s AND property = %s
            """
            cursor.execute(update_query, (desc, thing, property))
    
    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    
    print(f"Database has been updated with the desc values from {csv_path}")
    
    # Print the entries that were not found
    if not_found_entries:
        print("The following thing, property combinations were not found in the database:")
        for thing, property in not_found_entries:
            print(f"Thing: {thing}, Property: {property}")

except Exception as e:
    print(f"An error occurred: {e}")
