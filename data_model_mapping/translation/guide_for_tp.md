# Tag Mapping with concatenated outputs

Workflow:

1. run `data_process_concat.ipynb` to produce the folder `combined_data` containing the save_to_disk version of the DatasetDict
2. run `t5_train_tp.py` via `deepspeed --num_gpus 4 t5_train_tp.py`
3. run `t5_train_tp.py` to get inference result on "test" data

Training from the notebook limits the use of GPUs to 1. 

It is possible to raise the number of GPUs to 4, but it is easier to call the function from deepspeed and pass a num_gpu argument to use all 4 GPUs.