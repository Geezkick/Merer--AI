from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "product": "MERER AI",
        "module": "MERER Eval",
        "version": "0.1.0",
    }


@router.get("/")
async def api_info():
    return {
        "message": "MERER Eval API",
        "status": "development",
        "version": "0.1.0",
    }
