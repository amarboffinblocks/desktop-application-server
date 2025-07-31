from fastapi import APIRouter, HTTPException
from app.features.model.schemas import ModelSelectRequest
from app.features.model.controller import select_model_controller

router = APIRouter(prefix="/model", tags=["model"])

@router.post("/select")
async def select_model(request: ModelSelectRequest):
    result = await select_model_controller(request)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"]) 




