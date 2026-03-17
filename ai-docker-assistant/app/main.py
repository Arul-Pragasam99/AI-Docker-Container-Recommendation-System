from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import recommend, debug
from app.schemas import HealthResponse

app = FastAPI(
    title="AI Docker Assistant",
    description="AI-powered Docker image recommendations and intelligent log debugging",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend.router, prefix="/api", tags=["Recommendation"])
app.include_router(debug.router, prefix="/api", tags=["Debugging"])


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "AI Docker Assistant API",
        "docs": "/docs",
        "endpoints": {
            "recommend": "POST /api/recommend",
            "debug": "POST /api/debug",
        },
    }
