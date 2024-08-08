import pandas as pd

# Load the CSV files
data_mapping_file_path = 'select_db/data_mapping_mdm.csv'
data_model_master_file_path = 'master_model/data_model_master_export.csv'

data_mapping = pd.read_csv(data_mapping_file_path, dtype=str)
data_model_master = pd.read_csv(data_model_master_file_path, dtype=str)

# Initialize the reference_doc and match_count columns in data_model_master
data_model_master['reference_doc'] = ''
data_model_master['match_count'] = 0
data_mapping['thing_pattern'] = data_mapping['thing'].str.replace(r'\d', '#', regex=True) 
data_mapping['property_pattern'] = data_mapping['property'].str.replace(r'\d', '#', regex=True) 

# Iterate through data_model_master
for index, master_row in data_model_master.iterrows():
    # Filter data_mapping for matching thing and property patterns
    matching_rows = data_mapping[(data_mapping['thing_pattern'] == master_row['thing']) & 
                                 (data_mapping['property_pattern'] == master_row['property'])]
    
    # Concatenate the tag_description values
    reference_doc = " ".join(matching_rows['tag_description'].tolist())
    
    # Assign the count of matching rows to the match_count column in data_model_master
    data_model_master.at[index, 'match_count'] = len(matching_rows)

    # Assign the concatenated string to the reference_doc column in data_model_master
    data_model_master.at[index, 'reference_doc'] = reference_doc
    


# Save the updated data_model_master to a new CSV file
output_file_path = 'master_model/data_model_master_export_rdoc.csv'
data_model_master.to_csv(output_file_path, index=False, encoding='utf-8-sig')

print(f"Updated data_model_master saved to {output_file_path}")
