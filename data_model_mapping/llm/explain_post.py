import pandas as pd
import os
import re

# Read the master_desc.csv file
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_desc.csv')
df = pd.read_csv(csv_path)

# Replace numbers in the desc, thing, and property fields with #
df['desc'] = df['desc'].apply(lambda x: re.sub(r'\d', '#', str(x)))
df['thing'] = df['thing'].apply(lambda x: re.sub(r'\d', '#', str(x)))
df['property'] = df['property'].apply(lambda x: re.sub(r'\d', '#', str(x)))

# Add desc_numbers column counting '#' in the desc field
df['desc_numbers'] = df['desc'].apply(lambda x: x.count('#'))

# Define the new file path with '_post' appended to the original filename
new_csv_path = os.path.join(os.path.dirname(csv_path), 'master_desc_post.csv')

# Save the updated DataFrame to the new CSV file
df.to_csv(new_csv_path, index=False)

print(f"Updated DataFrame has been saved to {new_csv_path}")
