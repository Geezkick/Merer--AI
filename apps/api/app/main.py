from fastapi import FastAPI

app = FastAPI(
    title="MERER AI API",
    description="AI evaluation infrastructure by BSANXS",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "product": "MERER AI",
        "module": "MERER Eval",
        "version": "0.1.0",
    }


@app.get("/api/v1")
async def api_info():
    return {
        "message": "MERER Eval API",
        "status": "development",
    }
