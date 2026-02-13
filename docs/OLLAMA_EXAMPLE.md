# Complete Ollama Integration Example

This is a **complete, working example** of integrating Ollama (local LLM) with ScaleGuard.

## Prerequisites

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama2`
3. Ollama runs automatically on `http://localhost:11434`

## Step-by-Step Implementation

### 1. Update CustomAIProvider in `/backend/ai_integration.py`

Replace the `CustomAIProvider` class with this complete implementation:

```python
class CustomAIProvider(AIProvider):
    """Ollama Local LLM Integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.provider_name = "custom"
        self.api_endpoint = os.getenv("CUSTOM_AI_ENDPOINT", "http://localhost:11434")
        self.model_name = os.getenv("CUSTOM_AI_MODEL", "llama2")
        
    async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """Call Ollama to analyze system health"""
        try:
            import httpx
            
            prompt = self._build_analysis_prompt(analysis, system_data)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_endpoint}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 500
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "No response from AI")
                else:
                    return f"Ollama error: {response.status_code}"
                    
        except Exception as e:
            return f"Custom AI error: {str(e)}"
    
    async def generate_recommendations(self, analysis: RootCauseAnalysis, system_data: Dict) -> List[str]:
        """Generate recommendations using Ollama"""
        try:
            import httpx
            
            # Build bottleneck summary
            bottlenecks_summary = "\n".join([
                f"- {b.name} ({b.type}): Risk {b.risk_score:.0f}, CPU {b.cpu_usage:.0f}%, Memory {b.memory_usage:.0f}%"
                for b in analysis.primary_bottlenecks[:3]
            ])
            
            prompt = f"""As a DevOps expert, provide exactly 5 specific, actionable recommendations for these bottlenecks:

{bottlenecks_summary}

Risk Score: {analysis.risk_score:.1f}/100
Services at Risk: {len(analysis.cascading_failures)}

List each recommendation on a new line, starting with an action verb. Be specific about what to do.

Recommendations:
1."""
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_endpoint}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 300
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("response", "")
                    
                    # Parse recommendations (split by lines, clean up)
                    lines = content.split('\n')
                    recommendations = []
                    
                    for line in lines:
                        line = line.strip()
                        # Remove numbering and keep actionable content
                        if line and len(line) > 10:
                            # Remove common prefixes
                            for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '-', '*', '•']:
                                if line.startswith(prefix):
                                    line = line[len(prefix):].strip()
                            recommendations.append(line)
                    
                    return recommendations[:6]
                else:
                    return []
                    
        except Exception as e:
            return []
    
    def _build_analysis_prompt(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """Build a detailed prompt for Ollama"""
        bottlenecks_summary = "\n".join([
            f"- {b.name} ({b.type}): {b.reason} [Risk: {b.risk_score:.1f}]"
            for b in analysis.primary_bottlenecks[:3]
        ])
        
        return f"""You are a senior DevOps engineer analyzing a microservices system.

SYSTEM STATUS:
- Overall Risk Score: {analysis.risk_score}/100
- Total Services: {system_data.get('total_services', 0)}
- Critical Services: {system_data.get('critical_count', 0)}
- Services at Risk: {len(analysis.cascading_failures)}

DETECTED BOTTLENECKS:
{bottlenecks_summary}

SERVICE TYPES IN SYSTEM:
{', '.join(system_data.get('service_types', []))}

ANALYZE THIS SITUATION:
1. What is the root cause of these bottlenecks?
2. What is the immediate business impact?
3. Which services should be addressed first?
4. What architectural issues might be contributing?

Provide a concise analysis in 3-4 sentences."""
```

### 2. Add Environment Variables

Add to `/backend/.env`:

```bash
# Ollama Configuration
CUSTOM_AI_ENDPOINT=http://localhost:11434
CUSTOM_AI_MODEL=llama2  # or llama3, mistral, codellama, etc.
```

### 3. Install httpx

```bash
cd backend
pip install httpx
# or if using venv:
.\venv\Scripts\pip install httpx
```

### 4. Test It!

```bash
# Start Ollama (if not running)
ollama serve

# Switch to custom provider
curl -X POST "http://localhost:8000/api/ai/switch-provider?provider=custom"

# Create bottlenecks
curl -X POST "http://localhost:8000/api/simulate" \
  -H "Content-Type: application/json" \
  -d '{"traffic_growth_factor": 5.0, "duration_seconds": 30}'

# Get AI analysis
curl "http://localhost:8000/api/analysis"
```

### 5. View in Browser

1. Open http://localhost:5174
2. Go to "Incident Debugger"
3. Click AI provider dropdown → Select "Custom"
4. Click "Run Simulation" or wait for auto-refresh
5. See your local AI's analysis! 🎉

## Ollama Models You Can Use

```bash
# Fast and efficient
ollama pull llama2        # 7B model, good balance
ollama pull mistral       # 7B, very fast
ollama pull phi           # 2.7B, ultra-fast

# More capable
ollama pull llama3        # Better quality
ollama pull codellama     # For technical analysis
ollama pull mixtral       # 8x7B, very capable

# Specialized
ollama pull deepseek-coder  # Excellent for systems analysis
ollama pull wizardcoder     # Good at technical recommendations
```

Update the model in `.env`:
```bash
CUSTOM_AI_MODEL=llama3
```

## Troubleshooting

### "Connection refused"
```bash
# Start Ollama
ollama serve

# Or on Windows, Ollama Desktop should be running
```

### "Model not found"
```bash
# Pull the model first
ollama pull llama2

# List available models
ollama list
```

### "Timeout"
Increase timeout in the code:
```python
async with httpx.AsyncClient(timeout=120.0) as client:
```

Or use a smaller/faster model:
```bash
ollama pull phi  # Much faster than llama2
```

### Slow responses
- Use smaller models (phi, mistral)
- Reduce `num_predict` option (500 → 300)
- Ensure Ollama is using GPU if available

## GPU Acceleration

Ollama automatically uses GPU if available. Check:
```bash
ollama ps  # Shows running models and GPU usage
```

For NVIDIA GPUs, ensure you have CUDA installed.

## Example Output

```json
{
  "ai_insights": "The system is experiencing critical bottlenecks in the database layer. Primary DB is at 100% CPU and memory utilization, indicating query inefficiency or insufficient resources. This is causing cascading failures to dependent services. The 100.0 risk score suggests immediate action is required. Recommend horizontal scaling and query optimization as priority actions.",
  
  "recommended_actions": [
    "Scale Primary DB horizontally by adding 2-3 read replicas",
    "Implement connection pooling with max connections of 100",
    "Add Redis caching layer for frequently accessed queries",
    "Enable slow query logging and optimize queries taking >100ms",
    "Set up auto-scaling policies based on CPU threshold of 80%"
  ]
}
```

## Performance Tips

1. **Keep Ollama running** - First request is slow, subsequent ones are fast
2. **Use smaller models** for faster responses - phi, mistral
3. **Cache prompts** if analyzing similar patterns
4. **Adjust temperature** - Lower (0.1-0.3) for consistent technical analysis
5. **Tune num_predict** - Balance between detail and speed

## Next Steps

1. **Fine-tune prompts** - Adjust `_build_analysis_prompt()` for better results
2. **Add context** - Include historical data, recent changes, etc.
3. **Custom models** - Fine-tune Ollama models on your logs/incidents
4. **Ensemble** - Combine multiple models for better accuracy
5. **Caching** - Cache similar analyses to reduce latency

Enjoy your local AI-powered DevOps assistant! 🚀
