from fastapi import APIRouter, HTTPException
from app.schemas import DebugRequest, DebugResponse
from app.engine.debugger import analyse_logs

router = APIRouter()


@router.post("/debug", response_model=DebugResponse)
def debug(req: DebugRequest):
    """
    Accept raw Docker log text, detect the root cause using pattern matching
    + ML classifier, and return actionable fix suggestions with commands.
    """
    try:
        return analyse_logs(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
