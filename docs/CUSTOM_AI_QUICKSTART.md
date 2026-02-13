# Custom AI Integration - Quick Start

## 🚀 Integrate Your Own AI Model in 3 Steps

### Step 1: Edit CustomAIProvider

Open `/backend/ai_integration.py` and find the `CustomAIProvider` class (JARVIS).

### Step 2: Add Your AI Configuration

```python
def __init__(self, api_key: Optional[str] = None):
    super().__init__()
    self.provider_name = "jarvis"  # Your custom AI name
    
    # ADD YOUR CONFIGURATION
    self.api_endpoint = os.getenv("CUSTOM_AI_ENDPOINT", "http://localhost:11434")
    self.model_name = os.getenv("CUSTOM_AI_MODEL", "llama2")
```

### Step 3: Implement the Methods

#### For Ollama (Local LLM):

```python
async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
    import httpx
    prompt = self._build_analysis_prompt(analysis, system_data)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{self.api_endpoint}/api/generate",
            json={"model": self.model_name, "prompt": prompt, "stream": False}
        )
        return response.json()["response"]
```

#### For Hugging Face:

```python
def __init__(self, api_key: Optional[str] = None):
    super().__init__()
    self.provider_name = "custom"
    from transformers import pipeline
    self.generator = pipeline('text-generation', model='gpt2')

async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
    prompt = self._build_analysis_prompt(analysis, system_data)
    result = self.generator(prompt, max_length=500)
    return result[0]['generated_text']
```

#### For Custom API:

```python
async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
    import httpx
    prompt = self._build_analysis_prompt(analysis, system_data)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            self.api_endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"prompt": prompt}
        )
        return response.json()["analysis"]
```

## 🧪 Test Your Integration

### 1. Switch to JARVIS Provider

```bash
curl -X POST "http://localhost:8000/api/ai/switch-provider?provider=jarvis"
```

### 2. Run Analysis

```bash
# Create bottlenecks
curl -X POST "http://localhost:8000/api/simulate" \
  -H "Content-Type: application/json" \
  -d '{"traffic_growth_factor": 5.0, "duration_seconds": 30}'

# Get AI analysis
curl "http://localhost:8000/api/analysis"
```

### 3. View in UI

1. Go to http://localhost:5174
2. Open "Incident Debugger"
3. Use dropdown to switch to "JARVIS" provider
4. Run simulation and see your AI's analysis!

## 📚 More Examples

See `CUSTOM_AI_GUIDE.md` for:
- ✅ Ollama integration
- ✅ Azure OpenAI
- ✅ OpenRouter
- ✅ Custom REST APIs
- ✅ Fine-tuning tips
- ✅ Troubleshooting

## 💡 Environment Variables

Add to `/backend/.env`:

```bash
CUSTOM_AI_ENDPOINT=http://localhost:11434
CUSTOM_AI_MODEL=llama2
CUSTOM_AI_API_KEY=your_key_here
```

## ✨ What You Get

Your custom AI will:
- 🔍 Analyze system bottlenecks with your model
- 💡 Generate actionable recommendations
- 📊 Display in the beautiful ScaleGuard UI
- 🔄 Switch between providers on-the-fly

Happy integrating! 🎉
