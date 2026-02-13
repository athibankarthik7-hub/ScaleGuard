#!/bin/bash
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
echo 'curl -X POST http://localhost:11434/api/generate -d "{\"model\": \"scaleGuard-ai\", \"prompt\": \"Analyze: Database CPU 95%, Memory 87%, 3 cascading failures\"}"'
