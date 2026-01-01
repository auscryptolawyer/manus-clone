"""FastAPI application setup and routes."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from loguru import logger
import sys

from config import get_settings, Settings
from api.websocket import websocket_endpoint


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG",
)
logger.add(
    "logs/agent.log",
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Manus Clone API")
    yield
    logger.info("Shutting down Manus Clone API")


# Create FastAPI app
app = FastAPI(
    title="Manus Clone",
    description="Personal browser automation agent",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/config")
async def get_config():
    """Get public configuration."""
    settings = get_settings()
    return {
        "max_steps": settings.max_steps_per_task,
        "step_timeout": settings.step_timeout_seconds,
    }


@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """WebSocket endpoint for task execution."""
    settings = get_settings()
    await websocket_endpoint(websocket, settings)


# Serve frontend static files in production
# Uncomment these lines when building for production:
# app.mount("/assets", StaticFiles(directory="web/dist/assets"), name="assets")
# @app.get("/")
# async def serve_frontend():
#     return FileResponse("web/dist/index.html")


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
