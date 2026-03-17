from pydantic import BaseModel, Field
from typing import Optional


# ── Recommendation ──────────────────────────────────────────────────────────

class RecommendRequest(BaseModel):
    project_type: str = Field(
        ...,
        example="fastapi",
        description=(
            "Type of project. Supported: fastapi, django, flask, node, react, "
            "nextjs, ml, postgres, redis, nginx, go, rust"
        ),
    )
    expected_users: int = Field(
        ...,
        ge=1,
        example=10000,
        description="Expected concurrent users",
    )
    language: Optional[str] = Field(
        None,
        example="python",
        description="Primary language (auto-detected if omitted)",
    )
    has_gpu: Optional[bool] = Field(
        False,
        description="Whether the workload requires GPU (relevant for ml projects)",
    )


class RuntimeParams(BaseModel):
    memory: str
    cpus: str
    restart_policy: str
    env_vars: list[str]
    extra_flags: list[str]


class RecommendResponse(BaseModel):
    base_image: str
    dockerfile_snippet: str
    docker_run_command: str
    runtime_params: RuntimeParams
    reasoning: str
    confidence: float
    alternatives: list[str]


# ── Debugging ────────────────────────────────────────────────────────────────

class DebugRequest(BaseModel):
    log_text: str = Field(
        ...,
        min_length=10,
        example="OOMKilled: container exceeded memory limit of 512Mi",
        description="Raw Docker log output to analyse",
    )
    container_name: Optional[str] = Field(None, example="my-api")
    image_name: Optional[str] = Field(None, example="python:3.12-slim")


class DebugResponse(BaseModel):
    root_cause: str
    confidence: float
    severity: str           # low | medium | high | critical
    fix_suggestion: str
    commands: list[str]
    explanation: str
    prevention_tip: str


# ── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
