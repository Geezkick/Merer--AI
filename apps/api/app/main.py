from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(
    title="MERER AI API",
    description="AI evaluation infrastructure by BSANXS",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "product": "MERER AI",
        "module": "MERER Eval",
        "description": "The Infrastructure Behind Intelligence",
        "status": "operational",
        "api_docs": "/docs",
    }
