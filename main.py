"""
Application entrypoint.

This file only wires things together: it creates the FastAPI app, applies
middleware, and registers a startup hook. It intentionally does NOT contain
business logic — routes for documents/chat will be added as separate
routers in api/v1/ in future modules, then included here with
`app.include_router(...)`.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import create_tables

app = FastAPI(title=settings.app_name, debug=settings.debug)

# Allows the React frontend (running on a different port/origin during
# development) to call this API. Without this, the browser blocks requests
# due to the same-origin policy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """
    Creates database tables (if they don't already exist) when the app
    starts. Safe to run every time — create_all is a no-op for tables
    that already exist.
    """
    create_tables()


@app.get("/health")
def health_check() -> dict[str, str]:
    """
    Basic liveness check confirming the app and its configuration loaded
    correctly. Useful for verifying deployment/startup before building
    any real endpoints on top of it.
    """
    return {"status": "ok", "app_name": settings.app_name}
