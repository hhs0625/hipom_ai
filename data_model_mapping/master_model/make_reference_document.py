import pandas as pd
import re

# Function to clean special characters thoroughly
def thorough_clean_text(text):
    # Replace commas, newline characters, and multiple spaces with a single space
    text = re.sub(r'[,\r\n]+', ' ', text)
    # Remove double quotes and any other problematic characters
    text = re.sub(r'["]', '', text)
    # Trim leading and trailing spaces
    text = text.strip()
    return text

# Read the master model CSV file
master_file_path = 'master_model/data_model_master_export.csv'
master_df = pd.read_csv(master_file_path)

# Add the 'pattern' field
master_df['pattern'] = master_df['thing'] + " " + master_df['property']

# Read the test CSV file
test_file_path = 'make_test_csv/test.csv'
test_df = pd.read_csv(test_file_path)

# Initialize the 'r_doc' field in the master DataFrame
master_df['r_doc'] = ""

# Iterate over the master DataFrame and update the 'r_doc' field
for i, master_row in master_df.iterrows():
    # Find matching rows in the test DataFrame
    matching_rows = test_df[test_df['pattern'] == master_row['pattern']]
    # Concatenate the 'tag_description' values
    concatenated_description = ' '.join(matching_rows['tag_description'].astype(str).tolist())
    # Thoroughly clean the concatenated description
    cleaned_description = thorough_clean_text(concatenated_description)
    # Update the 'r_doc' field in the master DataFrame
    master_df.at[i, 'r_doc'] = cleaned_description

# Save the updated master DataFrame to a new CSV file
output_master_file_path = 'master_model/data_model_master_export_d_doc_cleaned.csv'
master_df.to_csv(output_master_file_path, index=False)

print(f"Thoroughly cleaned master model saved to {output_master_file_path}")
