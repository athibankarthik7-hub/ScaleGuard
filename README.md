# ScaleGuard

ScaleGuard is a predictive scaling and root-cause intelligence engine that helps engineering teams understand how systems behave under growth before they fail.

## 🌌 Vision
ScaleGuard treats software architectures like living systems — modeling load, stress, and failure propagation visually and interactively.

## 🚀 Features
- **Predictive Scaling Intelligence**: Simulate traffic growth and predict bottlenecks.
- **Visual Architecture**: Interactive 2D/3D graph of system dependencies.
- **Root Cause Analysis**: Correlate logs and rank likely root causes.
- **Real-time Dashboard**: Monitor system health and risk scores.

## 🛠 Tech Stack
- **Frontend**: React, TypeScript, TailwindCSS, Three.js, React Flow, Recharts
- **Backend**: FastAPI, NetworkX, Python
- **Simulation**: Probabilistic modeling of system load

## 📦 Installation & Run

### Prerequisites
- Node.js (v18+)
- Python (v3.9+)

### Backend Setup
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install fastapi uvicorn networkx pydantic
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🧪 Usage
1. Open the frontend URL (usually `http://localhost:5173`).
2. Click "Launch Demo" on the landing page.
3. Explore the **System Dashboard**.
4. Go to **Architecture Explorer** to see the dependency graph (switch between 2D/3D).
5. Navigate to **Simulation**, set a growth factor, and run a simulation to see predicted failures.

## 🎨 Design Stats
- **Theme**: Dark / Space / Neon
- **Font**: Inter
- **Icons**: Lucide React
