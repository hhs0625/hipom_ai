import pandas as pd
import re

# Function to replace numbers with '#' and compress multiple '#' into one
def replace_and_compress_numbers(s):
    s = re.sub(r'\d+', '#', s)  # Replace numbers with '#'
    s = re.sub(r'#+', '#', s)   # Compress multiple '#' into one
    return s

# Function to extract numbers
def extract_numbers(s):
    return re.findall(r'\d+', s)

# Function to replace placeholders in data_desc with num_1 and num_2
def replace_placeholders(data_desc, num_1, num_2):
    if pd.isna(data_desc):
        return data_desc
    placeholders = re.findall(r'#', data_desc)
    if len(placeholders) > 0:
        data_desc = data_desc.replace('#', num_1 if num_1 else '#', 1)
    if len(placeholders) > 1:
        data_desc = data_desc.replace('#', num_2 if num_2 else '#', 1)
    return data_desc

# Load the data_mapping CSV file
data_mapping_file_path = 'select_db/data_mapping.csv'  # Adjust this path to your actual file location
data_mapping = pd.read_csv(data_mapping_file_path, dtype=str)


# Add 'thing_property' field
data_mapping['thing_property'] = data_mapping['thing'] + data_mapping['property']

# Add 'num_1' and 'num_2' fields
data_mapping['num_1'] = data_mapping['thing_property'].apply(lambda x: (extract_numbers(x) + [None, None])[0])
data_mapping['num_2'] = data_mapping['thing_property'].apply(lambda x: (extract_numbers(x) + [None, None])[1])

# Add 'thing_pattern' and 'property_pattern' fields
data_mapping['thing_pattern'] = data_mapping['thing'].apply(replace_and_compress_numbers)
data_mapping['property_pattern'] = data_mapping['property'].apply(replace_and_compress_numbers)

# Load the data_model_master_export CSV file
data_model_master_file_path = 'master_model/data_model_master_export.csv'  # Adjust this path to your actual file location
data_model_master = pd.read_csv(data_model_master_file_path, dtype=str)

# Ensure columns in data_model_master are formatted correctly
data_model_master['thing'] = data_model_master['thing'].apply(replace_and_compress_numbers)
data_model_master['property'] = data_model_master['property'].apply(replace_and_compress_numbers)

# Merge data_mapping with data_model_master on the pattern fields
merged_data = pd.merge(
    data_mapping,
    data_model_master[['thing', 'property', 'data_desc']],
    left_on=['thing_pattern', 'property_pattern'],
    right_on=['thing', 'property'],
    how='left',
    suffixes=('', '_master')
)

# Add 'MDM' field
merged_data['MDM'] = merged_data['data_desc'].notnull()

# Filter out rows where MDM is False
merged_data = merged_data[merged_data['MDM']]

# Add 'data_desc_num' field
merged_data['data_desc_num'] = merged_data.apply(
    lambda row: replace_placeholders(row['data_desc'], row['num_1'], row['num_2']),
    axis=1
)

# Save the updated DataFrame to a new CSV file
output_file_path = 'select_db/data_mapping_filtered.csv'
merged_data.to_csv(output_file_path, index=False)

print(f"Updated data saved to {output_file_path}")
