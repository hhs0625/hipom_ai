import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm  # Import the tqdm library

# Load the CSV files

test_path = 'evaluation/train_t5-base_td_unit_80/checkpoint-4880/test_with_predictions.csv'
data_model_master_file_path = 'master_model/data_list_rdoc.csv'  # Updated file path

test_csv = pd.read_csv(test_path, low_memory=False)
data_model_master = pd.read_csv(data_model_master_file_path)

# Replace NaN values with empty strings in relevant columns
test_csv['tag_description'].fillna('', inplace=True)
data_model_master['reference_doc'].fillna('', inplace=True)

# Initialize new columns in test_csv
test_csv['c_thing_sdl'] = ''
test_csv['c_property_sdl'] = ''
test_csv['c_score_sdl'] = ''

# Create a TF-IDF Vectorizer with custom token pattern
vectorizer = TfidfVectorizer(token_pattern=r'\S+')

# Combine all tag_descriptions and reference_docs
all_documents = test_csv['tag_description'].tolist() + data_model_master['reference_doc'].tolist()

# Fit and transform the TF-IDF vectorizer on all documents
tfidf_matrix = vectorizer.fit_transform(all_documents)

# Split the TF-IDF matrix into test and reference parts
test_tfidf_matrix = tfidf_matrix[:len(test_csv)]
reference_tfidf_matrix = tfidf_matrix[len(test_csv):]

# Iterate through test_csv with tqdm for progress bar
for index, test_row in tqdm(test_csv.iterrows(), total=test_csv.shape[0], desc="Processing"):
    # Calculate cosine similarity between the test description and all reference_docs
    similarity_scores = cosine_similarity(test_tfidf_matrix[index:index+1], reference_tfidf_matrix).flatten()
    
    # Find the index of the highest similarity score
    best_match_index = similarity_scores.argmax()
    best_match_score = similarity_scores[best_match_index]
    
    # Get the corresponding thing and property from data_model_master
    best_match_row = data_model_master.iloc[best_match_index]
    test_csv.at[index, 'sdl_c_thing'] = best_match_row['thing']
    test_csv.at[index, 'sdl_c_property'] = best_match_row['property']
    test_csv.at[index, 'sdl_c_score'] = best_match_score

# Add new fields for correctness checks
test_csv['sdl_thing_correct'] = test_csv['thing'] == test_csv['sdl_c_thing']
test_csv['sdl_property_correct'] = test_csv['property'] == test_csv['sdl_c_property']
test_csv['sdl_tp_correct'] = test_csv['sdl_thing_correct'] & test_csv['sdl_property_correct']


mdm_true = test_csv[test_csv['MDM']] 
correct_mdm_true = mdm_true[mdm_true['sdl_tp_correct']]

# Calculate percentage
percentage_correct = (len(correct_mdm_true) / len(mdm_true)) * 100 if len(mdm_true) > 0 else 0

print(f"SDL accuracy: {percentage_correct:.2f}%")

# Save the updated test_csv to a new CSV file
output_file_path = test_path
test_csv.to_csv(output_file_path, index=False, encoding='utf-8-sig')
print(f"Updated test CSV saved to {output_file_path}")

