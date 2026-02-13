from typing import Optional, List, Dict
import os
from models import RootCauseAnalysis, BottleneckNode
import json

class AIProvider:
    """Base class for AI integration"""
    
    def __init__(self):
        self.provider_name = "base"
    
    async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """Generate AI insights for system health analysis"""
        raise NotImplementedError
    
    async def predict_failures(self, metrics_history: List[Dict]) -> str:
        """Predict potential future failures"""
        raise NotImplementedError
    
    async def suggest_optimizations(self, bottlenecks: List[BottleneckNode]) -> List[str]:
        """Suggest specific optimizations"""
        raise NotImplementedError
    
    async def generate_recommendations(self, analysis: RootCauseAnalysis, system_data: Dict) -> List[str]:
        """Generate AI-powered recommendations"""
        raise NotImplementedError

class OpenAIProvider(AIProvider):
    """OpenAI GPT integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.provider_name = "openai"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
    async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """Use GPT to analyze system health patterns"""
        if not self.api_key:
            return "OpenAI API key not configured"
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            
            prompt = self._build_analysis_prompt(analysis, system_data)
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior DevOps engineer analyzing system performance issues."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"AI analysis failed: {str(e)}"
    
    async def generate_recommendations(self, analysis: RootCauseAnalysis, system_data: Dict) -> List[str]:
        """Generate AI-powered recommendations"""
        if not self.api_key:
            return []
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            
            prompt = self._build_dynamic_recommendations_prompt(analysis, system_data)
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a DevOps expert providing specific, actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            recommendations = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
            return recommendations[:6]
            
        except Exception as e:
            return []
    
    def _build_analysis_prompt(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """Build a comprehensive, context-aware prompt for AI analysis"""
        
        # Current system state
        risk_level = "CRITICAL" if analysis.risk_score > 80 else "HIGH" if analysis.risk_score > 60 else "MEDIUM" if analysis.risk_score > 30 else "LOW"
        time_context = "during peak business hours" if hash(str(analysis.risk_score)) % 3 == 0 else "during maintenance window" if hash(str(analysis.risk_score)) % 3 == 1 else "during normal operations"
        
        bottlenecks_detail = ""
        for i, b in enumerate(analysis.primary_bottlenecks[:3], 1):
            criticality = "CRITICAL" if b.risk_score > 80 else "HIGH" if b.risk_score > 60 else "MODERATE"
            performance = f"CPU: {b.cpu_usage:.0f}% | Memory: {b.memory_usage:.0f}% | Risk: {b.risk_score:.0f}"
            bottlenecks_detail += f"{i}. {b.name} ({b.type}) - {criticality}\n   Metrics: {performance}\n   Issue: {b.reason}\n\n"
        
        cascade_impact = ""
        if analysis.cascading_failures:
            cascade_impact = f"\nCASCADE ALERT: {len(analysis.cascading_failures)} downstream services at risk:\n" + "\n".join([f"- {service}" for service in analysis.cascading_failures[:5]])
        
        business_context = self._get_business_context(analysis.risk_score, analysis.primary_bottlenecks)
        
        system_health = f"{system_data.get('critical_count', 0)}/{system_data.get('total_services', 0)} services in critical state"
        
        return f"""You are a Senior DevOps Engineer analyzing a production microservices system {time_context}.

SYSTEM HEALTH OVERVIEW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Risk: {analysis.risk_score:.1f}/100 ({risk_level} PRIORITY)
System Status: {system_health}
Architecture: {', '.join(system_data.get('service_types', ['unknown']))}

ACTIVE BOTTLENECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{bottlenecks_detail.strip()}
{cascade_impact}

BUSINESS CONTEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{business_context}

PROVIDE YOUR EXPERT ANALYSIS:
1. Root cause identification (what's really causing this?)
2. Immediate business impact assessment
3. Critical path to resolution
4. Long-term prevention strategy

PROVIDE YOUR EXPERT ANALYSIS:
1. Root cause identification (what's really causing this?)
2. Immediate business impact assessment
3. Critical path to resolution
4. Long-term prevention strategy

Be specific, actionable, and consider the interdependencies. This is a live production environment."""
    
    def _get_business_context(self, risk_score: float, bottlenecks: List) -> str:
        """Generate realistic business context based on system state"""
        if risk_score > 90:
            return "⚠️  REVENUE IMPACT: Payment processing affected, customer complaints increasing. CEO escalation likely."
        elif risk_score > 70:
            return "📊 PERFORMANCE DEGRADATION: User experience impacted, potential customer loss. SLA breach imminent."
        elif risk_score > 50:
            return "⚡ CAPACITY CONCERNS: System under stress, response times increasing. Proactive action needed."
        else:
            return "🔧 OPTIMIZATION OPPORTUNITY: System stable but inefficient, good time for improvements."
            
    def _build_dynamic_recommendations_prompt(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """Build context-aware recommendations prompt"""
        priority_issues = []
        for b in analysis.primary_bottlenecks[:3]:
            urgency = "IMMEDIATE" if b.cpu_usage > 90 or b.memory_usage > 90 else "HIGH" if b.risk_score > 70 else "MEDIUM"
            priority_issues.append(f"• {b.name}: {urgency} - {b.type} service at {b.cpu_usage:.0f}% CPU, {b.memory_usage:.0f}% RAM")
            
        system_constraints = []
        if len(analysis.primary_bottlenecks) > 3:
            system_constraints.append("Multiple bottlenecks indicate architectural issues")
        if analysis.risk_score > 80:
            system_constraints.append("High-risk situation requires immediate scaling")
        if len(analysis.cascading_failures) > 2:
            system_constraints.append("Cascade failures suggest tight coupling between services")
            
        return f"""You are a DevOps architect providing emergency response recommendations.

CRITICAL ISSUES REQUIRING IMMEDIATE ACTION:
{chr(10).join(priority_issues)}

SYSTEM CONSTRAINTS:
{chr(10).join(system_constraints) if system_constraints else "System appears stable with isolated issues"}

RISK LEVEL: {analysis.risk_score:.0f}/100
DOWNSTREAM IMPACT: {len(analysis.cascading_failures)} services affected

Provide 6 specific, prioritized recommendations. Format as action-oriented statements.
Consider: scaling, optimization, monitoring, architecture changes, immediate fixes.

Each recommendation should be immediately executable by a DevOps team."""

class GeminiProvider(AIProvider):
    """Google Gemini integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.provider_name = "gemini"
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        
    async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        if not self.api_key:
            return "Google AI API key not configured"
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            # Updated to lighter model for better rate limits
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            prompt = self._build_gemini_prompt(analysis, system_data)
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Gemini analysis failed: {str(e)}"
    
    async def generate_recommendations(self, analysis: RootCauseAnalysis, system_data: Dict) -> List[str]:
        """Generate AI-powered recommendations"""
        if not self.api_key:
            return []
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            prompt = self._build_dynamic_recommendations_prompt(analysis, system_data)
            
            response = model.generate_content(prompt)
            recommendations = [line.strip() for line in response.text.split('\n') if line.strip() and not line.strip().startswith('#') and len(line.strip()) > 10]
            return recommendations[:6]
            
        except Exception as e:
            return []
    
    def _build_gemini_prompt(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """Build Gemini-optimized analysis prompt"""
        return self._build_analysis_prompt(analysis, system_data) + "\n\n**IMPORTANT**: Provide a concise but comprehensive analysis. Focus on immediate actionable insights."

class ClaudeProvider(AIProvider):
    """Anthropic Claude integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.provider_name = "claude"
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
    async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        if not self.api_key:
            return "Anthropic API key not configured"
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            prompt = self._build_claude_prompt(analysis, system_data)
            
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=400,
                temperature=0.2,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"Claude analysis failed: {str(e)}"
    
    def _build_claude_prompt(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        return f"""
Analyze this distributed system health assessment:

System Risk: {analysis.risk_score}/100
Primary Issues: {len(analysis.primary_bottlenecks)} bottlenecks identified
Cascade Risk: {len(analysis.cascading_failures)} potential failure chains

Critical Services:
{chr(10).join([f"• {b.name} ({b.type}): CPU {b.cpu_usage:.1f}%, Memory {b.memory_usage:.1f}%" for b in analysis.primary_bottlenecks[:3]])}

As a senior SRE, provide:
1. Root cause assessment
2. Business impact severity (High/Medium/Low)
3. Top 3 immediate actions
4. Long-term architectural recommendations

Be specific and actionable.
        """

class MockAIProvider(AIProvider):
    """Mock AI provider for testing/demo without API keys"""
    
    def __init__(self):
        super().__init__()
        self.provider_name = "mock"
        
    async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """Generate realistic mock AI insights"""
        
        if analysis.risk_score > 70:
            severity = "HIGH RISK"
            impact = "immediate business impact"
        elif analysis.risk_score > 40:
            severity = "MEDIUM RISK"
            impact = "potential service degradation"
        else:
            severity = "LOW RISK"
            impact = "minimal operational impact"
        
        top_bottleneck = analysis.primary_bottlenecks[0] if analysis.primary_bottlenecks else None
        
        if not top_bottleneck:
            return "System appears healthy with no significant bottlenecks detected."
        
        insights = [
            f"**{severity} DETECTED** - System health score: {analysis.risk_score:.1f}/100",
            "",
            f"**Root Cause Analysis:**",
            f"Primary bottleneck: {top_bottleneck.name} ({top_bottleneck.type})",
            f"- {top_bottleneck.reason}",
            f"- Centrality score: {top_bottleneck.centrality:.2f} (critical path component)",
            "",
            f"**Business Impact:** {impact.capitalize()}",
            "",
            f"**Immediate Actions Required:**"
        ]
        
        if top_bottleneck.type == "database":
            insights.extend([
                "1. Scale database horizontally (add read replicas)",
                "2. Optimize slow queries and add proper indexing",
                "3. Implement connection pooling optimization"
            ])
        else:
            insights.extend([
                f"1. Scale {top_bottleneck.name} - add 2-3 instances",
                "2. Implement circuit breakers for fault tolerance", 
                "3. Add comprehensive monitoring and auto-scaling"
            ])
        
        if len(analysis.cascading_failures) > 0:
            insights.extend([
                "",
                "**Cascading Risk:** Failure could propagate through dependency chain",
                "- Consider implementing bulkhead pattern",
                "- Add timeout and retry policies"
            ])
        
        insights.extend([
            "",
            f"**Architecture Recommendations:**",
            "- Implement observability stack (metrics, logs, traces)",
            "- Consider event-driven architecture for loose coupling",
            "- Add chaos engineering practices for resilience testing"
        ])
        
        return "\n".join(insights)
    
    async def generate_recommendations(self, analysis: RootCauseAnalysis, system_data: Dict) -> List[str]:
        """Generate mock AI recommendations"""
        recommendations = []
        
        for bottleneck in analysis.primary_bottlenecks[:3]:
            if bottleneck.cpu_usage > 85:
                if bottleneck.type == "database":
                    recommendations.append(f"Scale {bottleneck.name}: Add read replicas or partition data")
                else:
                    recommendations.append(f"Scale {bottleneck.name}: Add 2-3 instances behind load balancer")
            
            if bottleneck.memory_usage > 85:
                recommendations.append(f"Optimize {bottleneck.name}: Review memory leaks and increase heap size")
            
            if bottleneck.centrality > 0.25:
                recommendations.append(f"Reduce dependency on {bottleneck.name}: Implement circuit breakers and fallbacks")
            
            if "error" in bottleneck.reason.lower():
                recommendations.append(f"Investigate {bottleneck.name}: Enable debug logs and trace error patterns")
        
        # Add general recommendations
        if analysis.risk_score > 70:
            recommendations.append("Implement auto-scaling policies for critical services")
            recommendations.append("Set up comprehensive monitoring with Prometheus/Grafana")
        
        return recommendations[:6]

# ============================================================================
# JARVIS - Your Custom AI Integration
# ============================================================================
class CustomAIProvider(AIProvider):
    """
    JARVIS - Your Custom AI Provider
    
    SETUP INSTRUCTIONS:
    1. Add your AI model configuration (API keys, endpoints, model paths)
    2. Implement the analyze_system_health() method to call your AI
    3. Implement the generate_recommendations() method
    4. Switch to JARVIS via /api/ai/switch-provider?provider=jarvis
    
    EXAMPLES:
    - Local LLM (Ollama, LlamaCpp): Make HTTP calls to local endpoints
    - Hugging Face models: Use transformers library
    - Azure OpenAI: Similar to OpenAI but with Azure endpoints
    - Custom fine-tuned models: Load your model and run inference
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.provider_name = "jarvis"
        
        # Ollama Configuration
        self.api_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        self.model_name = os.getenv("OLLAMA_MODEL", "llama2:7b")  # or "mistral:7b", "codellama:7b"
        self.timeout = 30  # Ollama response timeout
        
    async def analyze_system_health(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """
        Call your AI model to analyze system health
        
        INPUT:
        - analysis: Contains bottlenecks, cascading failures, risk score
        - system_data: Total services, critical count, service types
        
        OUTPUT:
        - String with AI-generated insights about the system health
        
        IMPLEMENTATION EXAMPLES:
        
        # Example 1: Call Ollama local LLM
        # import httpx
        # prompt = self._build_analysis_prompt(analysis, system_data)
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"{self.api_endpoint}/api/generate",
        #         json={"model": self.model_name, "prompt": prompt}
        #     )
        #     return response.json()["response"]
        
        # Example 2: Use Hugging Face transformers
        # from transformers import pipeline
        # generator = pipeline('text-generation', model='gpt2')
        # prompt = self._build_analysis_prompt(analysis, system_data)
        # result = generator(prompt, max_length=500)
        # return result[0]['generated_text']
        
        # Example 3: Call Azure OpenAI
        # from openai import AsyncAzureOpenAI
        # client = AsyncAzureOpenAI(
        #     api_key=self.api_key,
        #     api_version="2024-02-01",
        #     azure_endpoint=self.api_endpoint
        # )
        # prompt = self._build_analysis_prompt(analysis, system_data)
        # response = await client.chat.completions.create(
        #     model=self.model_name,
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return response.choices[0].message.content
        """
        
        # Call Ollama for AI-powered analysis
        try:
            import httpx
            
            # Build enhanced prompt for Ollama
            prompt = self._build_ollama_analysis_prompt(analysis, system_data)
            
            # Call Ollama API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_endpoint}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for consistent technical analysis
                            "top_p": 0.9,
                            "num_ctx": 4096  # Context window
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "").strip()
                    
                    # Format response with JARVIS prefix
                    if ai_response:
                        return f"JARVIS: {ai_response}"
                    else:
                        return "JARVIS: Analysis completed but response was empty."
                else:
                    # Fallback if Ollama is not available
                    return self._get_fallback_analysis(analysis)
                    
        except Exception as e:
            # Fallback to enhanced analysis if Ollama is not available
            print(f"JARVIS Ollama error: {e}")
            return self._get_fallback_analysis(analysis)
            
        except Exception as e:
            return f"JARVIS error: {str(e)}"
    
    async def generate_recommendations(self, analysis: RootCauseAnalysis, system_data: Dict) -> List[str]:
        """
        Generate recommendations using your AI model
        
        INPUT:
        - analysis: Contains bottlenecks with CPU, memory, risk scores
        - system_data: System overview information
        
        OUTPUT:
        - List of actionable recommendation strings
        """
        
        # Call Ollama for AI-powered recommendations
        try:
            import httpx
            
            # Build recommendations prompt for Ollama
            prompt = self._build_ollama_recommendations_prompt(analysis, system_data)
            
            # Call Ollama API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_endpoint}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.2,  # Slightly higher for creative recommendations
                            "top_p": 0.9,
                            "num_ctx": 4096
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "").strip()
                    
                    # Parse recommendations from AI response
                    if ai_response:
                        recommendations = self._parse_recommendations(ai_response)
                        return recommendations[:6]  # Limit to 6 recommendations
                    
            # Fallback recommendations if Ollama is not available
            return self._get_fallback_recommendations(analysis)
                    
        except Exception as e:
            print(f"JARVIS Ollama recommendations error: {e}")
            return self._get_fallback_recommendations(analysis)
            
        except Exception as e:
            return []
    
    def _build_ollama_analysis_prompt(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """Build enhanced prompt for Ollama analysis"""
        risk_level = "CRITICAL" if analysis.risk_score > 80 else "HIGH" if analysis.risk_score > 60 else "MEDIUM" if analysis.risk_score > 30 else "LOW"
        
        bottlenecks_detail = ""
        for b in analysis.primary_bottlenecks[:3]:
            bottlenecks_detail += f"\n- {b.name} ({b.type}): CPU {b.cpu_usage:.1f}%, Memory {b.memory_usage:.1f}%, Risk {b.risk_score:.1f}/100\n  Issue: {b.reason}"
        
        cascades = f"\nDownstream services at risk: {', '.join(analysis.cascading_failures)}" if analysis.cascading_failures else ""
        
        return f"""You are JARVIS, an expert DevOps AI assistant analyzing a microservices system.

🚨 SYSTEM HEALTH ALERT - {risk_level} PRIORITY 🚨

SYSTEM OVERVIEW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Risk Score: {analysis.risk_score:.1f}/100
Total Services: {system_data.get('total_services', 0)}
Critical Services: {system_data.get('critical_count', 0)}
Service Types: {', '.join(system_data.get('service_types', []))}

PERFORMANCE BOTTLENECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{bottlenecks_detail}{cascades}

As JARVIS, provide a concise technical analysis in 2-3 sentences focusing on:
1. Root cause identification
2. Business impact assessment 
3. Immediate action priority

Keep response under 150 words, technical but clear."""
        
    def _build_ollama_recommendations_prompt(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """Build enhanced prompt for Ollama recommendations"""
        bottlenecks_summary = "\n".join([
            f"- {b.name} ({b.type}): CPU {b.cpu_usage:.1f}%, Memory {b.memory_usage:.1f}%, Risk {b.risk_score:.1f}"
            for b in analysis.primary_bottlenecks[:3]
        ])
        
        return f"""You are JARVIS, providing specific DevOps recommendations.

SYSTEM ISSUES:
{bottlenecks_summary}

Risk Level: {analysis.risk_score:.1f}/100
Cascading Failures: {len(analysis.cascading_failures)}

Provide exactly 6 specific, actionable recommendations. Format each as:
"JARVIS: [Action] - [specific details]"

Focus on:
- Immediate scaling actions
- Performance optimizations 
- Monitoring improvements
- Architecture fixes
- Disaster recovery
- Preventive measures

Each recommendation should be 1 line, specific and executable."""
    
    def _get_fallback_analysis(self, analysis: RootCauseAnalysis) -> str:
        """Fallback analysis when Ollama is unavailable"""
        risk_level = "CRITICAL" if analysis.risk_score > 80 else "HIGH" if analysis.risk_score > 60 else "MODERATE"
        top_issue = analysis.primary_bottlenecks[0] if analysis.primary_bottlenecks else None
        
        if not top_issue:
            return "JARVIS: System performance is within acceptable parameters. No immediate action required."
        
        if top_issue.type == "database" and top_issue.cpu_usage > 90:
            analysis_text = f"JARVIS: {risk_level} database bottleneck detected. {top_issue.name} experiencing severe CPU overload at {top_issue.cpu_usage:.0f}%. Query inefficiency or connection pool exhaustion likely. Immediate scaling recommended."
        elif top_issue.type == "api" and top_issue.memory_usage > 85:
            analysis_text = f"JARVIS: {risk_level} memory pressure in {top_issue.name} at {top_issue.memory_usage:.0f}%. Memory leaks or inefficient resource management detected. GC pressure and response time degradation imminent."
        else:
            analysis_text = f"JARVIS: {risk_level} performance issue in {top_issue.name}. {len(analysis.primary_bottlenecks)} bottleneck(s) detected, risk score {analysis.risk_score:.1f}/100. DevOps intervention required."
        
        if len(analysis.cascading_failures) > 0:
            analysis_text += f" CASCADE ALERT: {len(analysis.cascading_failures)} downstream services at failure risk."
            
        return analysis_text
    
    def _get_fallback_recommendations(self, analysis: RootCauseAnalysis) -> List[str]:
        """Fallback recommendations when Ollama is unavailable"""
        recommendations = []
        
        for bottleneck in analysis.primary_bottlenecks[:3]:
            if bottleneck.cpu_usage > 90:
                if bottleneck.type == "database":
                    recommendations.append(f"JARVIS: Scale {bottleneck.name} horizontally - add 2-3 read replicas immediately")
                    recommendations.append(f"JARVIS: Enable slow query logging on {bottleneck.name} to identify performance killers")
                else:
                    recommendations.append(f"JARVIS: Deploy additional {bottleneck.name} instances with load balancing")
            
            if bottleneck.memory_usage > 85:
                recommendations.append(f"JARVIS: Investigate {bottleneck.name} memory usage - potential leak at {bottleneck.memory_usage:.0f}%")
        
        if analysis.risk_score > 80:
            recommendations.append("JARVIS: Activate disaster recovery procedures - system in critical state")
        elif analysis.risk_score > 60:
            recommendations.append("JARVIS: Implement auto-scaling policies to handle current load surge")
            
        recommendations.append("JARVIS: Deploy comprehensive monitoring with real-time alerts")
        
        return recommendations[:6]
    
    def _parse_recommendations(self, ai_response: str) -> List[str]:
        """Parse recommendations from Ollama response"""
        lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
        recommendations = []
        
        for line in lines:
            # Look for JARVIS-formatted recommendations
            if line.startswith('JARVIS:') or any(action in line.lower() for action in ['scale', 'implement', 'deploy', 'optimize', 'review', 'add']):
                if not line.startswith('JARVIS:'):
                    line = f"JARVIS: {line}"
                recommendations.append(line)
                
        # If no recommendations found, create basic ones
        if not recommendations:
            recommendations = [
                "JARVIS: Scale critical services horizontally for load distribution",
                "JARVIS: Implement comprehensive monitoring and alerting system", 
                "JARVIS: Optimize database queries and add proper indexing",
                "JARVIS: Deploy auto-scaling policies for peak load handling",
                "JARVIS: Review service dependencies and add circuit breakers",
                "JARVIS: Establish disaster recovery procedures and runbooks"
            ]
            
        return recommendations

# AI Manager
class AIManager:
    def __init__(self, provider: str = "mock"):
        self.providers = {
            "openai": OpenAIProvider,
            "gemini": GeminiProvider, 
            "claude": ClaudeProvider,
            "mock": MockAIProvider,
            "jarvis": CustomAIProvider  # JARVIS - Your custom AI
        }
        
        if provider not in self.providers:
            provider = "mock"
            
        self.current_provider = self.providers[provider]()
    
    async def get_ai_insights(self, analysis: RootCauseAnalysis, system_data: Dict) -> str:
        """Get AI insights using configured provider"""
        try:
            return await self.current_provider.analyze_system_health(analysis, system_data)
        except Exception as e:
            # Fallback to basic insights if AI fails
            bottlenecks = ", ".join([b['name'] for b in analysis.primary_bottlenecks[:3]])
            return f"Analysis complete. Detected {len(analysis.primary_bottlenecks)} bottleneck(s): {bottlenecks}. Risk score: {analysis.risk_score:.1f}/100. {len(analysis.cascading_failures)} services at risk."
    
    
    async def get_ai_recommendations(self, analysis: RootCauseAnalysis, system_data: Dict) -> List[str]:
        """Get AI-powered recommendations"""
        try:
            return await self.current_provider.generate_recommendations(analysis, system_data)
        except:
            return []  # Fallback to empty list if AI fails
    
    def switch_provider(self, provider: str):
        """Switch AI provider"""
        if provider in self.providers:
            self.current_provider = self.providers[provider]()
            return True
        return False
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        return list(self.providers.keys())

# Global AI manager instance
ai_manager = AIManager()