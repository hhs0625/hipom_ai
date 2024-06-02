# Tag Mapping with concatenated outputs

Workflow:

1. run `data_process_concat.ipynb` to produce the folder `combined_data` containing the save_to_disk version of the DatasetDict
2. run `t5_train_tp.ipynb` to make model located in `train_tp_checkpoint_1/checkpoint-xxxx`
3. run `produce_test_predictions.ipynb` to get inference result on `/make_test_csv/test_with_predictions.csv` data

GPU usage can be checed by `nvtop`