#!/usr/bin/env python3
"""Hugging Face Training Script for ScaleGuard AI"""

from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from datasets import Dataset
import torch

# Load and format data
from training_usage_example import load_training_data, format_for_huggingface

examples = load_training_data('training_data_large.json')
formatted_data = format_for_huggingface(examples)

# Create dataset
dataset = Dataset.from_dict(formatted_data)

# Load model and tokenizer
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Tokenize data
def tokenize_function(examples):
    inputs = tokenizer(examples['input'], truncation=True, padding=True, max_length=512)
    targets = tokenizer(examples['output'], truncation=True, padding=True, max_length=512)
    inputs['labels'] = targets['input_ids']
    return inputs

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir='./scaleGuard-ai-model',
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=100,
    save_steps=1000,
    eval_steps=1000,
)

# Create trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
)

# Train model
trainer.train()
trainer.save_model()

print("Model training completed!")
print("Model saved to ./scaleGuard-ai-model")
