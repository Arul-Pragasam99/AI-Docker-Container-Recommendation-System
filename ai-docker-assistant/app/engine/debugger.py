"""
Debugger Engine
───────────────
Phase 1/2 : Regex pattern matching — fast and reliable for known error types
Phase 3   : TF-IDF + LogisticRegression classifier for free-form logs
            To activate: set USE_ML_CLASSIFIER = True after running ml/train_debugger.py

The public API (analyse_logs) stays identical across all phases.
"""

import re
import os
from app.schemas import DebugRequest, DebugResponse

USE_ML_CLASSIFIER = os.getenv("USE_ML_CLASSIFIER", "false").lower() == "true"


# ── Pattern registry ──────────────────────────────────────────────────────────
# Each entry maps a regex → full diagnostic payload.
# Ordered from most specific to most general — first match wins.

PATTERNS: list[dict] = [
    # Out of memory
    {
        "pattern": r"(OOMKilled|out of memory|memory limit exceeded|exceeded memory|Killed process.*oom)",
        "root_cause": "Out of Memory (OOM)",
        "severity": "critical",
        "fix_suggestion": (
            "Your container was killed because it exceeded its memory limit. "
            "Increase --memory or optimise your application's memory usage."
        ),
        "explanation": (
            "The Linux OOM killer terminates the container's main process when "
            "available memory falls below the threshold set by --memory. "
            "This happens when the app has a memory leak, processes an unexpectedly "
            "large payload, or the limit is simply set too low for the workload."
        ),
        "prevention_tip": "Profile memory with 'docker stats' before setting limits. Add HEALTHCHECK and use restart policies to auto-recover.",
        "commands": [
            "docker stats <container>                            # check live memory usage",
            "docker update --memory 1g --memory-swap 2g <container>  # increase limit",
            "docker inspect <container> | grep -i memory         # check current limits",
        ],
    },

    # Port conflict
    {
        "pattern": r"(port.*already in use|bind.*address already in use|EADDRINUSE|listen.*bind.*failed)",
        "root_cause": "Port conflict",
        "severity": "high",
        "fix_suggestion": (
            "Another process is already bound to that port. "
            "Stop the conflicting process or map your container to a different host port."
        ),
        "explanation": (
            "Docker tries to bind the container port to the host network. "
            "If another process already owns that port (another container, or a local service), "
            "the bind fails. Common culprits: a previous container that wasn't stopped, "
            "a local dev server, or another Docker Compose service."
        ),
        "prevention_tip": "Use docker-compose which manages port allocation across services automatically.",
        "commands": [
            "lsof -i :<PORT>                        # find what owns the port",
            "kill -9 <PID>                          # free the port",
            "docker run -p 8001:8000 ...            # map to a different host port",
            "docker ps -a                           # check for stopped containers still holding ports",
        ],
    },

    # Permission denied
    {
        "pattern": r"(permission denied|Operation not permitted|EACCES|EPERM|cannot open.*read-only)",
        "root_cause": "Permission denied",
        "severity": "high",
        "fix_suggestion": (
            "The container process lacks permission to access a file, socket, or device. "
            "Check file ownership and the USER directive in your Dockerfile."
        ),
        "explanation": (
            "Containers run as root by default but mounted volumes inherit host file permissions. "
            "If a volume is owned by a different UID than the container process, access is denied. "
            "Also common when binding to privileged ports (<1024) as a non-root user."
        ),
        "prevention_tip": "Always set a non-root USER in your Dockerfile and use chown to fix volume ownership.",
        "commands": [
            "docker exec <container> ls -la /path/to/file       # inspect ownership",
            "docker run --user 1000:1000 ...                    # run as specific UID",
            "# In Dockerfile: RUN chown -R appuser:appuser /app",
            "docker run --cap-add NET_BIND_SERVICE ...          # allow binding to low ports",
        ],
    },

    # Connection refused
    {
        "pattern": r"(connection refused|ECONNREFUSED|dial tcp.*connect|connect.*failed|no route to host)",
        "root_cause": "Connection refused / network error",
        "severity": "high",
        "fix_suggestion": (
            "The container cannot reach a dependency (database, cache, external API). "
            "Verify the target service is running and that network configuration is correct."
        ),
        "explanation": (
            "Containers in Docker Compose share a private network by default, but they must "
            "reference each other by service name, not 'localhost'. "
            "Also common when a dependent service hasn't finished starting yet."
        ),
        "prevention_tip": "Use 'depends_on' with health checks in docker-compose.yml to enforce startup order.",
        "commands": [
            "docker network ls                                   # list networks",
            "docker network inspect <network>                   # check which containers are attached",
            "docker exec <container> ping <service-name>        # test connectivity",
            "# In docker-compose.yml: use service name not 'localhost'",
            "# e.g. DATABASE_URL=postgresql://user:pass@postgres:5432/db",
        ],
    },

    # Image not found
    {
        "pattern": r"(image.*not found|pull access denied|repository does not exist|manifest unknown|no such image|not found.*tag)",
        "root_cause": "Image not found",
        "severity": "medium",
        "fix_suggestion": (
            "Docker cannot find the specified image. "
            "Check the image name, tag, and registry credentials."
        ),
        "explanation": (
            "This happens when the image tag doesn't exist on the registry, "
            "the image name has a typo, or you're not authenticated to a private registry."
        ),
        "prevention_tip": "Pin images to specific digest hashes (e.g. python@sha256:...) to prevent tag drift.",
        "commands": [
            "docker pull <image>:<tag>                          # attempt manual pull",
            "docker login                                       # re-authenticate",
            "docker images | grep <image>                      # check local images",
            "docker search <image>                             # search Docker Hub",
        ],
    },

    # Disk full
    {
        "pattern": r"(no space left on device|disk quota exceeded|ENOSPC|write.*failed.*no space)",
        "root_cause": "Disk full",
        "severity": "critical",
        "fix_suggestion": (
            "The host or container filesystem is out of disk space. "
            "Clean up unused Docker objects immediately."
        ),
        "explanation": (
            "Docker stores image layers, build cache, volumes, and container logs on the host. "
            "Over time these accumulate and can exhaust disk space, causing crashes and failed builds."
        ),
        "prevention_tip": "Set up log rotation (--log-opt max-size=10m) and run 'docker system prune' in a cron job.",
        "commands": [
            "df -h                                              # check host disk usage",
            "docker system df                                  # show Docker disk usage breakdown",
            "docker system prune -af                           # remove all unused objects",
            "docker volume prune                               # remove unused volumes",
            "docker image prune -a                             # remove unused images",
        ],
    },

    # Missing environment variable
    {
        "pattern": r"(environment variable.*not set|KeyError.*env|getenv.*empty|required.*env.*missing|undefined.*environment)",
        "root_cause": "Missing environment variable",
        "severity": "medium",
        "fix_suggestion": (
            "A required environment variable is not set. "
            "Pass it via --env or a .env file."
        ),
        "explanation": (
            "Applications often require config via environment variables (database URL, API keys, etc.). "
            "When these are missing the app typically crashes on startup with a KeyError or similar."
        ),
        "prevention_tip": "Use a .env.example file in your repo to document required variables, and validate all env vars at startup.",
        "commands": [
            "docker run --env MY_VAR=value ...                 # pass single variable",
            "docker run --env-file .env ...                   # pass from file",
            "docker inspect <container> | grep -A 20 Env     # list current env vars",
        ],
    },

    # Health check failing
    {
        "pattern": r"(health.*unhealthy|healthcheck.*failed|container is unhealthy|starting.*unhealthy)",
        "root_cause": "Health check failing",
        "severity": "high",
        "fix_suggestion": (
            "The container health check is not passing. "
            "Inspect the health check command output and increase start_period if the app is slow to boot."
        ),
        "explanation": (
            "Docker runs the HEALTHCHECK command at intervals. If it fails retries times in a row, "
            "the container is marked 'unhealthy'. Orchestrators like Docker Compose and Kubernetes "
            "may then stop sending traffic or restart the container."
        ),
        "prevention_tip": "Set --start-period to a generous value (30–60s) for services that need time to initialise.",
        "commands": [
            "docker inspect --format='{{json .State.Health}}' <container>  # view health history",
            "docker exec <container> curl -f http://localhost:8000/health  # test manually",
            "# In Dockerfile: HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 CMD ...",
        ],
    },

    # Container crash / non-zero exit
    {
        "pattern": r"(exited with code [1-9]|exit code [1-9]|non-zero exit|container.*died|process.*killed)",
        "root_cause": "Container crash (non-zero exit code)",
        "severity": "high",
        "fix_suggestion": (
            "Your container exited unexpectedly. "
            "Check the CMD / entrypoint and review the full application logs."
        ),
        "explanation": (
            "A non-zero exit code indicates the main process terminated with an error. "
            "Common causes: application startup error, missing dependency, "
            "unhandled exception, or signal received (e.g. SIGTERM during deploy)."
        ),
        "prevention_tip": "Always handle SIGTERM gracefully and add structured logging so errors are easy to trace.",
        "commands": [
            "docker logs <container>                            # view full logs",
            "docker logs --tail 50 <container>                 # last 50 lines",
            "docker run --entrypoint sh <image>                # debug shell into image",
            "docker run --rm <image> python -c 'import app'   # test import on startup",
        ],
    },

    # SSL / TLS error
    {
        "pattern": r"(ssl.*error|certificate.*expired|certificate.*verify.*failed|TLS.*handshake|x509)",
        "root_cause": "SSL / TLS certificate error",
        "severity": "high",
        "fix_suggestion": (
            "A TLS certificate is invalid, expired, or untrusted. "
            "Check certificate validity and ensure CA bundles are up to date inside the image."
        ),
        "explanation": (
            "Slim and Alpine-based images often ship without full CA bundles. "
            "If your app connects to HTTPS services, you may need to install ca-certificates."
        ),
        "prevention_tip": "Add 'RUN apk add --no-cache ca-certificates' (Alpine) or 'RUN apt-get install -y ca-certificates' (Debian slim) to your Dockerfile.",
        "commands": [
            "docker exec <container> openssl s_client -connect host:443  # test TLS",
            "# Alpine: RUN apk add --no-cache ca-certificates && update-ca-certificates",
            "# Debian slim: RUN apt-get update && apt-get install -y ca-certificates",
        ],
    },

    # Timeout
    {
        "pattern": r"(timeout|timed out|deadline exceeded|context deadline|read timeout|write timeout)",
        "root_cause": "Timeout",
        "severity": "medium",
        "fix_suggestion": (
            "A network call or operation exceeded its time limit. "
            "Check for slow dependencies, increase timeouts, or add retry logic."
        ),
        "explanation": (
            "Timeouts commonly occur when a dependent service (DB, external API) is slow to respond, "
            "the network has high latency, or a service is temporarily unavailable."
        ),
        "prevention_tip": "Implement circuit breakers and exponential backoff retries for all external service calls.",
        "commands": [
            "docker exec <container> ping <dependency>         # test network latency",
            "docker stats                                      # check CPU/memory under load",
            "docker logs <dependency-container>               # check if dependency is healthy",
        ],
    },
]

# ── Unknown fallback ──────────────────────────────────────────────────────────

_UNKNOWN: dict = {
    "root_cause": "Unknown / unrecognised error",
    "severity": "low",
    "fix_suggestion": (
        "No known error pattern matched. Review the full log output or provide more context."
    ),
    "explanation": (
        "The log content doesn't match any known Docker error pattern. "
        "This could be an application-level error, a configuration issue, or a new type of failure."
    ),
    "prevention_tip": "Enable structured JSON logging in your application to make errors easier to parse.",
    "commands": [
        "docker logs --tail 200 <container>                    # review more log history",
        "docker events --filter container=<container>         # check Docker events",
        "docker inspect <container>                           # inspect container config",
    ],
}


# ── Pattern matcher ───────────────────────────────────────────────────────────

def _pattern_match(log: str) -> tuple[dict, float]:
    log_lower = log.lower()
    for entry in PATTERNS:
        matches = re.findall(entry["pattern"], log_lower, re.IGNORECASE)
        if matches:
            # Confidence scales with number of matching signals, capped at 0.97
            confidence = round(min(0.70 + 0.09 * len(matches), 0.97), 2)
            return entry, confidence
    return _UNKNOWN, 0.35


# ── ML classifier (Phase 3) ───────────────────────────────────────────────────

def _ml_classify(log: str) -> tuple[dict | None, float]:
    """
    Phase 3: TF-IDF vectoriser + LogisticRegression classifier.
    Trained on labelled Docker log snippets (ml/train_debugger.py).
    Returns None if model file not found — caller falls back to pattern match.
    """
    import pickle, pathlib

    model_path = pathlib.Path("ml/debugger_model.pkl")
    if not model_path.exists():
        return None, 0.0

    with open(model_path, "rb") as f:
        pipeline = pickle.load(f)

    label_map: dict[str, dict] = {e["root_cause"]: e for e in PATTERNS}

    predicted_label = pipeline.predict([log])[0]
    proba = pipeline.predict_proba([log])[0].max()

    matched = label_map.get(predicted_label)
    if not matched:
        return None, 0.0

    return matched, round(float(proba), 2)


# ── Public API ────────────────────────────────────────────────────────────────

def analyse_logs(req: DebugRequest) -> DebugResponse:
    entry, confidence = None, 0.0

    if USE_ML_CLASSIFIER:
        entry, confidence = _ml_classify(req.log_text)

    # Fall back to pattern matching if ML not available or confidence too low
    if entry is None or confidence < 0.50:
        entry, confidence = _pattern_match(req.log_text)

    container = req.container_name or "<container>"
    commands = [cmd.replace("<container>", container) for cmd in entry["commands"]]

    return DebugResponse(
        root_cause=entry["root_cause"],
        confidence=confidence,
        severity=entry["severity"],
        fix_suggestion=entry["fix_suggestion"],
        commands=commands,
        explanation=entry["explanation"],
        prevention_tip=entry["prevention_tip"],
    )
