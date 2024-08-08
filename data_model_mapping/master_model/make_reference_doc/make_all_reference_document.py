import pandas as pd

# Load the CSV file
data_mapping_file_path = 'select_db/data_mapping_mdm.csv'
data_mapping = pd.read_csv(data_mapping_file_path, dtype=str)

# Group by 'thing' and 'property' and concatenate 'tag_description'
grouped = data_mapping.groupby(['thing', 'property'])['tag_description'].apply(lambda x: ' '.join(x)).reset_index()

# Calculate group counts
group_counts = data_mapping.groupby(['thing', 'property']).size().reset_index(name='group_count')

# Merge group counts into the grouped DataFrame
grouped = pd.merge(grouped, group_counts, on=['thing', 'property'])

# Rename the concatenated column to 'reference_doc'
grouped.rename(columns={'tag_description': 'reference_doc'}, inplace=True)

# Reorder columns to have 'group_count' after 'property'
grouped = grouped[['thing', 'property', 'group_count', 'reference_doc']]

# Save the updated data to a new CSV file
output_file_path = 'master_model/data_list_rdoc.csv'
grouped.to_csv(output_file_path, index=False, encoding='utf-8-sig')

print(f"Updated data saved to {output_file_path}")
