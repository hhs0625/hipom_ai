import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
import os

# Load the CSV files
test_path = 'evaluation/train_t5-base_td_unit_80/checkpoint-4880/test_with_predictions.csv'
ship_data_list_reference_doc_file_path = 'master_model/data_list_rdoc.csv'

test_csv = pd.read_csv(test_path, low_memory=False)
sdl_rdoc = pd.read_csv(ship_data_list_reference_doc_file_path)

# Replace NaN values with empty strings in relevant columns
test_csv['tag_description'].fillna('', inplace=True)
sdl_rdoc['reference_doc'].fillna('', inplace=True)

# Initialize new columns in test_csv
test_csv['a_score'] = 0.0
test_csv['a_thing'] = ''
test_csv['a_property'] = ''
test_csv['a_correct'] = False

# Filter rows where duplicate is 2 or more
duplicate_filtered = test_csv[test_csv['duplicate'] >= 2].copy()

# Create a TF-IDF Vectorizer with custom token pattern
vectorizer = TfidfVectorizer(token_pattern=r'\S+')

# Fit and transform the TF-IDF vectorizer on all reference_docs
reference_tfidf_matrix = vectorizer.fit_transform(sdl_rdoc['reference_doc'])

# Create a mapping from thing/property to reference_doc
thing_property_to_reference_doc = sdl_rdoc.set_index(['thing', 'property'])['reference_doc'].to_dict()

# Calculate a_score for duplicate rows
for ships_idx, group in tqdm(duplicate_filtered.groupby('ships_idx'), desc="Processing duplicates"):
    for (p_thing, p_property), sub_group in group.groupby(['p_thing', 'p_property']):
        sub_group = sub_group.copy()
        tag_descriptions = sub_group['tag_description'].tolist()
        test_tfidf_matrix = vectorizer.transform(tag_descriptions)
        reference_doc = thing_property_to_reference_doc.get((p_thing, p_property), '')
        if reference_doc:
            reference_vector = vectorizer.transform([reference_doc])
            sub_group['a_score'] = cosine_similarity(test_tfidf_matrix, reference_vector).flatten()
        else:
            sub_group['a_score'] = 0
        test_csv.loc[sub_group.index, 'a_score'] = sub_group['a_score']

# For rows where duplicate is 1 or less, a_score is already initialized to 0

# Fill a_thing and a_property for all rows
for index, row in tqdm(test_csv.iterrows(), total=test_csv.shape[0], desc="Assigning a_thing and a_property"):
    if row['duplicate'] == 1:
        test_csv.at[index, 'a_thing'] = row['p_thing']
        test_csv.at[index, 'a_property'] = row['p_property']
    elif row['duplicate'] >= 2:
        ships_idx_group = test_csv[(test_csv['ships_idx'] == row['ships_idx']) & (test_csv['p_thing'] == row['p_thing']) & (test_csv['p_property'] == row['p_property'])]
        if not ships_idx_group.empty:
            best_row = ships_idx_group.loc[ships_idx_group['a_score'].idxmax()]
            if best_row.name == index:
                test_csv.at[index, 'a_thing'] = best_row['p_thing']
                test_csv.at[index, 'a_property'] = best_row['p_property']

# Calculate a_correct
test_csv['a_correct'] = ((test_csv['thing'] == test_csv['a_thing']) & 
                         (test_csv['property'] == test_csv['a_property']) & 
                         (test_csv['duplicate'] >= 1) &
                         (test_csv['MDM']))

# Calculate the percentage of correct a_thing and a_property
mdm_true_count = test_csv['MDM'].sum()
a_correct_count = test_csv['a_correct'].sum()
a_correct_percentage = (a_correct_count / mdm_true_count) * 100

print(f"a_correct count: {a_correct_count}")
print(f"MDM true count: {mdm_true_count}")
print(f"a_correct percentage: {a_correct_percentage:.2f}%")

# Save the updated DataFrame to a new CSV file
output_path = 'evaluation/train_t5-base_td_unit_80/checkpoint-4880/updated_test_with_ascore.csv'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
test_csv.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Updated data saved to {output_path}")

# Check for duplicates in a_thing and a_property within each ships_idx
print("\nShips_idx with duplicate a_thing and a_property:")
duplicate_ships_idx = []

for ships_idx, group in test_csv.groupby('ships_idx'):
    # Exclude rows with empty a_thing or a_property
    non_empty_group = group[(group['a_thing'] != '') & (group['a_property'] != '')]
    duplicate_entries = non_empty_group[non_empty_group.duplicated(subset=['a_thing', 'a_property'], keep=False)]
    if not duplicate_entries.empty:
        duplicate_ships_idx.append(ships_idx)
        print(f"Ships_idx: {ships_idx}")
        print(duplicate_entries[['a_thing', 'a_property']])

if not duplicate_ships_idx:
    print("No duplicates found.")
