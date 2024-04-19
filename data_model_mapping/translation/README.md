# Tag Mapping as a translation problem

original course for code: 
https://huggingface.co/learn/nlp-course/en/chapter7/4

## dependencies

I exported my conda env yaml in `env.yaml`, but a high-level overview of the 
packages installed are:

- python=3.12
- pytorch (following instructions from pytorch.org)
- transformers
- sentencepiece
- evaluate
- sacrebleau
- tensorboard
- accelerate
- deepspeed

For pytorch I used:

`
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
`

## What is this section?

This is an example of training a model via fine-tuning of a T5 model from an
input from the `tag_description` field to produce an output of `thing`.

The code is written by utilizing the huggingface libraries 
[dataset, tokenizers, transformers].

Additional libraries like [accelerate, deepspeed] are used to speed up training.

Inference is made easier and GPU-accelerated with [pipeline].

## How to use

### Pre-process

First, pre-process the data .csv files with `data_process.ipynb`. 

Set the path of the data files and import accordingly.

Run the section "create json data for thing", and you should get a json file
with the name 'translations_thing.json'.

This will be the input data for all subsequent operations.

### Training

In `t5_translation_model_train.py`, load the previously generated dataset in 
the `load_dataset()` function.

The file should be ready to run.

To train, execute the following:

`
deepspeed --num_gpus <your-num-of-GPUs> t5_translation_model_train.py
`

If you have a single GPU, you can also just train it normally with:

`
python t5_translation_model_train.py
`

No arguments are necessary.

When the code is run for the first time, 2 new folders are made:

- tag_description_to_thing
- tensorboard-log

In `tag_description_to_thing`, the checkpoint files are updated here. Model for
inference or future training can be loaded from here.

`tensorboard-log` stores the tensorboard training progress files here. Run 
tensorboard and pass this folder path as an argument to get a report in the 
browser.

### Inference

In order to test the newly trained model, you have to load the models from the
checkpoint. 

Update the checkpoint path under `model_checkpoint` variable.

Then run the file:

`
python inference_thing.py
`

The accuracy for training and test will be printed out.

It will take a little long as it will try to generate for both train and test data.