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

# Load the test_with_predictions_MPM CSV file
test_with_predictions_file_path = 'evaluation/test_with_predictions_MPM.csv'  # Adjust this path to your actual file location
data_mapping = pd.read_csv(test_with_predictions_file_path, dtype=str)

# Filter rows where p_MDM is TRUE
data_mapping = data_mapping[data_mapping['p_MDM'] == 'TRUE']

# Add 'p_thing_property' field
data_mapping['p_thing_property'] = data_mapping['p_thing'] + data_mapping['p_property']

# Add 'p_num_1' and 'p_num_2' fields
data_mapping['p_num_1'] = data_mapping['p_thing_property'].apply(lambda x: (extract_numbers(x) + [None, None])[0])
data_mapping['p_num_2'] = data_mapping['p_thing_property'].apply(lambda x: (extract_numbers(x) + [None, None])[1])

# Add 'p_thing_pattern' and 'p_property_pattern' fields
data_mapping['p_thing_pattern'] = data_mapping['p_thing'].apply(replace_and_compress_numbers)
data_mapping['p_property_pattern'] = data_mapping['p_property'].apply(replace_and_compress_numbers)

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
    left_on=['p_thing_pattern', 'p_property_pattern'],
    right_on=['thing', 'property'],
    how='left',
    suffixes=('', '_master')
)

# Rename the matched data_desc to p_data_desc
merged_data.rename(columns={'data_desc': 'p_data_desc'}, inplace=True)

# Add 'p_data_desc_num' field with placeholders replaced by num_1 and num_2
merged_data['p_data_desc_num'] = merged_data.apply(
    lambda row: replace_placeholders(row['p_data_desc'], row['p_num_1'], row['p_num_2']),
    axis=1
)

# Save the updated DataFrame to a new CSV file
output_file_path = 'evaluation/test_with_predictions_MPM_desc.csv'
merged_data.to_csv(output_file_path, index=False)

print(f"Updated data saved to {output_file_path}")
