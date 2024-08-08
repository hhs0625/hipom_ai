import pandas as pd
import re

# Load the data from 'data_mapping.csv' and 'data_model_master_export.csv'
df_test = pd.read_csv('select_db/data_mapping.csv')
df_master = pd.read_csv('master_model/data_model_master_export.csv')

# Create a new column 'master_pattern' in df_master
df_master['master_pattern'] = df_master['thing'] + " " + df_master['property']

# Create a pattern column in df_test that matches the format of 'master_pattern'
df_test['pattern'] = df_test['thing'].str.replace(r'\d', '#', regex=True) + " " + df_test['property'].str.replace(r'\d', '#', regex=True)

# Set of master patterns from df_master
master_patterns = set(df_master['master_pattern'])

# Check each pattern in df_test if it exists in df_master and assign the "MDM" field
df_test['MDM'] = df_test['pattern'].apply(lambda x: "TRUE" if x in master_patterns else "FALSE")

# Remove rows where tag_description is NULL
df_test = df_test.dropna(subset=['tag_description'])

# Function to extract alphabetic characters from a string
def extract_alpha_characters(text):
    return ''.join(re.findall(r'[A-Za-z]', text))

# Update f_thing and f_property based on MDM value
df_test['f_thing'] = df_test.apply(lambda row: '$UNMAPPED' if row['MDM'] == 'FALSE' else row['thing'], axis=1)
df_test['f_property'] = df_test.apply(lambda row: extract_alpha_characters(row['tag_description']) if row['MDM'] == 'FALSE' else row['property'], axis=1)


df_test = df_test.dropna(subset=['f_property'])


# Update thing and property based on MDM value
df_test['thing'] = df_test.apply(lambda row: row['f_thing'] if row['MDM'] == 'FALSE' else row['thing'], axis=1)
df_test['property'] = df_test.apply(lambda row: row['f_property'] if row['MDM'] == 'FALSE' else row['property'], axis=1)


# Print the dataframe with the updated thing and property columns
print(df_test)

# Optionally, save the updated dataframe to a new CSV file
df_test.to_csv('select_db/data_mapping_fake_tp.csv', index=False)
