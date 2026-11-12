from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db.session import init_db
from .api.v1.router import router as api_v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables created and directories ready
    settings.ensure_directories()
    await init_db()
    yield
    # Shutdown

app = FastAPI(
    title="CTF HUNTER X Core API",
    version=settings.VERSION,
    description="Evidence-based CTF Analysis & Flag Discovery Workstation",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_v1_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "mode": settings.MODE
    }

# Mount frontend if built
dist_dir = settings.BASE_DIR / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")
