"""
Recommendation Engine
─────────────────────
Phase 1  : Rule-based image + config lookup (active)
Phase 2  : Scikit-learn RandomForest model trained on Docker Hub metadata
           To activate: set USE_ML_MODEL = True after running ml/train_recommender.py

The public API (get_recommendation) stays identical in both phases.
"""

import os
import math
from app.schemas import RecommendRequest, RecommendResponse, RuntimeParams

USE_ML_MODEL = os.getenv("USE_ML_MODEL", "false").lower() == "true"

# ── Image registry ────────────────────────────────────────────────────────────
# project_type → config dict
IMAGE_REGISTRY: dict[str, dict] = {
    "fastapi": {
        "image_slim":   "python:3.12-slim",
        "image_standard": "python:3.12",
        "language":     "python",
        "port":         8000,
        "install":      "pip install --no-cache-dir -r requirements.txt",
        "cmd":          'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]',
        "healthcheck":  "curl -f http://localhost:8000/health || exit 1",
        "alternatives": ["tiangolo/uvicorn-gunicorn-fastapi:python3.12-slim"],
    },
    "django": {
        "image_slim":   "python:3.12-slim",
        "image_standard": "python:3.12",
        "language":     "python",
        "port":         8000,
        "install":      "pip install --no-cache-dir -r requirements.txt",
        "cmd":          'CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]',
        "healthcheck":  "curl -f http://localhost:8000/ || exit 1",
        "alternatives": ["python:3.11-slim"],
    },
    "flask": {
        "image_slim":   "python:3.12-slim",
        "image_standard": "python:3.12",
        "language":     "python",
        "port":         5000,
        "install":      "pip install --no-cache-dir -r requirements.txt",
        "cmd":          'CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "--workers", "2"]',
        "healthcheck":  "curl -f http://localhost:5000/ || exit 1",
        "alternatives": ["python:3.11-slim"],
    },
    "node": {
        "image_slim":   "node:20-alpine",
        "image_standard": "node:20",
        "language":     "javascript",
        "port":         3000,
        "install":      "npm ci --omit=dev",
        "cmd":          'CMD ["node", "server.js"]',
        "healthcheck":  "curl -f http://localhost:3000/health || exit 1",
        "alternatives": ["node:18-alpine"],
    },
    "react": {
        "image_slim":   "node:20-alpine",
        "image_standard": "node:20",
        "language":     "javascript",
        "port":         3000,
        "install":      "npm ci && npm run build",
        "cmd":          'CMD ["npx", "serve", "-s", "build", "-l", "3000"]',
        "healthcheck":  "curl -f http://localhost:3000 || exit 1",
        "alternatives": ["nginx:alpine  # serve the build output with nginx"],
    },
    "nextjs": {
        "image_slim":   "node:20-alpine",
        "image_standard": "node:20",
        "language":     "javascript",
        "port":         3000,
        "install":      "npm ci && npm run build",
        "cmd":          'CMD ["npm", "start"]',
        "healthcheck":  "curl -f http://localhost:3000 || exit 1",
        "alternatives": ["node:18-alpine"],
    },
    "ml": {
        "image_slim":   "python:3.12-slim",
        "image_standard": "python:3.12",
        "image_gpu":    "pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime",
        "language":     "python",
        "port":         8000,
        "install":      "pip install --no-cache-dir -r requirements.txt",
        "cmd":          'CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8000"]',
        "healthcheck":  "curl -f http://localhost:8000/health || exit 1",
        "alternatives": ["tensorflow/tensorflow:2.16.1", "huggingface/transformers-pytorch-cpu"],
    },
    "postgres": {
        "image_slim":   "postgres:16-alpine",
        "image_standard": "postgres:16",
        "language":     "sql",
        "port":         5432,
        "install":      "# No install step — use official image as-is",
        "cmd":          "# Postgres uses its own default entrypoint",
        "healthcheck":  "pg_isready -U postgres || exit 1",
        "alternatives": ["postgres:15-alpine"],
    },
    "redis": {
        "image_slim":   "redis:7-alpine",
        "image_standard": "redis:7",
        "language":     "none",
        "port":         6379,
        "install":      "# No install step — use official image as-is",
        "cmd":          'CMD ["redis-server", "--appendonly", "yes", "--maxmemory-policy", "allkeys-lru"]',
        "healthcheck":  "redis-cli ping | grep PONG || exit 1",
        "alternatives": ["valkey/valkey:7-alpine"],
    },
    "nginx": {
        "image_slim":   "nginx:alpine",
        "image_standard": "nginx:latest",
        "language":     "none",
        "port":         80,
        "install":      "COPY nginx.conf /etc/nginx/nginx.conf",
        "cmd":          "# nginx uses its own default entrypoint",
        "healthcheck":  "curl -f http://localhost/ || exit 1",
        "alternatives": ["caddy:alpine"],
    },
    "go": {
        "image_slim":   "golang:1.22-alpine",
        "image_standard": "golang:1.22",
        "language":     "go",
        "port":         8080,
        "install":      "RUN go mod download && go build -o server .",
        "cmd":          'CMD ["./server"]',
        "healthcheck":  "curl -f http://localhost:8080/health || exit 1",
        "alternatives": ["gcr.io/distroless/static-debian12  # minimal final stage for multi-stage builds"],
    },
    "rust": {
        "image_slim":   "rust:1.78-slim",
        "image_standard": "rust:1.78",
        "language":     "rust",
        "port":         8080,
        "install":      "RUN cargo build --release",
        "cmd":          'CMD ["./target/release/app"]',
        "healthcheck":  "curl -f http://localhost:8080/health || exit 1",
        "alternatives": ["gcr.io/distroless/cc-debian12  # for compiled Rust binaries"],
    },
}

_FALLBACK_KEY = "fastapi"


# ── Load tier thresholds ──────────────────────────────────────────────────────

def _load_tier(users: int) -> str:
    if users < 500:       return "tiny"
    if users < 5_000:     return "small"
    if users < 25_000:    return "medium"
    if users < 100_000:   return "large"
    return "xlarge"


_TIER_CONFIG = {
    #         memory   cpus   workers
    "tiny":   ("256m",  "0.5", 1),
    "small":  ("512m",  "1",   2),
    "medium": ("1g",    "2",   4),
    "large":  ("2g",    "4",   8),
    "xlarge": ("4g",    "8",   16),
}


# ── Image selection ───────────────────────────────────────────────────────────

def _pick_image(info: dict, users: int, has_gpu: bool) -> str:
    if has_gpu and "image_gpu" in info:
        return info["image_gpu"]
    # Use heavier image only for very high loads requiring native extensions
    if users >= 100_000 and info.get("language") in ("python", "javascript"):
        return info["image_standard"]
    return info["image_slim"]


# ── Dockerfile builder ────────────────────────────────────────────────────────

def _build_dockerfile(info: dict, image: str, port: int) -> str:
    language = info.get("language", "none")

    if language in ("python",):
        return f"""\
FROM {image}

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN {info['install']}

# Copy application code
COPY . .

# Expose application port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \\
  CMD {info['healthcheck']}

{info['cmd']}
"""

    if language in ("javascript",):
        return f"""\
FROM {image}

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN {info['install']}

# Copy source
COPY . .

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \\
  CMD {info['healthcheck']}

{info['cmd']}
"""

    if language in ("go",):
        return f"""\
# ── Build stage ──────────────────────────────────────────────
FROM {image} AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server .

# ── Runtime stage ─────────────────────────────────────────────
FROM alpine:3.20

WORKDIR /app
COPY --from=builder /app/server .

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
  CMD {info['healthcheck']}

{info['cmd']}
"""

    if language in ("rust",):
        return f"""\
# ── Build stage ──────────────────────────────────────────────
FROM {image} AS builder

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

# ── Runtime stage ─────────────────────────────────────────────
FROM debian:bookworm-slim

WORKDIR /app
COPY --from=builder /app/target/release/app .

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
  CMD {info['healthcheck']}

{info['cmd']}
"""

    # Generic / database / cache images
    return f"""\
FROM {image}

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \\
  CMD {info['healthcheck']}

{info['cmd']}
"""


# ── Runtime params ────────────────────────────────────────────────────────────

def _build_runtime(project_type: str, users: int, port: int, info: dict) -> RuntimeParams:
    tier = _load_tier(users)
    memory, cpus, workers = _TIER_CONFIG[tier]

    env_vars = [f"PORT={port}", "ENV=production"]
    extra_flags: list[str] = []

    if project_type in ("postgres",):
        env_vars = [
            "POSTGRES_DB=mydb",
            "POSTGRES_USER=admin",
            "POSTGRES_PASSWORD=changeme",
            "POSTGRES_MAX_CONNECTIONS=100",
        ]
        extra_flags = ["-v postgres_data:/var/lib/postgresql/data"]

    elif project_type in ("redis",):
        env_vars = []
        extra_flags = [
            f"--maxmemory {memory}",
            "--maxmemory-policy allkeys-lru",
            "-v redis_data:/data",
        ]

    elif project_type in ("ml",):
        env_vars = [f"PORT={port}", "ENV=production", f"WORKERS={workers}"]
        extra_flags = ["--shm-size=1g"]

    elif project_type in ("nginx",):
        env_vars = []
        extra_flags = ["-v ./nginx.conf:/etc/nginx/nginx.conf:ro"]

    return RuntimeParams(
        memory=memory,
        cpus=cpus,
        restart_policy="unless-stopped",
        env_vars=env_vars,
        extra_flags=extra_flags,
    )


# ── docker run command builder ────────────────────────────────────────────────

def _build_run_command(
    image: str,
    container_name: str,
    port: int,
    params: RuntimeParams,
) -> str:
    parts = [
        "docker run -d",
        f"  --name {container_name}",
        f"  --memory {params.memory}",
        f"  --cpus {params.cpus}",
        f"  --restart {params.restart_policy}",
        f"  -p {port}:{port}",
    ]
    for ev in params.env_vars:
        parts.append(f"  -e {ev}")
    for fl in params.extra_flags:
        parts.append(f"  {fl}")
    parts.append(f"  {image}")
    return " \\\n".join(parts)


# ── Rule-based engine ─────────────────────────────────────────────────────────

def _rule_based(req: RecommendRequest) -> RecommendResponse:
    key = req.project_type.lower().strip()
    info = IMAGE_REGISTRY.get(key, IMAGE_REGISTRY[_FALLBACK_KEY])
    image = _pick_image(info, req.expected_users, req.has_gpu or False)
    port = info["port"]
    container_name = f"my-{key}"

    runtime = _build_runtime(key, req.expected_users, port, info)
    tier = _load_tier(req.expected_users)

    reasoning = (
        f"Project '{key}' with {req.expected_users:,} expected users falls in the "
        f"'{tier}' load tier. "
        f"Selected '{image}' — "
        + (
            "GPU-enabled image for ML workloads."
            if req.has_gpu and "gpu" in image
            else "slim/alpine variant to minimise image size and attack surface."
            if "slim" in image or "alpine" in image
            else "standard image selected for compatibility with native extensions."
        )
        + f" Runtime capped at {runtime.memory} RAM / {runtime.cpus} CPU."
    )

    return RecommendResponse(
        base_image=image,
        dockerfile_snippet=_build_dockerfile(info, image, port),
        docker_run_command=_build_run_command(image, container_name, port, runtime),
        runtime_params=runtime,
        reasoning=reasoning,
        confidence=0.85 if key in IMAGE_REGISTRY else 0.60,
        alternatives=info.get("alternatives", []),
    )


# ── ML-based engine (Phase 2) ─────────────────────────────────────────────────

def _ml_based(req: RecommendRequest) -> RecommendResponse:
    """
    Phase 2: Load the trained Scikit-learn pipeline and use it to predict
    the best image. Falls back to rule-based if the model isn't found.

    To train the model run:  python ml/train_recommender.py
    """
    import pickle, pathlib

    model_path = pathlib.Path("ml/recommender_model.pkl")
    if not model_path.exists():
        return _rule_based(req)

    with open(model_path, "rb") as f:
        pipeline = pickle.load(f)

    features = [[
        req.project_type.lower(),
        req.expected_users,
        1 if req.has_gpu else 0,
    ]]

    predicted_image = pipeline.predict(features)[0]
    proba = pipeline.predict_proba(features)[0].max()

    # Use rule-based config for the rest (Dockerfile, runtime params etc.)
    base = _rule_based(req)

    return RecommendResponse(
        base_image=predicted_image,
        dockerfile_snippet=base.dockerfile_snippet.replace(base.base_image, predicted_image),
        docker_run_command=base.docker_run_command.replace(base.base_image, predicted_image),
        runtime_params=base.runtime_params,
        reasoning=f"[ML model] Predicted '{predicted_image}' with {proba:.0%} confidence for '{req.project_type}' at {req.expected_users:,} users.",
        confidence=round(float(proba), 2),
        alternatives=base.alternatives,
    )


# ── Public API ────────────────────────────────────────────────────────────────

def get_recommendation(req: RecommendRequest) -> RecommendResponse:
    if USE_ML_MODEL:
        return _ml_based(req)
    return _rule_based(req)
