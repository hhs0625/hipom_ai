import csv
import psycopg2

# Function to read the db connection info
def read_db_connection_info(filename="../../db_connection_info.txt"):
    connection_info = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            connection_info[key] = value
    return connection_info

# Function to read data from CSV file
def read_data_from_csv(csv_filepath):
    with open(csv_filepath, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        data = [tuple(row) for row in reader]  # Convert each row to a tuple
    return data

# Main function to read CSV and insert data into the database
def main(csv_filepath, connection_info):
    # Connect to the database
    conn = psycopg2.connect(
        host=connection_info["host"],
        user=connection_info["user"],
        password=connection_info["password"],
        dbname=connection_info["database"],
        port=connection_info["port"]
    )
    cursor = conn.cursor()

    # Read data from the CSV file
    data = read_data_from_csv(csv_filepath)

    insert_query = """INSERT INTO data_model_master (thing, property, ships_count) 
                      VALUES (%s, %s, %s);"""
    try:
        # Insert data into the database
        cursor.executemany(insert_query, data)
        conn.commit()
        print(f"{cursor.rowcount} rows were inserted.")
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()  # Roll back the transaction in case of error
        print(error)
    finally:
        cursor.close()
        conn.close()  # Ensure the database connection is closed

if __name__ == "__main__":
    csv_filepath = 'master_model.csv'  # Path to your CSV file
    # Load the connection info
    connection_info = read_db_connection_info()
    main(csv_filepath, connection_info)
