#!/usr/bin/env python3
"""OpenAI Fine-tuning Script for ScaleGuard AI"""

import openai
import json

# Load and format training data
from training_usage_example import load_training_data, format_for_openai_finetuning

examples = load_training_data('training_data_medium.json')
formatted_data = format_for_openai_finetuning(examples)

# Save as JSONL for OpenAI
with open('scaleGuard_training.jsonl', 'w') as f:
    for example in formatted_data:
        f.write(json.dumps(example) + '\n')

print("Training data saved to scaleGuard_training.jsonl")
print("Upload to OpenAI and run:")
print("openai api fine_tunes.create -t scaleGuard_training.jsonl -m gpt-3.5-turbo")
