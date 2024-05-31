
# import data and load dataset
from datasets import load_from_disk
# Path to saved combined_dataset
# file_path = 'combined_data_reference'
file_path = 'combined_data'
split_datasets = load_from_disk(file_path)

# prepare tokenizer
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("t5-base", return_tensors="pt")
# Define additional special tokens
additional_special_tokens = ["<THING_START>", "<THING_END>", "<PROPERTY_START>", "<PROPERTY_END>", "<attn>"]
# Add the additional special tokens to the tokenizer
tokenizer.add_special_tokens({"additional_special_tokens": additional_special_tokens})

max_length = 64

def preprocess_function(examples):
    inputs = [ex["tag_description"] for ex in examples['translation']]
    targets = [ex["thing_property"] for ex in examples['translation']]
    # text_target sets the corresponding label to inputs
    # there is no need to create a separate 'labels'
    model_inputs = tokenizer(
        inputs, text_target=targets, max_length=max_length, truncation=True
    )
    return model_inputs

tokenized_datasets = split_datasets.map(
    preprocess_function,
    batched=True,
    remove_columns=split_datasets["train"].column_names,
)


from transformers import AutoModelForSeq2SeqLM
model_checkpoint = "t5-base"
model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)
from transformers import DataCollatorForSeq2Seq

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
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

import os
os.environ['NCCL_P2P_DISABLE'] = '1'
os.environ['NCCL_IB_DISABLE'] = '1'

args = Seq2SeqTrainingArguments(
    # f"checkpoint_reference_20",
    f"checkpoint_attention_token_40",
    evaluation_strategy="no",
    # logging_dir="tensorboard-log",
    # logging_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=64,
    auto_find_batch_size=True,
    ddp_find_unused_parameters=False,
    weight_decay=0.01,
    save_total_limit=1,
    num_train_epochs=40,
    predict_with_generate=True,
    bf16=True,
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
