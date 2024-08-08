import pandas as pd

# Load the CSV file with low_memory=False
test_path = 'evaluation/train_t5-base_td_unit_80/checkpoint-4880/test_with_predictions.csv'
test_csv = pd.read_csv(test_path, low_memory=False)

# Replace NaN values with empty strings in relevant columns
test_csv['tag_description'].fillna('', inplace=True)

# Ensure p_MDM is boolean
test_csv['p_MDM'] = test_csv['p_MDM'].astype(bool)

# Filter rows where p_MDM is True
test_csv_filtered = test_csv[test_csv['p_MDM'] == True].copy()

# Group by ships_idx, p_thing, and p_property to count duplicates
duplicate_counts = test_csv_filtered.groupby(['ships_idx', 'p_thing', 'p_property']).size().reset_index(name='duplicate')

# Merge the duplicate counts back to the filtered dataframe
test_csv_filtered = test_csv_filtered.merge(duplicate_counts, on=['ships_idx', 'p_thing', 'p_property'], how='left')

# Initialize new columns in the filtered dataframe
test_csv_filtered['a_thing'] = ''
test_csv_filtered['a_property'] = ''

# Assign a_thing and a_property based on duplicate count
def assign_values(group):
    if group['duplicate'].iloc[0] == 1:
        group['a_thing'] = group['p_thing']
        group['a_property'] = group['p_property']
    else:
        best_row = group.loc[group['p_score'].idxmax()]
        group['a_thing'] = best_row['p_thing']
        group['a_property'] = best_row['p_property']
    return group

test_csv_filtered = test_csv_filtered.groupby(['ships_idx', 'p_thing', 'p_property']).apply(assign_values)

# Update the original dataframe with the filtered results
test_csv = test_csv.merge(test_csv_filtered[['ships_idx', 'p_thing', 'p_property', 'a_thing', 'a_property', 'duplicate']], 
                          on=['ships_idx', 'p_thing', 'p_property'], 
                          how='left', 
                          suffixes=('', '_filtered'))

# Drop unnecessary columns from the original dataframe
test_csv.drop(columns=['a_thing_filtered', 'a_property_filtered'], inplace=True)

# Count the number of rows where a_thing and a_property are assigned
assigned_count = test_csv['a_thing'].notna().sum()

# Count the number of rows where p_MDM is True
p_mdm_true_count = test_csv['p_MDM'].sum()

# Save the updated test_csv to a new CSV file
output_file_path = 'evaluation/updated_test_with_duplicates_and_assigned.csv'
test_csv.to_csv(output_file_path, index=False, encoding='utf-8-sig')

print(f"Updated test CSV saved to {output_file_path}")
print(f"Number of rows where p_MDM is True: {p_mdm_true_count}")
print(f"Number of rows where a_thing and a_property are assigned: {assigned_count}")
