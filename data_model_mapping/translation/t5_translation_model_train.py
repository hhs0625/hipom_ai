from datasets import load_dataset
from transformers import AutoTokenizer

# import data and load dataset
# translations_thing.json is produced from 'data_process.ipynb'
raw_dataset = load_dataset("json", data_files="/to_path/translations_thing.json")
split_datasets = raw_dataset["train"].train_test_split(train_size=0.9, seed=20)
split_datasets["validation"] = split_datasets.pop("test")

# prepare tokenizer
tokenizer = AutoTokenizer.from_pretrained("t5-base", return_tensors="pt")
added_toks = {}
added_toks['sep_token'] = "<SEP>"
tokenizer.add_special_tokens(added_toks)
max_length = 256

# preprocess function tokenizes the input and target fields
def preprocess_function(examples):
    inputs = [ex["tag_description"] for ex in examples['translation']]
    targets = [ex["thing"] for ex in examples['translation']]
    model_inputs = tokenizer(
        inputs, text_target=targets, max_length=max_length, truncation=True
    )
    return model_inputs

# this produces tokenized_datasets for all subdata of split_datasets (train and validation)
tokenized_datasets = split_datasets.map(
    preprocess_function,
    batched=True,
    remove_columns=split_datasets["train"].column_names,
)

# we use the pre-trained t5-base model
from transformers import AutoModelForSeq2SeqLM
model_checkpoint = "t5-base"
model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)

# data collator
from transformers import DataCollatorForSeq2Seq
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# evaluation 
import evaluate
metric = evaluate.load("sacrebleu")
import numpy as np

def compute_metrics(eval_preds):
    preds, labels = eval_preds
    # In case the model returns more than the prediction logits
    if isinstance(preds, tuple):
        preds = preds[0]

    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

    # Replace -100s in the labels as we can't decode them
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # Some simple post-processing
    decoded_preds = [pred.strip() for pred in decoded_preds]
    decoded_labels = [[label.strip()] for label in decoded_labels]

    result = metric.compute(predictions=decoded_preds, references=decoded_labels)
    return {"bleu": result["score"]}

from transformers import Seq2SeqTrainingArguments

# load environment variables to disable GPU p2p mode for multi-gpu training without p2p mode
# not required for single-gpu training
import os
os.environ['NCCL_P2P_DISABLE'] = '1'
os.environ['NCCL_IB_DISABLE'] = '1'

args = Seq2SeqTrainingArguments(
    f"tag_description_to_thing",
    evaluation_strategy="no",
    logging_dir="tensorboard-log",
    logging_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=64,
    weight_decay=0.01,
    save_total_limit=1, # sets number of checkpoints to save
    num_train_epochs=40, # number of epochs to train
    predict_with_generate=True,
    bf16=True, # disable if gpu doesn't support bfloat16
    push_to_hub=False,
)

from transformers import Seq2SeqTrainer

trainer = Seq2SeqTrainer(
    model,
    args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

trainer.train()
