#!/usr/bin/env python3
"""
SSID Finance Service
Root: 18_data_layer
Shard: Shard_10_Finanzen_Banking
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.endpoints import router as api_router
from src.api.middleware import setup_middleware
from src.api.health import router as health_router
from src.utils.hasher import init_hasher
from src.config import settings

app = FastAPI(
    title="Finance Service",
    version="2.0.0",
    description="Datenhaltung für Konten, Zahlungen"
)

# Setup middleware
setup_middleware(app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(api_router, prefix="/v1", tags=["api"])

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    init_hasher()
    print(f"🚀 {shard['domain'].title()} Service started")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
