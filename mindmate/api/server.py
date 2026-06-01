"""FastAPI server — runs alongside the Telegram bot."""
import os
from contextlib import asynccontextmanager
from pathlib import Path

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from mindmate.core.config import settings
from mindmate.api.routes import career, exam, friends, stats, user

# Resolve webapp directory robustly: walk up from this file to project root.
# Works regardless of working directory (local, Render, Heroku, Docker).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_WEBAPP_DIR   = _PROJECT_ROOT / "webapp"
_INDEX_HTML   = _WEBAPP_DIR / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=2,
        max_size=8,
        command_timeout=30,
    )
    yield
    await app.state.pool.close()


app = FastAPI(title="MindMate API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(user.router,    prefix="/api")
app.include_router(exam.router,    prefix="/api")
app.include_router(career.router,  prefix="/api")
app.include_router(friends.router, prefix="/api")
app.include_router(stats.router,   prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/config")
async def get_config():
    return {"bot_username": settings.BOT_USERNAME}


# ── Mini App static serving ────────────────────────────────────────────────
# Always register / so the route exists even if the file isn't found yet.
@app.get("/", include_in_schema=False)
async def serve_root():
    if _INDEX_HTML.is_file():
        return FileResponse(str(_INDEX_HTML), media_type="text/html")
    return HTMLResponse("<h2>MindMate API is running ✓</h2><p>webapp/index.html not found.</p>", status_code=200)


# Catch-all: serve index.html for any non-API path (SPA routing).
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    # Don't intercept API routes (handled above)
    if full_path.startswith("api/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    # Try exact file first, fall back to index.html
    target = _WEBAPP_DIR / full_path
    if target.is_file():
        return FileResponse(str(target))
    if _INDEX_HTML.is_file():
        return FileResponse(str(_INDEX_HTML), media_type="text/html")
    return HTMLResponse("<h2>MindMate API is running ✓</h2>", status_code=200)
