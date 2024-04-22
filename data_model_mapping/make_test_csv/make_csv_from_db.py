import psycopg2
import csv

def read_db_connection_info(filename):
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

# Load the connection info from the correct path
filename = "../db_connection_info.txt"  # Adjust the path as necessary
connection_info = read_db_connection_info(filename)

try:
    # Connect to the database
    conn = psycopg2.connect(
        host=connection_info["host"],
        user=connection_info["user"],
        password=connection_info["password"],
        dbname=connection_info["database"],
        port=connection_info["port"]
    )
    with conn:
        with conn.cursor() as cursor:
            # SQL to select matched records, excluding where tag_description is NULL or 'NULL'
            query = """
            SELECT dm.*
            FROM data_mapping dm
            WHERE dm.ships_idx BETWEEN 1000 AND 1999;
            """
            cursor.execute(query)
            results = cursor.fetchall()

            # Define additional fields with default values or computation logic here
            additional_fields = ['p_thing', 'p_property', 'score', 'correct', 'overlap']
            default_values = ['', '', '', '', '']  # Example default values

            # Save results to CSV
            with open('make_test_csv/test.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                # Write headers based on the cursor description, extended with additional fields
                headers = [desc[0] for desc in cursor.description] + additional_fields
                writer.writerow(headers)
                # Write data, extending each row with the additional fields
                for row in results:
                    extended_row = list(row) + default_values
                    writer.writerow(extended_row)
            print("Data exported successfully to 'test.csv'")

except (Exception, psycopg2.DatabaseError) as error:
    print(f"An error occurred: {error}")
finally:
    if conn is not None:
        conn.close()
