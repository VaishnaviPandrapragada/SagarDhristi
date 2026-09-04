from fastapi import FastAPI
from backend.routes.analysis import router as analysis_router

app = FastAPI(
    title="SagarDhristi API",
    description="SAR-based oil spill detection and maritime analysis API",
    version="1.0.0"
)

app.include_router(analysis_router)