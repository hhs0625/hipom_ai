import pandas as pd

# Load the CSV files
data_mapping_file_path = 'select_db/data_mapping_filtered.csv'
data_model_master_file_path = 'master_model/data_model_master_export.csv'

data_mapping = pd.read_csv(data_mapping_file_path, dtype=str)
data_model_master = pd.read_csv(data_model_master_file_path, dtype=str)

# Initialize the reference_doc column in data_model_master
data_model_master['reference_doc'] = ''
# Concatenate tag_description and unit into a new column 'td_unit', handling NaN values
data_mapping['td_unit'] = data_mapping['tag_description'].fillna('') + " " + data_mapping['unit'].fillna('')

# Iterate through data_model_master
for index, master_row in data_model_master.iterrows():
    # Filter data_mapping for matching thing and property patterns
    matching_rows = data_mapping[(data_mapping['thing_pattern'] == master_row['thing']) & 
                                 (data_mapping['property_pattern'] == master_row['property'])]
    
    # Concatenate the tag_description values
    reference_doc = " ".join(matching_rows['td_unit'].astype(str).tolist())
    
    # Assign the concatenated string to the reference_doc column in data_model_master
    data_model_master.at[index, 'reference_doc'] = reference_doc

# Save the updated data_model_master to a new CSV file
output_file_path = 'master_model/data_model_master_export_rdoc_unit.csv'
data_model_master.to_csv(output_file_path, index=False)

print(f"Updated data_model_master saved to {output_file_path}")
