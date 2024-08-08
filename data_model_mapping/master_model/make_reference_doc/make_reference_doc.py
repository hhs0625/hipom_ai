import pandas as pd

# Load the CSV files
data_mapping_file_path = 'select_db/data_mapping_filtered.csv'
data_mapping = pd.read_csv(data_mapping_file_path, dtype=str)

data_model_master_file_path = 'master_model/data_model_master_export.csv'
data_model_master = pd.read_csv(data_model_master_file_path, dtype=str)

# Add a new column 'reference_doc' to data_model_master and initialize with empty strings
data_model_master['reference_doc'] = ""

# Iterate through each row in data_model_master
for i, master_row in data_model_master.iterrows():
    master_thing = master_row['thing']
    master_property = master_row['property']
    
    # Find matching rows in data_mapping
    matching_rows = data_mapping[
        (data_mapping['thing_pattern'] == master_thing) &
        (data_mapping['property_pattern'] == master_property)
    ]
    
    # If there are matching rows, concatenate their tag_descriptions and set reference_doc
    if not matching_rows.empty:
        tag_descriptions = matching_rows['tag_description'].tolist()
        data_model_master.at[i, 'reference_doc'] = ' '.join(tag_descriptions)

# Save the updated data_model_master to a new CSV file
output_file_path = 'master_model/data_model_master_export_rdoc.csv'
data_model_master.to_csv(output_file_path, index=False)

print(f"Updated data_model_master saved to {output_file_path}")
