# %% d
from datasets import load_from_disk
from transformers.pipelines.pt_utils import KeyDataset
from transformers import pipeline
from tqdm import tqdm

# import data and load dataset
# Path to saved combined_dataset
file_path = 'combined_data'
split_datasets = load_from_disk(file_path)


model_checkpoint = "train_tp_checkpoint_40/checkpoint-2320"

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("t5-base", return_tensors="pt")
# Define additional special tokens
additional_special_tokens = ["<THING_START>", "<THING_END>", "<PROPERTY_START>", "<PROPERTY_END>"]
# Add the additional special tokens to the tokenizer
tokenizer.add_special_tokens({"additional_special_tokens": additional_special_tokens})
# tokenizer.add_special_tokens({'sep_token': "<SEP>"})


pipe = pipeline("translation_XX_to_YY", model=model_checkpoint, tokenizer=tokenizer, max_length=64, device=0)


# %%
# perform inference for test
output_list = []
print("making inference on test set")
for out in tqdm(pipe(KeyDataset(split_datasets["test"]["translation"], "tag_description"), batch_size=256)):
    output_list.append(out[0]['translation_text'])
print("inference done")

answer_list = [ item['answer'] for item in split_datasets["test"]["translation"]]
assert(len(output_list) == len(answer_list))
count_num_equal = 0
for i in range(len(output_list)):
    if (output_list[i] == answer_list[i]):
        count_num_equal = count_num_equal + 1
print("test acc", count_num_equal/len(output_list))


# perform inference for train
output_list = []
print("making inference on train set")
for out in tqdm(pipe(KeyDataset(split_datasets["train"]["translation"], "tag_description"), batch_size=256)):
    output_list.append(out[0]['translation_text'])
print("inference done")

answer_list = [ item['answer'] for item in split_datasets["train"]["translation"]]
assert(len(output_list) == len(answer_list))
count_num_equal = 0
for i in range(len(output_list)):
    if (output_list[i] == answer_list[i]):
        count_num_equal = count_num_equal + 1
print("train acc", count_num_equal/len(output_list))