#!/usr/bin/env python3
"""
Usage Example: How to use the generated training data for AI model training
This script demonstrates how to load and use the training data for different ML frameworks
"""

import json
import random
from typing import List, Dict, Any

def load_training_data(file_path: str) -> List[Dict[str, Any]]:
    """Load training data from JSON file"""
    with open(file_path, 'r') as f:
        dataset = json.load(f)
    return dataset['examples']

def format_for_openai_finetuning(examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format training data for OpenAI fine-tuning (jsonl format)"""
    formatted_examples = []
    
    for example in examples:
        # Create system prompt
        system_prompt = """You are JARVIS, an expert DevOps AI assistant for ScaleGuard monitoring system. 
Analyze system performance data and provide expert insights and actionable recommendations."""
        
        # Format input data as user message
        input_data = example['input_data']
        user_message = f"""SYSTEM HEALTH ANALYSIS REQUEST
===========================================

SYSTEM STATE:
- Risk Score: {input_data['system_state']['risk_score']:.1f}/100
- Services: {input_data['system_state']['total_services']} total, {input_data['system_state']['critical_count']} critical
- Context: {input_data['system_state']['time_context']}
- Business Impact: {input_data['system_state']['business_impact']}

DETECTED BOTTLENECKS:"""

        for bottleneck in input_data['bottlenecks']:
            user_message += f"""
- {bottleneck['name']} ({bottleneck['type']})
  CPU: {bottleneck['cpu_usage']:.1f}%, Memory: {bottleneck['memory_usage']:.1f}%
  Risk: {bottleneck['risk_score']:.1f}/100
  Issue: {bottleneck['reason']}"""

        if input_data['cascading_failures']:
            user_message += f"""

CASCADING FAILURES:
{', '.join(input_data['cascading_failures'])}"""

        user_message += """

Please provide:
1. Expert analysis of the situation
2. Six specific actionable recommendations"""

        # Format expected output
        assistant_response = f"""ANALYSIS:
{example['expected_analysis']}

RECOMMENDATIONS:
"""
        for i, rec in enumerate(example['expected_recommendations'], 1):
            assistant_response += f"{i}. {rec}\n"

        # OpenAI fine-tuning format
        formatted_example = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_response.strip()}
            ]
        }
        
        formatted_examples.append(formatted_example)
    
    return formatted_examples

def format_for_huggingface(examples: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Format training data for Hugging Face transformers"""
    inputs = []
    outputs = []
    
    for example in examples:
        # Create input text
        input_data = example['input_data']
        
        input_text = f"<system_state>risk_score:{input_data['system_state']['risk_score']:.1f}|"
        input_text += f"services:{input_data['system_state']['total_services']}|"
        input_text += f"critical:{input_data['system_state']['critical_count']}|"
        input_text += f"context:{input_data['system_state']['time_context']}</system_state>"
        
        input_text += "<bottlenecks>"
        for bottleneck in input_data['bottlenecks']:
            input_text += f"{bottleneck['name']}[{bottleneck['type']}]:"
            input_text += f"cpu={bottleneck['cpu_usage']:.1f},"
            input_text += f"mem={bottleneck['memory_usage']:.1f},"
            input_text += f"risk={bottleneck['risk_score']:.1f}|"
        input_text += "</bottlenecks>"
        
        if input_data['cascading_failures']:
            input_text += f"<cascades>{','.join(input_data['cascading_failures'])}</cascades>"
        
        # Create output text
        output_text = f"<analysis>{example['expected_analysis']}</analysis>"
        output_text += "<recommendations>"
        output_text += "|".join(example['expected_recommendations'])
        output_text += "</recommendations>"
        
        inputs.append(input_text)
        outputs.append(output_text)
    
    return {"input": inputs, "output": outputs}

def create_ollama_modelfile(model_name: str = "scaleGuard-ai") -> str:
    """Generate Ollama Modelfile for local AI training"""
    modelfile_content = f"""FROM llama2:7b

# Set parameters
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096

# System prompt for ScaleGuard
SYSTEM \"\"\"
You are JARVIS, an expert DevOps AI assistant specialized in microservices monitoring and incident response. 

Your expertise includes:
- Database performance optimization (PostgreSQL, MySQL, MongoDB) 
- API service scaling and load balancing
- Cache layer optimization (Redis, Memcached)
- Queue system management (RabbitMQ, Kafka)
- Infrastructure monitoring and alerting
- Incident response and root cause analysis

Always provide:
1. Technical analysis with specific metrics
2. Immediate actionable recommendations
3. Long-term architectural improvements
4. Business impact assessment

Response format:
- Start analysis with risk level indicator (🔧 🆠🚨 🔥)
- Include specific resource utilization percentages
- Provide 6 concrete, executable recommendations
- Consider cascade effects and dependencies
\"\"\"

# Template for responses
TEMPLATE \"\"\"{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

{{ .Response }}<|eot_id|>\"\"\"
"""
    
    with open(f"Modelfile.{model_name}", 'w', encoding='utf-8') as f:
        f.write(modelfile_content)
    
    return f"Modelfile.{model_name}"

def generate_training_scripts():
    """Generate training scripts for different platforms"""
    
    # OpenAI fine-tuning script
    openai_script = """#!/usr/bin/env python3
\"\"\"OpenAI Fine-tuning Script for ScaleGuard AI\"\"\"

import openai
import json

# Load and format training data
from training_usage_example import load_training_data, format_for_openai_finetuning

examples = load_training_data('training_data_medium.json')
formatted_data = format_for_openai_finetuning(examples)

# Save as JSONL for OpenAI
with open('scaleGuard_training.jsonl', 'w') as f:
    for example in formatted_data:
        f.write(json.dumps(example) + '\\n')

print("Training data saved to scaleGuard_training.jsonl")
print("Upload to OpenAI and run:")
print("openai api fine_tunes.create -t scaleGuard_training.jsonl -m gpt-3.5-turbo")
"""
    
    # Hugging Face training script
    hf_script = """#!/usr/bin/env python3
\"\"\"Hugging Face Training Script for ScaleGuard AI\"\"\"

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
"""
    
    # Ollama setup script
    ollama_script = """#!/bin/bash
# Ollama Local AI Setup for ScaleGuard

echo "Setting up ScaleGuard AI with Ollama..."

# Pull base model
ollama pull llama2:7b

# Create custom model
ollama create scaleGuard-ai -f Modelfile.scaleGuard-ai

echo "ScaleGuard AI model created!"
echo ""
echo "Test the model:"
echo "ollama run scaleGuard-ai"
echo ""
echo "Example query:"
echo 'curl -X POST http://localhost:11434/api/generate -d "{\\"model\\": \\"scaleGuard-ai\\", \\"prompt\\": \\"Analyze: Database CPU 95%, Memory 87%, 3 cascading failures\\"}"'
"""
    
    # Save scripts
    with open('train_openai.py', 'w') as f:
        f.write(openai_script)
    
    with open('train_huggingface.py', 'w') as f:
        f.write(hf_script)
    
    with open('setup_ollama.sh', 'w') as f:
        f.write(ollama_script)
    
    print("Training scripts generated:")
    print("- train_openai.py (OpenAI fine-tuning)")
    print("- train_huggingface.py (Hugging Face transformers)")
    print("- setup_ollama.sh (Local Ollama setup)")

def main():
    """Main demonstration function"""
    print("ScaleGuard AI Training Data Usage Examples")
    print("=" * 50)
    
    # Load sample data
    print("\\n1. Loading training data...")
    try:
        examples = load_training_data('training_data_small.json')
        print(f"Loaded {len(examples)} training examples")
    except FileNotFoundError:
        print("Training data not found. Run training_data_generator.py first.")
        return
    
    # Show data structure
    print("\\n2. Sample training example structure:")
    sample = examples[0]
    print("Input data keys:", list(sample['input_data'].keys()))
    print("System state keys:", list(sample['input_data']['system_state'].keys()))
    print("Bottleneck keys:", list(sample['input_data']['bottlenecks'][0].keys()))
    print("Analysis length:", len(sample['expected_analysis']), "characters")
    print("Recommendations count:", len(sample['expected_recommendations']))
    
    # Format for different platforms
    print("\\n3. Formatting for OpenAI fine-tuning...")
    openai_format = format_for_openai_finetuning(examples[:2])
    print("OpenAI format keys:", list(openai_format[0].keys()))
    print("Message roles:", [msg['role'] for msg in openai_format[0]['messages']])
    
    print("\\n4. Formatting for Hugging Face...")
    hf_format = format_for_huggingface(examples[:2])
    print("HF format keys:", list(hf_format.keys()))
    print("Input sample length:", len(hf_format['input'][0]))
    print("Output sample length:", len(hf_format['output'][0]))
    
    print("\\n5. Creating Ollama Modelfile...")
    modelfile = create_ollama_modelfile("scaleGuard-ai")
    print(f"Modelfile created: {modelfile}")
    
    print("\\n6. Generating training scripts...")
    generate_training_scripts()
    
    print("\\n" + "=" * 50)
    print("NEXT STEPS:")
    print("1. Choose your preferred AI platform:")
    print("   - OpenAI: High quality, but requires API costs")
    print("   - Hugging Face: Open source, requires GPU")
    print("   - Ollama: Local deployment, privacy-focused")
    print()
    print("2. Run the appropriate training script")
    print("3. Test the model with ScaleGuard system data")
    print("4. Iterate and improve based on results")
    
    # Show a sample formatted input/output
    print("\\n" + "=" * 50)
    print("SAMPLE FORMATTED TRAINING PAIR:")
    print("=" * 50)
    
    sample_formatted = format_for_openai_finetuning([examples[0]])[0]
    print("USER MESSAGE:")
    print(sample_formatted['messages'][1]['content'][:400] + "...")
    print("\\nASSISTANT RESPONSE:")
    print(sample_formatted['messages'][2]['content'][:400] + "...")

if __name__ == "__main__":
    main()