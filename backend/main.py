from fastapi import FastAPI

from backend.routes.analysis import router as analysis_router
from backend.routes.phase_b import router as phase_b_router

app = FastAPI(
    title="SagarDhristi API",
    description="SAR-based oil spill detection and maritime analysis API",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "SagarDhristi API"
    }


app.include_router(analysis_router)
app.include_router(phase_b_router)