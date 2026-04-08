from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os
from contextlib import asynccontextmanager
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.api.v1.api import api_router

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=1.0,
        send_default_pii=True
    )

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

# Serve shared asset files such as local fonts used by the frontend.
APP_ASSETS_DIR = os.path.join(os.getcwd(), "app", "assets")
if os.path.exists(APP_ASSETS_DIR):
    app.mount("/app-assets", StaticFiles(directory=APP_ASSETS_DIR), name="app-assets")

# Serve built Vite assets when present.
FRONTEND_DIST_DIR = os.path.join(os.getcwd(), "frontend", "dist")
FRONTEND_ASSETS_DIR = os.path.join(FRONTEND_DIST_DIR, "assets")

if os.path.exists(FRONTEND_ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS_DIR), name="frontend-assets")

FRONTEND_INDEX = os.path.join(FRONTEND_DIST_DIR, "index.html")


def frontend_missing_response() -> HTMLResponse:
    return HTMLResponse(
        """
        <html>
            <body style="font-family: sans-serif; padding: 40px;">
                <h1>Frontend build not found.</h1>
                <p>Run <code>cd frontend && npm install && npm run build</code> or start the Vite dev server with <code>npm run dev</code>.</p>
            </body>
        </html>
        """,
        status_code=503,
    )

@app.get("/", response_class=HTMLResponse)
async def serve_spa():
    """Serve the built React SPA frontend."""
    if os.path.exists(FRONTEND_INDEX):
        return FileResponse(FRONTEND_INDEX, media_type="text/html")
    return frontend_missing_response()

# Catch-all for SPA routes
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_spa_catchall(full_path: str):
    """Catch-all to serve the SPA for any non-API, non-static route."""
    if full_path.startswith(("api/", "media/", "assets/", "app-assets/", "docs", "redoc", "openapi.json")):
        return HTMLResponse("<html><body><h1>Not found.</h1></body></html>", status_code=404)
    if os.path.exists(FRONTEND_INDEX):
        return FileResponse(FRONTEND_INDEX, media_type="text/html")
    return frontend_missing_response()
