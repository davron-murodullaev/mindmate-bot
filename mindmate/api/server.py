"""FastAPI server — runs alongside the Telegram bot."""
import os
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from mindmate.core.config import settings
from mindmate.api.routes import career, exam, friends, stats, user

_WEBAPP_DIR = os.path.join(os.path.dirname(__file__), "../../webapp")


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
app.include_router(user.router, prefix="/api")
app.include_router(exam.router, prefix="/api")
app.include_router(career.router, prefix="/api")
app.include_router(friends.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/config")
async def get_config():
    return {"bot_username": settings.BOT_USERNAME}


# Serve the Mini App (index.html for all non-API routes)
if os.path.isdir(_WEBAPP_DIR):
    _index_html = os.path.join(_WEBAPP_DIR, "index.html")

    @app.get("/", include_in_schema=False)
    async def serve_root():
        return FileResponse(_index_html)

    # Serve static assets (css, js, images)
    app.mount("/static", StaticFiles(directory=_WEBAPP_DIR), name="static")
