import pandas as pd

# Read the CSV files
data_model_master_export = pd.read_csv('master_model/data_model_master_export.csv')
master_model = pd.read_csv('master_model/master_model.csv')

# Set ships_count to 0 in data_model_master_export
data_model_master_export['ships_count'] = 0

# List to hold new rows
new_rows = []

# Iterate over each row in master_model
for index, row in master_model.iterrows():
    thing = row['thing']
    property = row['property']
    ships_count = row['ships_count']
    
    # Check if there is a matching thing and property in data_model_master_export
    match = (data_model_master_export['thing'] == thing) & (data_model_master_export['property'] == property)
    
    if match.any():
        # If there is a match, update ships_count
        data_model_master_export.loc[match, 'ships_count'] = ships_count
    else:
        # If there is no match, add the new row to the list
        new_row = {
            'thing': thing,
            'property': property,
            'ships_count': ships_count
        }
        new_rows.append(new_row)

# Create a DataFrame from the list of new rows
if new_rows:
    new_rows_df = pd.DataFrame(new_rows)
    # Concatenate the original DataFrame with the new rows DataFrame
    data_model_master_export = pd.concat([data_model_master_export, new_rows_df], ignore_index=True)

# Save the updated data to a new CSV file
data_model_master_export.to_csv('master_model/data_model_master_export_updated.csv', index=False)

print("Task completed. The updated file has been saved as 'master_model/data_model_master_export_updated.csv'.")
