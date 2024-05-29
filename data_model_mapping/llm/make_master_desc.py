import psycopg2
import pandas as pd
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

try:
    # Connect to the database
    conn = psycopg2.connect(
        host=connection_info["host"],
        user=connection_info["user"],
        password=connection_info["password"],
        dbname=connection_info["database"],
        port=connection_info["port"]
    )
    cursor = conn.cursor()
    
    # Fetch all data from data_model_master
    cursor.execute("SELECT * FROM data_model_master")
    rows = cursor.fetchall()
    
    # Get column names
    colnames = [desc[0] for desc in cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=colnames)
    
    # Replace '#' with '1' in the DataFrame
    df = df.replace('#', '1', regex=True)
    
    # List of properties that require '1' to be replaced with '2'
    special_properties = [
        'CurrentA', 'CurrentB', 'FrequencyA', 'FrequencyB', 
        'VoltageA', 'VoltageB', 'GenPowerA', 'GenPowerB'
    ]
    
    # Replace '1' with '2' for specific properties
    for prop in special_properties:
        df.loc[df['property'] == prop, 'thing'] = df.loc[df['property'] == prop, 'thing'].str.replace('1', '2')
    
    # Add a new column for tag_description
    df['tag_description'] = None

    # Query to fetch the tag_description from data_mapping
    query = """
    SELECT thing, property, tag_description
    FROM data_mapping
    WHERE ships_idx BETWEEN 1000 AND 1100
    ORDER BY ships_idx DESC
    """
    cursor.execute(query)
    mapping_rows = cursor.fetchall()
    
    # Create a dictionary to store the largest ships_idx tag_description for each (thing, property)
    tag_description_dict = {}
    for row in mapping_rows:
        thing, property, tag_description = row
        key = (thing, property)
        if key not in tag_description_dict:
            tag_description_dict[key] = tag_description

    # Update the DataFrame with the tag_description
    for index, row in df.iterrows():
        key = (row['thing'], row['property'])
        if key in tag_description_dict:
            df.at[index, 'tag_description'] = tag_description_dict[key]
    
    # Sort the DataFrame by ships_count in descending order
    df_sorted = df.sort_values(by='ships_count', ascending=False)
    
    # Define the path to save the CSV file
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_desc.csv')
    
    # Save the DataFrame to a CSV file
    df_sorted.to_csv(output_path, index=False)
    
    # Close the cursor and connection
    cursor.close()
    conn.close()
    
    print(f"DataFrame has been sorted and saved to {output_path}")
    
except Exception as e:
    print(f"An error occurred: {e}")
