import pandas as pd
import os

# Read the master_desc.csv file
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_desc.csv')
df = pd.read_csv(csv_path)

# Function to clean trailing spaces from 'tag_description'
def clean_trailing_spaces(tag_description):
    while tag_description.endswith(' '):
        tag_description = tag_description[:-1]
    return tag_description

# Clean trailing spaces from 'tag_description' column
df['tag_description'] = df['tag_description'].apply(clean_trailing_spaces)

# Function to clean the 'desc' field
def clean_desc(row):
    desc = row['desc']
    tag_description = row['tag_description']
    
    # Remove specified phrases
    phrases_to_remove = [
        "The tag_description ",
        "The tag description ",
        "refers to ",
        "is ",
        f"'{tag_description}' "
    ]
    
    for phrase in phrases_to_remove:
        desc = desc.replace(phrase, "")
    
    return desc.strip()

# Apply the clean_desc function to the 'desc' column
df['desc'] = df.apply(clean_desc, axis=1)

# Define the new path to save the CSV file with '_post' appended to the original name
new_csv_path = os.path.splitext(csv_path)[0] + '_post.csv'

# Save the updated DataFrame to the new CSV file
df.to_csv(new_csv_path, index=False)

print(f"Updated DataFrame has been saved to {new_csv_path}")
