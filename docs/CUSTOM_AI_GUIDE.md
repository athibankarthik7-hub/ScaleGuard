# Custom AI Integration Guide

This guide shows you how to integrate your own AI model into ScaleGuard for analyzing system bottlenecks and generating recommendations.

## Quick Start

1. **Edit the CustomAIProvider class** in `/backend/ai_integration.py`
2. **Add your AI configuration** (API keys, endpoints, model paths)
3. **Implement the two main methods**:
   - `analyze_system_health()` - Analyzes bottlenecks and provides insights
   - `generate_recommendations()` - Generates actionable recommendations
4. **Switch to your provider**: `POST /api/ai/switch-provider?provider=custom`

## Integration Examples

### Example 1: Ollama (Local LLM)

Perfect for running AI locally without API costs.

```python
def __init__(self, api_key: Optional[str] = None):
    super().__init__()
    self.provider_name = "custom"
    self.api_endpoint = os.getenv("CUSTOM_AI_ENDPOINT", "http://localhost:11434")
    self.model_name = os.getenv("CUSTOM_AI_MODEL", "llama2")

async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
    import httpx
    
    prompt = self._build_analysis_prompt(analysis, system_data)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{self.api_endpoint}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"]
```

**Setup Ollama:**
```bash
# Install Ollama
# Visit: https://ollama.ai

# Pull a model
ollama pull llama2

# Ollama will run on http://localhost:11434 by default
```

### Example 2: Hugging Face Transformers

Use Hugging Face models directly in Python.

```python
def __init__(self, api_key: Optional[str] = None):
    super().__init__()
    self.provider_name = "custom"
    from transformers import pipeline
    self.generator = pipeline(
        'text-generation',
        model=os.getenv("CUSTOM_AI_MODEL", "gpt2"),
        device="cpu"  # or "cuda" for GPU
    )

async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
    prompt = self._build_analysis_prompt(analysis, system_data)
    
    result = self.generator(
        prompt,
        max_length=500,
        num_return_sequences=1,
        temperature=0.7
    )
    
    return result[0]['generated_text']
```

**Install dependencies:**
```bash
pip install transformers torch
```

### Example 3: Azure OpenAI

If you're using Azure OpenAI Service.

```python
def __init__(self, api_key: Optional[str] = None):
    super().__init__()
    self.provider_name = "custom"
    self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
    self.api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")

async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
    from openai import AsyncAzureOpenAI
    
    client = AsyncAzureOpenAI(
        api_key=self.api_key,
        api_version="2024-02-01",
        azure_endpoint=self.api_endpoint
    )
    
    prompt = self._build_analysis_prompt(analysis, system_data)
    
    response = await client.chat.completions.create(
        model=self.deployment_name,
        messages=[
            {"role": "system", "content": "You are a DevOps expert analyzing system performance."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.3
    )
    
    return response.choices[0].message.content
```

**Environment variables (.env):**
```bash
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

### Example 4: OpenRouter (Multi-Model API)

Access multiple AI models through a single API.

```python
def __init__(self, api_key: Optional[str] = None):
    super().__init__()
    self.provider_name = "custom"
    self.api_key = os.getenv("OPENROUTER_API_KEY")
    self.model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-sonnet")

async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
    import httpx
    
    prompt = self._build_analysis_prompt(analysis, system_data)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8000",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )
        return response.json()["choices"][0]["message"]["content"]
```

### Example 5: Custom REST API

If you have your own AI service deployed.

```python
def __init__(self, api_key: Optional[str] = None):
    super().__init__()
    self.provider_name = "custom"
    self.api_endpoint = os.getenv("CUSTOM_AI_ENDPOINT", "http://your-ai-service.com/api")
    self.api_key = os.getenv("CUSTOM_AI_API_KEY")

async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
    import httpx
    
    prompt = self._build_analysis_prompt(analysis, system_data)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{self.api_endpoint}/analyze",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.3
            }
        )
        return response.json()["analysis"]

async def generate_recommendations(self, analysis: RootCauseAnalysis, system_data: Dict) -> List[str]:
    import httpx
    
    bottlenecks_summary = "\n".join([
        f"- {b.name} ({b.type}): Risk {b.risk_score:.0f}, CPU {b.cpu_usage:.0f}%, Memory {b.memory_usage:.0f}%"
        for b in analysis.primary_bottlenecks[:3]
    ])
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{self.api_endpoint}/recommendations",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "bottlenecks": bottlenecks_summary,
                "risk_score": analysis.risk_score
            }
        )
        return response.json()["recommendations"]
```

## Testing Your Integration

### 1. Test locally first

```python
# Add this at the end of ai_integration.py for testing
if __name__ == "__main__":
    import asyncio
    from mock_data import generate_mock_system
    from graph import SystemGraph
    
    async def test_custom_ai():
        provider = CustomAIProvider()
        
        # Create test data
        from models import RootCauseAnalysis, BottleneckNode
        test_bottleneck = BottleneckNode(
            id="test-db",
            name="Test DB",
            type="database",
            risk_score=85.0,
            centrality=0.5,
            cpu_usage=95.0,
            memory_usage=90.0,
            reason="CPU overload"
        )
        
        test_analysis = RootCauseAnalysis(
            primary_bottlenecks=[test_bottleneck],
            cascading_failures=["Service A", "Service B"],
            recommended_actions=[],
            risk_score=85.0
        )
        
        test_system_data = {
            "total_services": 10,
            "critical_count": 3,
            "service_types": ["api", "database", "cache"]
        }
        
        # Test insights
        insights = await provider.analyze_system_health(test_analysis, test_system_data)
        print("AI Insights:", insights)
        
        # Test recommendations
        recommendations = await provider.generate_recommendations(test_analysis, test_system_data)
        print("\nRecommendations:", recommendations)
    
    asyncio.run(test_custom_ai())
```

Run the test:
```bash
cd backend
python ai_integration.py
```

### 2. Switch to custom provider

```bash
# Switch to your custom AI
curl -X POST "http://localhost:8000/api/ai/switch-provider?provider=custom"

# Trigger analysis
curl "http://localhost:8000/api/analysis"
```

### 3. View in UI

1. Go to http://localhost:5174
2. Navigate to "Incident Debugger"
3. Use the AI provider dropdown to switch to "Custom"
4. Run a simulation to generate bottlenecks
5. View AI-powered insights and recommendations

## Environment Variables

Add these to your `/backend/.env` file:

```bash
# Custom AI Configuration
CUSTOM_AI_ENDPOINT=http://localhost:11434
CUSTOM_AI_MODEL=llama2
CUSTOM_AI_API_KEY=your_api_key_here

# Or for Azure OpenAI
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Or for OpenRouter
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=anthropic/claude-3-sonnet
```

## Advanced: Fine-tuning for ScaleGuard

To get better results from your AI model, consider:

1. **Fine-tuning on DevOps knowledge** - Train on incident reports, runbooks, and system documentation
2. **Prompt engineering** - Adjust the `_build_analysis_prompt()` method to provide more context
3. **Few-shot examples** - Add example analyses in your prompts
4. **Output formatting** - Parse and structure AI responses consistently

### Sample prompt template:

```python
def _build_analysis_prompt(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
    return f"""
You are a senior DevOps engineer analyzing a microservices system.

CURRENT SITUATION:
Risk Score: {analysis.risk_score}/100
Services at Risk: {len(analysis.cascading_failures)}
Critical Bottlenecks: {len(analysis.primary_bottlenecks)}

BOTTLENECKS DETECTED:
{self._format_bottlenecks(analysis.primary_bottlenecks)}

TASK:
1. Identify the root cause of the bottlenecks
2. Assess the immediate business impact
3. Provide 3-5 specific, actionable recommendations
4. Prioritize recommendations by urgency

FORMAT YOUR RESPONSE AS:
**Root Cause:** [brief explanation]
**Impact:** [business impact assessment]
**Recommendations:**
1. [action 1]
2. [action 2]
...
"""
```

## Troubleshooting

### Issue: "Custom AI provider not found"
**Solution:** Make sure you registered the provider in AIManager's `self.providers` dict

### Issue: Timeout errors
**Solution:** Increase httpx timeout: `httpx.AsyncClient(timeout=60.0)`

### Issue: Model not loading
**Solution:** Check model name/path and ensure dependencies are installed

### Issue: Out of memory
**Solution:** Use smaller models or offload to GPU with `device="cuda"`

## Need Help?

- Check the other provider implementations (OpenAIProvider, GeminiProvider) for reference
- Test with the mock provider first to ensure data flow is correct
- Use logging: `import logging; logging.info(f"AI response: {response}")`
- Check backend logs for errors: `uvicorn main:app --reload --log-level debug`

## What's Next?

Once your custom AI is integrated:
- Add more sophisticated prompt engineering
- Implement caching for repeated queries
- Add fallback logic for when your AI is unavailable
- Track AI response quality and iterate on prompts
- Consider adding multi-model ensemble approaches

Happy integrating! 🚀
