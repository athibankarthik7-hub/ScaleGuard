# ScaleGuard Training Scripts

This directory contains all AI training-related scripts and data for ScaleGuard.

## 📁 Directory Structure

```
backend/training/
├── data/                          # Training datasets
│   ├── training_data_small.json   # 50 examples
│   ├── training_data_medium.json  # 500 examples
│   └── training_data_large.json   # 2000 examples
├── training_data_generator.py     # Generate training data
├── training_data_validator.py     # Validate training data quality
├── training_usage_example.py      # Format data for different platforms
├── train_openai.py               # Fine-tune OpenAI models
└── train_huggingface.py          # Train Hugging Face models
```

## 🚀 Quick Start

### 1. Generate Training Data

```bash
cd backend/training
python training_data_generator.py
```

This creates three datasets:
- `data/training_data_small.json` (50 examples) - Quick testing
- `data/training_data_medium.json` (500 examples) - Development
- `data/training_data_large.json` (2000 examples) - Production training

### 2. Validate Training Data

```bash
python training_data_validator.py
```

Validates:
- JSON structure correctness
- Scenario diversity
- Metric value ranges
- Recommendation quality

### 3. Format for Your Platform

```bash
python training_usage_example.py
```

Outputs formatted data for:
- **OpenAI** - Fine-tuning format
- **Hugging Face** - Dataset format with JSONL
- **Ollama** - Modelfile format

### 4. Train Models

**OpenAI Fine-tuning:**
```bash
python train_openai.py
```

**Hugging Face Training:**
```bash
python train_huggingface.py
```

## 📊 Training Data Format

Each example contains:

```json
{
  "scenario": "E-commerce platform Black Friday traffic surge",
  "service_type": "web_server",
  "metrics": {
    "cpu_usage": 85.5,
    "memory_usage": 78.2,
    "error_rate": 3.5,
    "latency": 450.0,
    "request_rate": 5000
  },
  "bottleneck_indicators": [
    "High CPU usage",
    "Increased latency"
  ],
  "recommendations": [
    "Scale horizontally by adding 2-3 instances",
    "Enable caching for static assets"
  ],
  "severity": "high"
}
```

## 🎯 Service Types

- `web_server` - Frontend/API servers
- `database` - SQL/NoSQL databases
- `cache` - Redis, Memcached
- `message_queue` - RabbitMQ, Kafka
- `load_balancer` - Nginx, HAProxy
- `api_gateway` - Kong, Traefik

## 📈 Severity Levels

- `low` - Minor performance issues
- `medium` - Noticeable degradation
- `high` - Critical performance problems
- `critical` - Service failure imminent

## 🔧 Configuration

Edit `training_data_generator.py` to customize:

```python
# Number of examples
SMALL_SIZE = 50
MEDIUM_SIZE = 500
LARGE_SIZE = 2000

# Service type distribution
SERVICE_TYPES = ['web_server', 'database', 'cache', ...]

# Metric ranges
CPU_RANGE = (0, 100)
MEMORY_RANGE = (0, 100)
ERROR_RATE_RANGE = (0, 50)
```

## 📚 Documentation

For complete documentation, see:
- [Training Data Specifications](../../docs/TRAINING_DATA_SPECS.md)
- [Custom AI Guide](../../docs/CUSTOM_AI_GUIDE.md)
- [Ollama Examples](../../docs/OLLAMA_EXAMPLE.md)

## 🧪 Testing

Run validator to check data quality:

```bash
python training_data_validator.py
```

Expected output:
- Validation rate: 60-70%
- Invalid examples identified with reasons
- Metric distribution analysis

## 💡 Tips

1. **Start Small** - Test with small dataset first
2. **Validate Often** - Run validator after changes
3. **Diverse Scenarios** - Include various service types
4. **Realistic Metrics** - Use production-like values
5. **Quality > Quantity** - 500 good examples > 2000 mediocre ones

## 🤝 Contributing

When adding new scenarios:
1. Use realistic metric values
2. Provide actionable recommendations
3. Include bottleneck indicators
4. Validate before committing
5. Document new service types

## 📝 Notes

- Data is auto-generated with realistic distributions
- All values are within operational ranges
- Scenarios cover common DevOps situations
- Ready for production AI training
