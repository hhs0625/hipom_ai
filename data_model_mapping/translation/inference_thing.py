from datasets import load_dataset
from transformers.pipelines.pt_utils import KeyDataset
from transformers import pipeline
from tqdm import tqdm

# translations_thing.json obtained from data_process.ipynb
raw_dataset = load_dataset("json", data_files="/path/translations_thing.json")
# load checkpoint from the "tag_description_to_thing/checkpoint-x" folder
model_checkpoint = "tag_description_to_thing/checkpoint-2600"
# perform split with same seed to get same data split as training
split_datasets = raw_dataset["train"].train_test_split(train_size=0.9, seed=20)
pipe = pipeline("translation_XX_to_YY", model=model_checkpoint, max_length=256, device=0)


# perform inference for train
output_list = []
print("making inference on train set")
for out in tqdm(pipe(KeyDataset(split_datasets["train"]["translation"], "tag_description"))):
    output_list.append(out[0]['translation_text'])
print("inference done")

answer_list = [ item['thing'] for item in split_datasets["train"]["translation"]]
assert(len(output_list) == len(answer_list))
count_num_equal = 0
for i in range(len(output_list)):
    if (output_list[i] == answer_list[i]):
        count_num_equal = count_num_equal + 1
print("train acc", count_num_equal/len(output_list))


# perform inference for test
output_list = []
print("making inference on test set")
for out in tqdm(pipe(KeyDataset(split_datasets["test"]["translation"], "tag_description"))):
    output_list.append(out[0]['translation_text'])
print("inference done")

answer_list = [ item['thing'] for item in split_datasets["test"]["translation"]]
assert(len(output_list) == len(answer_list))
count_num_equal = 0
for i in range(len(output_list)):
    if (output_list[i] == answer_list[i]):
        count_num_equal = count_num_equal + 1
print("test acc", count_num_equal/len(output_list))