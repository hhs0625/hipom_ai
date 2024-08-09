# Mapping Ship Data List to Platform Data List

## Prerequisites
1. Run Python programs from the `hipom_ai/data_model_mapping` directory.
2. Place the `db_connection_info.txt` file containing database connection information in the `hipom_ai/` directory.

## Preparing the Data
1. Navigate to the `select_db` directory to execute the program.
2. Run `select_db.py` to extract data from the `data_mapping` table in the database and generate a CSV file.
3. Execute `normalization.ipynb` to normalize the `tag_description`.
4. Run `make_csv.py` to create the `data_mapping_mdm.csv` file for training and the `test.csv` file for testing.

## Training the T5 Model
Run the following steps in the `translation` directory:

### Creating Training Data in Binary Format
1. In `data_process_concat.ipynb`, choose the mode (mode is saved as JSON for later use).
2. Run the script to convert the `data_mapping_mdm.csv` file into a binary format for training (the output will be saved as `combined_data`).

### Training the Model
1. Set the number of epochs and model name in `t5_train_tp.ipynb`.
2. Run the script to train the model; the trained model will be saved as `train_{model_name}_{mode}_{train_epochs}`.

### Testing the Model
1. Run `produce_test_predictions.ipynb`.
2. The test results will be saved in `../evaluation/{model_checkpoint}/test_with_predictions.csv`.
3. During execution, you can check the accuracy by verifying whether duplicates contain the correct answer.

### Checking Accuracy by Ship
1. In the `evaluation` folder, configure the file path for `test_with_predictions.csv` in the `check_t5.ipynb` script.
2. Run the script to view the accuracy for each ship.
3. The script also allows you to check the number of cases where the actual MDM was `true` but predicted as `false` and vice versa.

## Removing Duplicates in T5 Results Using TF-IDF to Improve Accuracy
1. In the `similarity` folder, configure the file path for `test_with_predictions.csv` in the `pick_one_from_t5` script and run it.
2. Check the accuracy results.
3. Review the CSV file generated in the same folder as `test_with_predictions.csv`.
