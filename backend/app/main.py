from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.retirements import router as retirements_router
from app.config import settings

app = FastAPI(
    title="Ultra Civic API",
    description="API for carbon allowance retirement and $PR token distribution",
    version="1.0.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(retirements_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Ultra Civic API is running"}