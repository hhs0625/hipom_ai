import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

# Load the CSV files
test_path = 'evaluation/train_t5-base_td_unit_80/checkpoint-4880/test_with_predictions.csv'
ship_data_list_reference_doc_file_path = 'master_model/data_list_rdoc.csv'

test_csv = pd.read_csv(test_path, low_memory=False)
sdl_rdoc = pd.read_csv(ship_data_list_reference_doc_file_path)

# Replace NaN values with empty strings in relevant columns
test_csv['tag_description'].fillna('', inplace=True)
sdl_rdoc['reference_doc'].fillna('', inplace=True)

# Initialize new columns in test_csv
test_csv['p_score'] = 0.0
test_csv['b_thing'] = ''
test_csv['b_property'] = ''
test_csv['b_score'] = 0.0

# Filter rows where p_MDM is True and p_mapping_count is 1 or more
test_csv_filtered = test_csv[(test_csv['p_MDM'] == True) & (test_csv['p_mapping_count'] >= 1)].copy()

# Reset index of the filtered dataframe
test_csv_filtered.reset_index(drop=True, inplace=True)

# Create a TF-IDF Vectorizer with custom token pattern
vectorizer = TfidfVectorizer(token_pattern=r'\S+')

# Combine all tag_descriptions and reference_docs
all_documents = test_csv_filtered['tag_description'].tolist() + sdl_rdoc['reference_doc'].tolist()

# Fit and transform the TF-IDF vectorizer on all documents
tfidf_matrix = vectorizer.fit_transform(all_documents)

# Split the TF-IDF matrix into test and reference parts
test_tfidf_matrix = tfidf_matrix[:len(test_csv_filtered)]
reference_tfidf_matrix = tfidf_matrix[len(test_csv_filtered):]

# Create a mapping from thing/property to reference_doc
thing_property_to_reference_doc = sdl_rdoc.set_index(['thing', 'property'])['reference_doc'].to_dict()

# Iterate through test_csv_filtered with tqdm for progress bar
for index, test_row in tqdm(test_csv_filtered.iterrows(), total=test_csv_filtered.shape[0], desc="Processing"):
    # Get the p_thing and p_property from the current test row
    p_thing = test_row['p_thing']
    p_property = test_row['p_property']
    tag_description = test_row['tag_description']

    # Get the index of the current test_row in test_tfidf_matrix
    test_tfidf_vector = test_tfidf_matrix[index:index+1]
    
    # Get the index of the corresponding reference_doc in reference_tfidf_matrix
    ref_index = sdl_rdoc[(sdl_rdoc['thing'] == p_thing) & (sdl_rdoc['property'] == p_property)].index[0]
    ref_tfidf_vector = reference_tfidf_matrix[ref_index:ref_index+1]
    
    # Calculate cosine similarity for p_score
    similarity_score = cosine_similarity(test_tfidf_vector, ref_tfidf_vector).flatten()[0]
    test_csv.at[test_row.name, 'p_score'] = similarity_score
    
    # Calculate cosine similarity with all reference_docs for b_score
    all_similarity_scores = cosine_similarity(test_tfidf_vector, reference_tfidf_matrix).flatten()
    best_match_index = all_similarity_scores.argmax()
    best_match_score = all_similarity_scores[best_match_index]
    
    # Get the corresponding thing and property from the best match
    best_match_row = sdl_rdoc.iloc[best_match_index]
    test_csv.at[test_row.name, 'b_thing'] = best_match_row['thing']
    test_csv.at[test_row.name, 'b_property'] = best_match_row['property']
    test_csv.at[test_row.name, 'b_score'] = best_match_score

# Save the updated test_csv to a new CSV file
output_file_path = 'evaluation/updated_test_with_pscore.csv'
test_csv.to_csv(output_file_path, index=False, encoding='utf-8-sig')

print(f"Updated test CSV saved to {output_file_path}")
