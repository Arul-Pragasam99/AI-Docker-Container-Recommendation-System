# AI Docker Assistant

AI-powered Docker container recommendation system and intelligent log debugging assistant.

Built with FastAPI, Scikit-learn, React, and Docker.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Installation & Setup](#installation--setup)
7. [Running the App](#running-the-app)
8. [Using the App](#using-the-app)
9. [API Reference](#api-reference)
10. [Activating ML Models](#activating-ml-models)
11. [Running Tests](#running-tests)
12. [Frontend Development](#frontend-development)
13. [Deployment](#deployment)
14. [Troubleshooting](#troubleshooting)
15. [Roadmap](#roadmap)

---

## Project Overview

AI Docker Assistant solves two problems developers face daily:

**Problem 1 — Which Docker image should I use?**  
Developers waste time researching base images, memory limits, and runtime flags for every new project. This tool takes your project type and expected load and returns the optimal image, a ready-to-use Dockerfile, and a `docker run` command with scaled parameters.

**Problem 2 — Why is my container broken?**  
Reading Docker logs is tedious. This tool accepts raw log output and instantly identifies the root cause, severity, fix steps, and ready-to-run commands — powered by pattern matching and an optional ML classifier.

---

## Features

| Feature | Description |
|---------|-------------|
| Image Recommender | Input project type + expected users, get base image, Dockerfile, docker run command, and runtime params |
| Log Debugger | Paste Docker logs, get root cause, severity, fix suggestion, commands, and prevention tip |
| ML Models | Phase 2: RandomForest recommender — Phase 3: TF-IDF + LogisticRegression log classifier |
| 12 project types | fastapi, django, flask, node, react, nextjs, ml, postgres, redis, nginx, go, rust |
| 11 error patterns | OOM, port conflict, permission denied, connection refused, image not found, disk full, missing env var, health check, crash, SSL, timeout |
| Load tiers | tiny (<500), small (1-5k), medium (5-25k), large (25-100k), xlarge (100k+) |
| Multi-stage builds | Go and Rust projects get optimised multi-stage Dockerfiles automatically |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, Pydantic v2, Uvicorn |
| ML | Scikit-learn — RandomForestClassifier, TF-IDF, LogisticRegression |
| Frontend | React 18, Vite, IBM Plex fonts |
| Infrastructure | Docker, Docker Compose |
| Testing | Pytest (30+ tests) |

---

## Project Structure

```
ai-docker-assistant/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point, CORS, health check
│   ├── schemas.py               # All Pydantic request and response models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── recommend.py         # POST /api/recommend
│   │   └── debug.py             # POST /api/debug
│   └── engine/
│       ├── __init__.py
│       ├── recommender.py       # Rule-based engine (Phase 1) + ML model (Phase 2)
│       └── debugger.py          # Pattern matching (Phase 1/2) + ML classifier (Phase 3)
│
├── ml/
│   ├── train_recommender.py     # Train and save RandomForest recommendation model
│   └── train_debugger.py        # Train and save TF-IDF log classifier
│
├── frontend/
│   ├── index.html               # HTML entry point, Google Fonts
│   ├── package.json             # Node dependencies
│   ├── vite.config.js           # Vite config with API proxy
│   └── src/
│       ├── main.jsx             # React root mount
│       ├── App.jsx              # Root component + tab navigation
│       ├── App.css              # Header, tabs, layout
│       ├── index.css            # Design tokens (CSS variables), body reset
│       ├── api.js               # Fetch wrapper for all API calls
│       ├── components/
│       │   ├── index.jsx        # Button, Card, CodeBlock, Badge, Toggle, etc.
│       │   └── components.css   # All component styles
│       └── pages/
│           ├── RecommendPage.jsx
│           ├── RecommendPage.css
│           ├── DebugPage.jsx
│           └── DebugPage.css
│
├── tests/
│   ├── __init__.py
│   └── test_engines.py          # 30+ unit tests for both engines
│
├── Dockerfile                   # Production container for the API
├── docker-compose.yml           # Full stack orchestration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
└── README.md
```

---

## Prerequisites

Make sure the following are installed before you start:

**Docker Desktop**
- Download from https://www.docker.com/products/docker-desktop
- Install and launch it
- Wait for the whale icon in the system tray to stop animating
- Verify it is running: `docker info`

**Node.js** (only needed if running the frontend locally outside Docker)
- Download from https://nodejs.org — use the LTS version
- Verify: `node --version` and `npm --version`

**Python 3.12** (only needed for local backend development or ML training)
- Download from https://python.org
- Verify: `python --version`

**Git**
- Download from https://git-scm.com

---

## Installation & Setup

### Step 1 — Clone the repository

```bash
git clone https://github.com/yourname/ai-docker-assistant.git
cd ai-docker-assistant
```

Or if you downloaded the zip file:

```bash
# Extract the zip, then open a terminal in the folder
cd ai-docker-assistant
```

### Step 2 — Copy the environment file

```bash
cp .env.example .env
```

The default values in `.env` work out of the box for local development. No changes needed to get started.

### Step 3 — Choose your setup method

There are two ways to run this project. Pick one:

- **Option A — Docker** (recommended, no Python or Node install required)
- **Option B — Local** (faster for active development)

---

## Running the App

### Option A — Docker (Recommended)

This runs the entire backend in a container. No Python setup needed.

**Step 1 — Make sure Docker Desktop is open and running**

```bash
docker info
# Should print system info. If it errors, open Docker Desktop first.
```

**Step 2 — Build and start**

```bash
docker-compose up --build
```

The first build takes 2-3 minutes to download the base image and install dependencies. Subsequent starts are instant.

**Step 3 — Verify it is running**

```
API:  http://localhost:8000
Docs: http://localhost:8000/docs
```

**Step 4 — Start the frontend** (separate terminal)

```bash
cd frontend
npm install
npm run dev
```

```
Frontend: http://localhost:5173
```

**To stop everything:**

```bash
docker-compose down
```

---

### Option B — Local Development

**Backend:**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API
uvicorn app.main:app --reload --port 8000
```

**Frontend** (separate terminal):

```bash
cd frontend
npm install
npm run dev
```

```
API:      http://localhost:8000
Docs:     http://localhost:8000/docs
Frontend: http://localhost:5173
```

---

## Using the App

### Image Recommender

1. Open http://localhost:5173
2. The app opens on the **recommend** tab
3. Select your **project type** from the dropdown (e.g. fastapi, node, ml)
4. Enter your **expected concurrent users** or click a preset button
5. Toggle **GPU workload** on if your project needs CUDA (ML projects)
6. Click **Get Recommendation**
7. The result shows:
   - Recommended base image
   - Memory and CPU limits
   - Confidence score
   - Runtime parameters and env vars
   - Ready-to-copy `docker run` command
   - Complete Dockerfile
   - Reasoning and alternative images

### Log Debugger

1. Click the **debug** tab
2. Optionally enter your **container name** (used in the suggested commands)
3. Paste your **Docker log output** into the textarea
4. Or click one of the **example buttons** to load a sample log
5. Click **Analyse Logs**
6. The result shows:
   - Root cause label
   - Severity rating (low / medium / high / critical)
   - Confidence score
   - Fix suggestion
   - Why this error happens
   - Ready-to-run commands with your container name substituted in
   - Prevention tip

---

## API Reference

The API runs at `http://localhost:8000`. Interactive docs are at `/docs`.

### GET /health

```bash
curl http://localhost:8000/health
```

```json
{ "status": "ok", "version": "1.0.0" }
```

---

### POST /api/recommend

**Request:**

```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "project_type": "fastapi",
    "expected_users": 10000,
    "has_gpu": false
  }'
```

**Request fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project_type | string | yes | One of: fastapi, django, flask, node, react, nextjs, ml, postgres, redis, nginx, go, rust |
| expected_users | integer | yes | Expected concurrent users (minimum 1) |
| has_gpu | boolean | no | Set true for ML/CUDA workloads (default: false) |
| language | string | no | Auto-detected from project_type if omitted |

**Response:**

```json
{
  "base_image": "python:3.12-slim",
  "dockerfile_snippet": "FROM python:3.12-slim\n\nWORKDIR /app\n...",
  "docker_run_command": "docker run -d \\\n  --name my-fastapi \\\n  --memory 512m \\\n  --cpus 1 \\\n  --restart unless-stopped \\\n  -p 8000:8000 \\\n  -e PORT=8000 \\\n  -e ENV=production \\\n  python:3.12-slim",
  "runtime_params": {
    "memory": "512m",
    "cpus": "1",
    "restart_policy": "unless-stopped",
    "env_vars": ["PORT=8000", "ENV=production"],
    "extra_flags": []
  },
  "reasoning": "Project 'fastapi' with 10,000 expected users falls in the 'medium' load tier...",
  "confidence": 0.85,
  "alternatives": ["tiangolo/uvicorn-gunicorn-fastapi:python3.12-slim"]
}
```

---

### POST /api/debug

**Request:**

```bash
curl -X POST http://localhost:8000/api/debug \
  -H "Content-Type: application/json" \
  -d '{
    "log_text": "OOMKilled: container exceeded memory limit of 512Mi",
    "container_name": "my-api"
  }'
```

**Request fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| log_text | string | yes | Raw Docker log output (minimum 10 characters) |
| container_name | string | no | Used to personalise the suggested commands |
| image_name | string | no | Optional image name for context |

**Response:**

```json
{
  "root_cause": "Out of Memory (OOM)",
  "confidence": 0.79,
  "severity": "critical",
  "fix_suggestion": "Your container was killed because it exceeded its memory limit. Increase --memory or optimise your app's memory usage.",
  "commands": [
    "docker stats my-api",
    "docker update --memory 1g --memory-swap 2g my-api",
    "docker inspect my-api | grep -i memory"
  ],
  "explanation": "The Linux OOM killer terminates the container's main process when available memory falls below the threshold set by --memory...",
  "prevention_tip": "Profile memory with 'docker stats' before setting limits. Add HEALTHCHECK and use restart policies to auto-recover."
}
```

**Severity levels:**

| Level | Meaning |
|-------|---------|
| low | Minor issue, app likely still running |
| medium | Degraded functionality, needs attention |
| high | App failing, fix required soon |
| critical | App down, fix immediately |

---

## Activating ML Models

The app ships with rule-based engines active by default. You can upgrade to ML-powered engines by training the models locally.

### Phase 2 — Recommendation Model (RandomForest)

```bash
# Make sure you are in the project root with venv activated
python ml/train_recommender.py
```

This trains a RandomForest classifier on project type, user count, and GPU flag, then saves it to `ml/recommender_model.pkl` and prints a classification report.

To activate in Docker, open `docker-compose.yml` and change:

```yaml
- USE_ML_MODEL=false
```
to:
```yaml
- USE_ML_MODEL=true
```

Then restart:

```bash
docker-compose down && docker-compose up --build
```

To activate locally, set the environment variable before starting:

```bash
# Windows
set USE_ML_MODEL=true

# Mac/Linux
export USE_ML_MODEL=true

uvicorn app.main:app --reload
```

---

### Phase 3 — Log Classifier (TF-IDF + LogisticRegression)

```bash
python ml/train_debugger.py
```

This trains a TF-IDF vectoriser + LogisticRegression pipeline on labelled Docker log snippets, saves it to `ml/debugger_model.pkl`, and prints accuracy metrics.

To activate in Docker, open `docker-compose.yml` and change:

```yaml
- USE_ML_CLASSIFIER=false
```
to:
```yaml
- USE_ML_CLASSIFIER=true
```

Then restart:

```bash
docker-compose down && docker-compose up --build
```

---

## Running Tests

Make sure your virtual environment is active and dependencies are installed.

```bash
pytest tests/ -v
```

**Sample output:**

```
tests/test_engines.py::TestRecommender::test_fastapi_small_load_uses_slim PASSED
tests/test_engines.py::TestRecommender::test_fastapi_huge_load_uses_standard PASSED
tests/test_engines.py::TestRecommender::test_ml_gpu_returns_pytorch_image PASSED
tests/test_engines.py::TestDebugger::test_oom_detected PASSED
tests/test_engines.py::TestDebugger::test_port_conflict_detected PASSED
...
30 passed in 0.45s
```

**What is tested:**

- Image selection for all 12 project types
- Load tier scaling (tiny through xlarge)
- Runtime parameter values at each tier
- Dockerfile content — HEALTHCHECK, EXPOSE, multi-stage builds for Go/Rust
- docker run command includes memory and image flags
- All 11 error pattern detections
- Confidence scoring
- Container name substitution in commands
- Fallback behaviour for unknown project types
- Response field completeness

Run a specific test class:

```bash
pytest tests/test_engines.py::TestRecommender -v
pytest tests/test_engines.py::TestDebugger -v
```

---

## Frontend Development

The frontend is a React 18 app built with Vite.

**Start dev server:**

```bash
cd frontend
npm install
npm run dev
```

**Build for production:**

```bash
cd frontend
npm run build
# Output is in frontend/dist/
```

**Preview production build:**

```bash
npm run preview
```

**Vite proxy:** The `vite.config.js` proxies all `/api` requests to `http://localhost:8000` so the frontend can talk to the backend during development without CORS issues.

**Design system:** All colours and spacing are defined as CSS variables in `src/index.css`. The UI uses a black and white theme with IBM Plex Sans and IBM Plex Mono fonts.

---

## Deployment

### Railway (recommended free option)

1. Push the project to GitHub
2. Go to https://railway.app and create a new project
3. Connect your GitHub repository
4. Railway auto-detects the Dockerfile and builds it
5. Set environment variables in the Railway dashboard:
   ```
   ENV=production
   USE_ML_MODEL=false
   USE_ML_CLASSIFIER=false
   ```
6. Deploy — Railway gives you a public URL

For the frontend, deploy separately to Vercel or Netlify:

1. Push the `frontend/` folder or the full repo to GitHub
2. In Vercel/Netlify, set the root directory to `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Set environment variable: `VITE_API_URL=https://your-railway-url.railway.app`

Then update `frontend/src/api.js` to use the env variable:

```js
const BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : "/api";
```

---

### Render

1. Create a new Web Service on https://render.com
2. Connect your GitHub repository
3. Set:
   - **Environment:** Docker
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in the Render dashboard
5. Deploy

---

### Manual VPS / EC2

```bash
# On the server
git clone https://github.com/yourname/ai-docker-assistant.git
cd ai-docker-assistant

# Copy and edit env
cp .env.example .env

# Build and run
docker-compose up --build -d

# Check logs
docker-compose logs -f
```

---

## Troubleshooting

### Docker Desktop is not running

**Error:** `failed to connect to the docker API ... check if the daemon is running`

**Fix:**
1. Open Docker Desktop from the Start menu
2. Wait for the whale icon in the system tray to stop animating
3. Run `docker info` to confirm it is ready
4. Then run `docker-compose up --build` again

If Docker Desktop is open but still failing, right-click the whale icon in the system tray and click **Switch to Linux containers**.

---

### Port 8000 is already in use

**Error:** `bind: address already in use`

**Fix:**

```bash
# Find what is using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :8000
kill -9 <PID>
```

Or change the port in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"   # use 8001 on the host instead
```

---

### Frontend cannot reach the API

**Error:** `Network Error` or `Failed to fetch` in the browser

**Fix:** Make sure the backend is running on port 8000 before starting the frontend. The Vite dev server proxies `/api` to `http://localhost:8000`.

```bash
# Check the API is up
curl http://localhost:8000/health
```

---

### pip install fails inside Docker

**Error:** `Failed to establish a new connection` during `docker-compose up --build`

**Fix:** This is a network issue inside the Docker build. Make sure Docker Desktop has internet access. Try:

```bash
docker-compose build --no-cache
```

---

### Module not found errors in tests

**Fix:** Make sure your virtual environment is activated before running pytest:

```bash
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

pytest tests/ -v
```

---

## Roadmap

- [x] Phase 1 — FastAPI skeleton, Pydantic schemas, rule-based engines
- [x] Phase 2 — Scikit-learn RandomForest recommendation model
- [x] Phase 3 — TF-IDF + LogisticRegression log classifier
- [x] Phase 4 — React frontend, black and white design, centered layout
- [ ] Phase 5 — Deploy to Railway with CI/CD pipeline
- [ ] Phase 6 — Real Docker API integration (live image sizes, pull counts, vulnerability scan)
- [ ] Phase 7 — User feedback loop to continuously retrain models
- [ ] Phase 8 — Support for docker-compose.yml generation
- [ ] Phase 9 — GitHub Actions workflow for auto-testing on push
