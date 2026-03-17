"""
Tests for the AI Docker Assistant
Run: pytest tests/ -v
"""

import sys
import os
import types

# ── Proper FastAPI stubs (Pylance-safe using setattr) ────────────────────────

fastapi_stub = types.ModuleType("fastapi")

class _Router:
    def __init__(self, *a, **kw): pass

class _App:
    def __init__(self, *a, **kw): pass

setattr(fastapi_stub, "APIRouter", _Router)
setattr(fastapi_stub, "FastAPI", _App)
setattr(fastapi_stub, "HTTPException", Exception)

cors_stub = types.ModuleType("fastapi.middleware.cors")

class _CORS:
    def __init__(self, *a, **kw): pass

setattr(cors_stub, "CORSMiddleware", _CORS)

sys.modules["fastapi"] = fastapi_stub
sys.modules["fastapi.middleware"] = types.ModuleType("fastapi.middleware")
sys.modules["fastapi.middleware.cors"] = cors_stub

# ── Path setup ───────────────────────────────────────────────────────────────

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Imports ──────────────────────────────────────────────────────────────────

from app.schemas import RecommendRequest, DebugRequest
from app.engine.recommender import get_recommendation
from app.engine.debugger import analyse_logs


# ══════════════════════════════════════════════════════════════════════════════
# Recommender tests
# ══════════════════════════════════════════════════════════════════════════════

class TestRecommender:

    def _req(self, project_type: str, users: int, gpu: bool = False) -> RecommendRequest:
        return RecommendRequest(
            project_type=project_type,
            expected_users=users,
            has_gpu=gpu,
            language=None
        )

    def test_fastapi_small_load_uses_slim(self):
        r = get_recommendation(self._req("fastapi", 1000))
        assert "slim" in r.base_image

    def test_fastapi_huge_load_uses_standard(self):
        r = get_recommendation(self._req("fastapi", 200_000))
        assert r.base_image == "python:3.12"

    def test_node_uses_alpine(self):
        r = get_recommendation(self._req("node", 5000))
        assert "alpine" in r.base_image

    def test_ml_gpu_returns_pytorch_image(self):
        r = get_recommendation(self._req("ml", 100, gpu=True))
        assert "pytorch" in r.base_image or "cuda" in r.base_image

    def test_postgres_returns_alpine(self):
        r = get_recommendation(self._req("postgres", 1000))
        assert "alpine" in r.base_image

    def test_unknown_project_returns_fallback(self):
        r = get_recommendation(self._req("someunknownframework", 1000))
        assert r.base_image is not None
        assert r.confidence < 0.70

    def test_tiny_load_params(self):
        r = get_recommendation(self._req("fastapi", 100))
        assert r.runtime_params.memory == "256m"
        assert r.runtime_params.cpus == "0.5"

    def test_medium_load_params(self):
        r = get_recommendation(self._req("fastapi", 10_000))
        assert r.runtime_params.memory == "512m"

    def test_large_load_params(self):
        r = get_recommendation(self._req("fastapi", 75_000))
        assert r.runtime_params.memory == "2g"
        assert r.runtime_params.cpus == "4"

    def test_xlarge_load_params(self):
        r = get_recommendation(self._req("fastapi", 200_000))
        assert r.runtime_params.memory == "4g"

    def test_dockerfile_contains_base_image(self):
        r = get_recommendation(self._req("fastapi", 1000))
        assert r.base_image in r.dockerfile_snippet

    def test_dockerfile_contains_healthcheck(self):
        r = get_recommendation(self._req("fastapi", 1000))
        assert "HEALTHCHECK" in r.dockerfile_snippet

    def test_dockerfile_exposes_port(self):
        r = get_recommendation(self._req("fastapi", 1000))
        assert "EXPOSE" in r.dockerfile_snippet

    def test_go_uses_multistage_dockerfile(self):
        r = get_recommendation(self._req("go", 1000))
        assert "AS builder" in r.dockerfile_snippet

    def test_rust_uses_multistage_dockerfile(self):
        r = get_recommendation(self._req("rust", 1000))
        assert "AS builder" in r.dockerfile_snippet

    def test_run_command_contains_memory_flag(self):
        r = get_recommendation(self._req("fastapi", 1000))
        assert "--memory" in r.docker_run_command

    def test_run_command_contains_image(self):
        r = get_recommendation(self._req("fastapi", 1000))
        assert r.base_image in r.docker_run_command

    def test_fastapi_has_alternatives(self):
        r = get_recommendation(self._req("fastapi", 1000))
        assert len(r.alternatives) > 0


# ══════════════════════════════════════════════════════════════════════════════
# Debugger tests
# ══════════════════════════════════════════════════════════════════════════════

class TestDebugger:

    def _req(self, log: str, container: str = "test-container") -> DebugRequest:
        return DebugRequest(
            log_text=log,
            container_name=container,
            image_name=None
        )

    def test_oom_detected(self):
        r = analyse_logs(self._req("OOMKilled: container exceeded memory limit of 512Mi"))
        assert r.root_cause == "Out of Memory (OOM)"
        assert r.severity == "critical"

    def test_oom_alternate_wording(self):
        r = analyse_logs(self._req("fatal error: runtime: out of memory"))
        assert r.root_cause == "Out of Memory (OOM)"

    def test_port_conflict_detected(self):
        r = analyse_logs(self._req("Error: listen EADDRINUSE :::3000"))
        assert r.root_cause == "Port conflict"

    def test_permission_denied_detected(self):
        r = analyse_logs(self._req("permission denied: /var/run/docker.sock"))
        assert r.root_cause == "Permission denied"

    def test_connection_refused_detected(self):
        r = analyse_logs(self._req("dial tcp 127.0.0.1:5432: connect: connection refused"))
        assert r.root_cause == "Connection refused / network error"

    def test_image_not_found_detected(self):
        r = analyse_logs(self._req("manifest for myimage:latest not found: manifest unknown"))
        assert r.root_cause == "Image not found"

    def test_disk_full_detected(self):
        r = analyse_logs(self._req("write /var/lib/docker/overlay2: no space left on device"))
        assert r.root_cause == "Disk full"
        assert r.severity == "critical"

    def test_missing_env_var_detected(self):
        r = analyse_logs(self._req("KeyError: 'DATABASE_URL'"))
        assert r.root_cause == "Missing environment variable"

    def test_health_check_detected(self):
        r = analyse_logs(self._req("container is unhealthy after 3 retries"))
        assert r.root_cause == "Health check failing"

    def test_crash_exit_code_detected(self):
        r = analyse_logs(self._req("exited with code 1"))
        assert r.root_cause == "Container crash (non-zero exit code)"

    def test_ssl_error_detected(self):
        r = analyse_logs(self._req("x509: certificate has expired or is not yet valid"))
        assert r.root_cause == "SSL / TLS certificate error"

    def test_timeout_detected(self):
        r = analyse_logs(self._req("context deadline exceeded (Client.Timeout exceeded)"))
        assert r.root_cause == "Timeout"

    def test_unknown_returns_fallback(self):
        r = analyse_logs(self._req("some completely random log line with no known pattern"))
        assert r.root_cause == "Unknown / unrecognised error"
        assert r.confidence < 0.50

    def test_known_error_has_high_confidence(self):
        r = analyse_logs(self._req("OOMKilled: container exceeded memory limit"))
        assert r.confidence >= 0.70

    def test_multiple_signals_increase_confidence(self):
        single = analyse_logs(self._req("OOMKilled"))
        multi  = analyse_logs(self._req("OOMKilled out of memory exceeded memory limit killed process"))
        assert multi.confidence >= single.confidence

    def test_response_contains_commands(self):
        r = analyse_logs(self._req("OOMKilled: exceeded memory"))
        assert len(r.commands) > 0

    def test_container_name_substituted_in_commands(self):
        r = analyse_logs(self._req("OOMKilled: exceeded memory", container="my-api"))
        assert any("my-api" in cmd for cmd in r.commands)

    def test_response_has_explanation(self):
        r = analyse_logs(self._req("OOMKilled: exceeded memory"))
        assert len(r.explanation) > 20

    def test_response_has_prevention_tip(self):
        r = analyse_logs(self._req("OOMKilled: exceeded memory"))
        assert len(r.prevention_tip) > 10