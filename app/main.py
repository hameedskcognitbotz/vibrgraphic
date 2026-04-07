from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    yield
    # Shutdown logic

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI Infographic Generator Backend API",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve local media files
MEDIA_DIR = os.path.join(os.getcwd(), "media")
os.makedirs(MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Serve frontend static assets (CSS, JS, images)
FRONTEND_DIST_DIR = os.path.join(os.getcwd(), "frontend-react", "dist")
FRONTEND_ASSETS_DIR = os.path.join(FRONTEND_DIST_DIR, "assets")

if os.path.exists(FRONTEND_ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS_DIR), name="frontend-assets")
elif os.path.exists(os.path.join(os.getcwd(), "frontend", "assets")):
    # Fallback to old vanilla JS for safety if React isn't built yet
    app.mount("/frontend/assets", StaticFiles(directory=os.path.join(os.getcwd(), "frontend", "assets")), name="frontend-assets-legacy")

FRONTEND_INDEX = os.path.join(FRONTEND_DIST_DIR, "index.html")
if not os.path.exists(FRONTEND_INDEX):
    # Fallback
    FRONTEND_INDEX = os.path.join(os.getcwd(), "frontend", "index.html")

@app.get("/", response_class=HTMLResponse)
async def serve_spa():
    """Serve the React SPA frontend."""
    return FileResponse(FRONTEND_INDEX, media_type="text/html")

# Catch-all for SPA routes
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_spa_catchall(full_path: str):
    """Catch-all to serve the SPA for any non-API, non-static route."""
    if full_path.startswith(("api/", "media/", "frontend/", "assets/", "docs", "redoc", "openapi.json")):
        return None
    if os.path.exists(FRONTEND_INDEX):
        return FileResponse(FRONTEND_INDEX, media_type="text/html")
    return HTMLResponse("<html><body><h1>Frontend not built. Run npm run build in frontend-react.</h1></body></html>", status_code=404)
