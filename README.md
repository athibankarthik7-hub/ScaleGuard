# ScaleGuard 🛡️

**AI-Powered Predictive Infrastructure Monitoring & Auto-Remediation Platform**

ScaleGuard is an intelligent system that predicts infrastructure failures before they happen and automatically fixes common issues. Powered by JARVIS AI (Ollama qwen3:4b), it provides real-time monitoring, historical tracking, failure predictions, and autonomous remediation.

---

## 🌟 Key Features

### 🤖 **JARVIS AI Integration**
- Multi-provider AI support (OpenAI GPT-4, Google Gemini, Anthropic Claude, Custom JARVIS)
- Local LLM integration via Ollama (qwen3:4b model)
- Intelligent root cause analysis and recommendations
- Real-time system insights

### 📊 **Historical Tracking**
- Track 5 key metrics over 48 hours (risk_score, CPU, memory, error_rate, latency)
- Trend analysis with direction indicators (increasing/decreasing/stable/volatile)
- Interactive time-series charts
- Metric snapshots with configurable windows (15m/30m/60m)

### 🔮 **Predictive Analytics**
- AI-powered failure prediction before they occur
- Failure probability percentages with time-to-failure estimates
- Contributing factors analysis
- Preventive action recommendations
- Cascade failure detection

### 🔧 **Auto-Remediation**
- 5 built-in remediation rules:
  - CPU auto-scaling (>85% usage)
  - Memory leak restart (>95% usage)
  - Circuit breaker activation (>15% error rate)
  - Rate limiting on overload
  - Cache clearing (>1000ms latency)
- Auto-approval and manual approval modes
- Dry-run mode for testing
- Action history and statistics
- Cooldown periods to prevent rapid re-execution

### 📈 **Real-Time Monitoring**
- Live system health dashboard
- Bottleneck detection and analysis
- Risk score calculation
- Interactive architecture visualization
- Service dependency mapping

---

## 📁 Project Structure

```
ScaleGuard/
├── backend/               # Python FastAPI backend
│   ├── main.py           # Main API server
│   ├── ai_integration.py # Multi-provider AI hub
│   ├── historical_tracker.py    # Metric tracking
│   ├── predictive_analytics.py  # Failure prediction
│   ├── auto_remediation.py      # Auto-fix system
│   ├── graph.py          # Network analysis
│   ├── simulation.py     # Load simulation
│   ├── models.py         # Data models
│   ├── mock_data.py      # Test data generation
│   ├── requirements.txt  # Python dependencies
│   ├── .env.example      # Environment template
│   └── training/         # AI training scripts
│       ├── data/         # Training datasets (50/500/2000 examples)
│       ├── training_data_generator.py
│       ├── training_data_validator.py
│       └── train_*.py    # Training scripts
├── frontend/             # React + TypeScript frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   │   ├── PredictionsPanel.tsx
│   │   │   ├── HistoricalTrends.tsx
│   │   │   ├── RemediationPanel.tsx
│   │   │   ├── MainLayout.tsx
│   │   │   └── AIProviderSwitcher.tsx
│   │   ├── pages/        # Page components
│   │   │   ├── DashboardPage.tsx  # Main dashboard with tabs
│   │   │   ├── ArchitecturePage.tsx
│   │   │   ├── Simulation.tsx
│   │   │   ├── IncidentDebugger.tsx
│   │   │   └── LandingPage.tsx
│   │   └── utils/
│   │       └── api.ts    # API client (25+ endpoints)
│   ├── package.json
│   └── vite.config.ts
├── docs/                 # Documentation
│   ├── ADVANCED_FEATURES_API.md    # API reference
│   ├── FRONTEND_UPDATES.md         # UI/UX guide
│   ├── CUSTOM_AI_GUIDE.md          # JARVIS setup
│   ├── TRAINING_DATA_SPECS.md      # Training data format
│   └── OLLAMA_EXAMPLE.md           # Ollama integration
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+**
- **Node.js 18+**
- **Ollama** (optional, for local JARVIS AI)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (optional for cloud AI providers)

# Start server
python -m uvicorn main:app --reload --port 8000
```

**Backend will be available at:** `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend will be available at:** `http://localhost:5173` (or next available port)

### 3. Ollama Setup (Optional - for JARVIS AI)

```bash
# Install Ollama from https://ollama.ai

# Pull qwen3:4b model
ollama pull qwen3:4b

# Verify it's running
ollama list
```

Add to `backend/.env`:
```env
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

---

## 🎯 Usage Guide

### Dashboard Navigation

The main dashboard has **4 tabs**:

#### 1. 🔵 Overview Tab
- **Risk Score** - System-wide scaling risk (0-100)
- **Active Services** - Total monitored nodes
- **Traffic Stats** - Request rate and trends
- **Bottleneck List** - Top 5 critical services

#### 2. 🟣 Historical Trends Tab
- **Time Windows** - View 15min/30min/60min history
- **5 Metric Cards** - Current values with trend indicators
- **Multi-Line Chart** - Visualize all metrics over time
- **Change Rates** - Per-minute rate of change

#### 3. 🔴 AI Predictions Tab
- **At-Risk Services** - Services predicted to fail
- **Failure Probability** - Percentage likelihood (0-100%)
- **Time to Failure** - Estimated minutes/hours until failure
- **Contributing Factors** - What's causing the issue
- **Preventive Actions** - AI-recommended fixes

#### 4. 🟢 Auto-Remediation Tab
- **System Controls** - ON/OFF switch, dry-run mode
- **Statistics** - Total actions, success rate
- **Rules Management** - Enable/disable individual rules
- **Action History** - Last 24 hours of executed fixes

### API Endpoints

**Core System:**
- `GET /api/system` - Get system state
- `GET /api/risk-score` - Calculate risk score
- `GET /api/analysis` - Full AI analysis
- `GET /api/bottlenecks` - Bottleneck detection
- `POST /api/reset` - Reset system

**Historical Tracking:**
- `GET /api/historical/trends` - Metric trends
- `GET /api/historical/snapshots` - Raw snapshots
- `GET /api/historical/statistics` - Storage stats

**Predictions:**
- `GET /api/predictions/all` - All predictions
- `GET /api/predictions/failures` - Failure forecasts
- `GET /api/predictions/cascades` - Cascade predictions

**Auto-Remediation:**
- `GET /api/remediation/rules` - View rules
- `GET /api/remediation/actions` - Action history
- `GET /api/remediation/statistics` - System stats
- `POST /api/remediation/execute/{id}` - Approve action
- `POST /api/remediation/toggle` - Enable/disable system
- `POST /api/remediation/dry-run` - Toggle simulation mode

**AI Provider:**
- `GET /api/ai/providers` - List available providers
- `POST /api/ai/switch-provider` - Change AI provider

Full API documentation: [docs/ADVANCED_FEATURES_API.md](docs/ADVANCED_FEATURES_API.md)

---

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **NetworkX** - Graph analysis and centrality calculations
- **Pydantic** - Data validation
- **httpx** - Async HTTP client (Ollama integration)
- **python-dotenv** - Environment management
- **OpenAI SDK** - GPT-4 integration
- **Google Generative AI** - Gemini integration
- **Anthropic SDK** - Claude integration

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS
- **Recharts** - Data visualization
- **Lucide React** - Icon library
- **React Router** - Client-side routing

### AI/ML
- **Ollama** - Local LLM runtime
- **qwen3:4b** - Lightweight language model (JARVIS)
- **OpenAI GPT-4** - Cloud AI option
- **Google Gemini** - Cloud AI option
- **Anthropic Claude** - Cloud AI option

---

## 📊 Training AI Models

ScaleGuard includes comprehensive training data generation:

```bash
cd backend/training

# Generate training data (50/500/2000 examples)
python training_data_generator.py

# Validate data quality
python training_data_validator.py

# Format for different platforms
python training_usage_example.py

# Train models
python train_openai.py       # OpenAI fine-tuning
python train_huggingface.py  # Hugging Face training
```

See [backend/training/README.md](backend/training/README.md) for details.

---

## 🎨 Design System

### Color Palette
- **Primary Blue** - `#3b82f6` - Overview/Actions
- **Purple** - `#8b5cf6` - Historical data
- **Red** - `#ef4444` - Alerts/Predictions
- **Green** - `#10b981` - Success/Remediation
- **Orange** - `#f59e0b` - Warnings

### UI Components
- **Glassmorphism** - Semi-transparent panels with blur
- **Smooth Animations** - Hover effects and transitions
- **Responsive Grid** - Mobile-first design
- **Dark Theme** - Space-inspired aesthetic
- **Modern Typography** - Clean hierarchy

---

## 🧪 Testing

### Backend Testing
```bash
cd backend

# Test API health
curl http://localhost:8000/health

# Test historical trends
curl http://localhost:8000/api/historical/trends

# Test predictions
curl http://localhost:8000/api/predictions/all

# Test remediation stats
curl http://localhost:8000/api/remediation/statistics
```

### Frontend Testing
1. Open `http://localhost:5173` in browser
2. Navigate through all 4 dashboard tabs
3. Switch AI providers in sidebar
4. Toggle remediation settings
5. Monitor real-time updates

---

## 📚 Documentation

- **[Advanced Features API](docs/ADVANCED_FEATURES_API.md)** - Complete API reference
- **[Frontend Updates](docs/FRONTEND_UPDATES.md)** - UI/UX guide
- **[Custom AI Guide](docs/CUSTOM_AI_GUIDE.md)** - JARVIS setup instructions
- **[Training Data Specs](docs/TRAINING_DATA_SPECS.md)** - Training data format
- **[Ollama Examples](docs/OLLAMA_EXAMPLE.md)** - Local LLM integration

---

## 🔒 Environment Variables

Create `backend/.env` from `.env.example`:

```env
# OpenAI (optional)
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini

# Google Gemini (optional)
GOOGLE_AI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.0-flash-lite

# Anthropic Claude (optional)
ANTHROPIC_API_KEY=your_claude_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Ollama (local AI - recommended)
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

---

## 🚦 System Status

Current implementation status:

| Feature | Status | Details |
|---------|--------|---------|
| Backend API | ✅ Complete | 25+ endpoints operational |
| Historical Tracking | ✅ Complete | 48hr storage, 5 metrics |
| Predictive Analytics | ✅ Complete | AI-powered forecasting |
| Auto-Remediation | ✅ Complete | 5 rules, auto-execution |
| Frontend Dashboard | ✅ Complete | 4 tabs, responsive design |
| JARVIS AI | ✅ Complete | Ollama integration |
| Multi-AI Support | ✅ Complete | 5 providers available |
| Training System | ✅ Complete | 2000 examples generated |
| Documentation | ✅ Complete | Comprehensive guides |

---

## 🎯 Performance Metrics

### Backend
- **API Response Time:** 50-200ms
- **Historical Storage:** Up to 2880 snapshots (48 hours)
- **Prediction Accuracy:** Real-time analysis
- **Auto-Remediation:** <1s action execution

### Frontend
- **Initial Load:** ~500ms
- **Component Render:** <100ms
- **Chart Rendering:** <150ms
- **Bundle Size:** ~800KB (gzipped)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime
- **Alibaba Cloud** - qwen3:4b model
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **Recharts** - Data visualization

---

## 📧 Contact

For questions, issues, or feedback:
- Open an issue on GitHub
- Check documentation in `docs/` folder

---

**Built with ❤️ for production-grade infrastructure monitoring**
