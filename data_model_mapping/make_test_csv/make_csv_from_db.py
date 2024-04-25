import psycopg2
import pandas as pd

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
            # SQL to select matched records
            query_data_mapping = """
            SELECT dm.*
            FROM data_mapping dm
            WHERE dm.ships_idx BETWEEN 1000 AND 1999;
            """
            cursor.execute(query_data_mapping)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(results, columns=column_names)

             # Set 'thing' and 'property' to "" if 'thing' value is $UNMAPPED
            df.loc[df['thing'] == '$UNMAPPED', ['thing', 'property']] = ''

            # Query to get patterns from data_model_master
            query_patterns = """
            SELECT thing, property
            FROM data_model_master;
            """
            cursor.execute(query_patterns)
            patterns = cursor.fetchall()
            patterns_df = pd.DataFrame(patterns, columns=['thing', 'property'])
            patterns_df['pattern'] = patterns_df['thing'] + "@" + patterns_df['property']
            # Add additional fields with default values
            additional_fields = {
                'p_thing': '', 'p_property': '', 'p_thing_correct': '',
                'p_property_correct': '', 'MDM': 'FALSE'
            }
            for field in additional_fields:
                df[field] = additional_fields[field]

            df['pattern'] = df['thing'].str.replace('\d+', '#', regex=True) + "@" + df['property'].str.replace('\d+', '#', regex=True)
            df['MDM'] = df['pattern'].isin(patterns_df['pattern']).replace({True: 'TRUE', False: 'FALSE'})

            df.to_excel('make_test_csv/test.xlsx', index=False)
            print("Data exported successfully to 'test.xlsx'")

except (Exception, psycopg2.DatabaseError) as error:
    print(f"An error occurred: {error}")
finally:
    if conn is not None:
        conn.close()
