from fastapi import APIRouter, HTTPException
from app.schemas import RecommendRequest, RecommendResponse
from app.engine.recommender import get_recommendation

router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    """
    Given a project type and expected user load, return the optimal Docker
    base image, Dockerfile snippet, docker run command, and runtime parameters.
    """
    try:
        return get_recommendation(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
