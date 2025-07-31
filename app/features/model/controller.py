from fastapi import HTTPException
from app.features.model.manager import ModelManager
from app.features.model.schemas import ModelSelectRequest

async def select_model_controller(request: ModelSelectRequest):
    manager = ModelManager()
    try:
        if request.model_type not in ["gguf"]:
            raise ValueError("Invalid model type. Must be 'gguf'.")

        await manager.load_model(
            request.model_name, 
        )

        return {
            "success": True,
            "message": f"Model '{request.model_name}' ({request.model_type}) loaded successfully."
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ImportError as e:
        raise HTTPException(
            status_code=501,
            detail=f"Required dependencies not installed: {str(e)}"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model initialization failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model load error: {str(e)}"
        )


