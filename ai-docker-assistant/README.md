# 🐳 AI Docker Assistant

AI-powered Docker container recommendations and intelligent log debugging.

> **Resume headline:** Built an AI-powered Docker assistant using FastAPI, Scikit-learn, and React that recommends optimal container configurations and performs ML-based log root cause analysis.

---

## Features

| Feature | Description |
|---------|-------------|
| 📦 **Image Recommender** | Input project type + expected users → get base image, Dockerfile, `docker run` command, and scaled runtime params |
| 🔍 **Log Debugger** | Paste raw Docker logs → get root cause, severity, fix suggestion, ready-to-run commands, and prevention tip |
| 🤖 **ML Models** | Phase 2: RandomForest recommender · Phase 3: TF-IDF + LogisticRegression log classifier |
| ⚡ **12 project types** | fastapi, django, flask, node, react, nextjs, ml, postgres, redis, nginx, go, rust |
| 🔎 **11 error patterns** | OOM, port conflict, permission denied, connection refused, image not found, disk full, missing env var, health check, crash, SSL, timeout |

---

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, Uvicorn
- **ML:** Scikit-learn (RandomForestClassifier, TF-IDF + LogisticRegression)
- **Frontend:** React 18, Vite, CSS variables (dark theme)
- **Infrastructure:** Docker, Docker Compose

---

## Project Structure

```
ai-docker-assistant/
│
├── app/
│   ├── main.py                  # FastAPI app + CORS + health endpoint
│   ├── schemas.py               # All Pydantic request/response models
│   ├── routers/
│   │   ├── recommend.py         # POST /api/recommend
│   │   └── debug.py             # POST /api/debug
│   └── engine/
│       ├── recommender.py       # Rule-based + ML recommendation engine
│       └── debugger.py          # Pattern matching + ML log analyser
│
├── ml/
│   ├── train_recommender.py     # Phase 2: Train RandomForest model
│   └── train_debugger.py        # Phase 3: Train TF-IDF classifier
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Root component + tab navigation
│   │   ├── api.js               # API service module
│   │   ├── components/          # Reusable UI components
│   │   └── pages/
│   │       ├── RecommendPage.jsx
│   │       └── DebugPage.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── tests/
│   └── test_engines.py          # 30+ pytest tests
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Quickstart

### Option A — Docker (recommended)

```bash
git clone https://github.com/yourname/ai-docker-assistant
cd ai-docker-assistant

cp .env.example .env
docker-compose up --build
```

API → http://localhost:8000  
Docs → http://localhost:8000/docs

### Option B — Local dev

```bash
# Backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Frontend → http://localhost:5173

---

## API Reference

### POST /api/recommend

```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "project_type": "fastapi",
    "expected_users": 10000,
    "has_gpu": false
  }'
```

**Response:**
```json
{
  "base_image": "python:3.12-slim",
  "dockerfile_snippet": "FROM python:3.12-slim\n...",
  "docker_run_command": "docker run -d \\\n  --name my-fastapi \\\n  --memory 512m ...",
  "runtime_params": {
    "memory": "512m",
    "cpus": "1",
    "restart_policy": "unless-stopped",
    "env_vars": ["PORT=8000", "ENV=production"],
    "extra_flags": []
  },
  "reasoning": "Project 'fastapi' with 10,000 expected users...",
  "confidence": 0.85,
  "alternatives": ["tiangolo/uvicorn-gunicorn-fastapi:python3.12-slim"]
}
```

### POST /api/debug

```bash
curl -X POST http://localhost:8000/api/debug \
  -H "Content-Type: application/json" \
  -d '{
    "log_text": "OOMKilled: container exceeded memory limit of 512Mi",
    "container_name": "my-api"
  }'
```

**Response:**
```json
{
  "root_cause": "Out of Memory (OOM)",
  "confidence": 0.79,
  "severity": "critical",
  "fix_suggestion": "Your container was killed because it exceeded its memory limit...",
  "commands": [
    "docker stats my-api",
    "docker update --memory 1g --memory-swap 2g my-api"
  ],
  "explanation": "The Linux OOM killer terminates the container's main process...",
  "prevention_tip": "Profile memory with 'docker stats' before setting limits."
}
```

---

## Activating ML Models (Phase 2 & 3)

### Phase 2 — Recommendation model

```bash
python ml/train_recommender.py
# → saves ml/recommender_model.pkl

# Activate in docker-compose.yml:
USE_ML_MODEL=true
```

### Phase 3 — Log classifier

```bash
python ml/train_debugger.py
# → saves ml/debugger_model.pkl

# Activate in docker-compose.yml:
USE_ML_CLASSIFIER=true
```

---

## Running Tests

```bash
pytest tests/ -v
```

30+ tests covering:
- Image selection for all project types and load tiers
- Runtime parameter scaling
- Dockerfile content validation (multi-stage builds for Go/Rust)
- All 11 error pattern detections
- Confidence scoring
- Container name substitution in commands
- Fallback behaviour for unknown inputs

---

## Deployment

### Railway / Render (free tier)

```bash
# Set start command to:
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Build frontend for production

```bash
cd frontend
npm run build
# → dist/ folder — serve with nginx or any static host
```

---

## Roadmap

- [x] Phase 1 — FastAPI skeleton, Pydantic schemas, rule-based engines
- [x] Phase 2 — Scikit-learn RandomForest recommendation model
- [x] Phase 3 — TF-IDF + LogisticRegression log classifier
- [x] Phase 4 — React frontend with both features
- [ ] Phase 5 — Deploy to Railway/Render with CI/CD
- [ ] Phase 6 — Real Docker API integration (pull actual image sizes, layer counts)
- [ ] Phase 7 — User feedback loop to retrain models
