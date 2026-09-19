from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.analysis import router as analysis_router
from backend.routes.phase_b import router as phase_b_router


app = FastAPI(
    title="SagarDhristi API",
    description="SAR-based oil spill detection and maritime analysis API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sagardhristi-dts3.onrender.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "SagarDhristi API"
    }


app.include_router(analysis_router)
app.include_router(phase_b_router)