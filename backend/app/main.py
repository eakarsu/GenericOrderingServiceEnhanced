from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .database import engine, Base, SessionLocal
from .middleware.error_handler import GlobalErrorHandlerMiddleware
from .middleware.rate_limiter import RateLimitMiddleware
from .middleware.security import SecurityHeadersMiddleware, InputSanitizationMiddleware
from .routers import auth, users, sectors, items, orders, export, ai
from .seed import seed_database

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Generic Ordering Service Enhanced",
    description="Universal multi-sector ordering and service management platform",
    version="2.0.0"
)

# Middleware (order matters - outermost first)
app.add_middleware(GlobalErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware, requests_limit=200, window=60)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputSanitizationMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(sectors.router)
app.include_router(items.router)
app.include_router(orders.router)
app.include_router(export.router)
app.include_router(ai.router)
from .routers import analytics_api as _aa, realtime as _rt, payments as _pay, tenant_onboarding as _ton, recommendations as _rec, multi_channel_intake as _mc  # noqa: E402
app.include_router(_aa.router); app.include_router(_rt.router); app.include_router(_pay.router); app.include_router(_ton.router); app.include_router(_rec.router); app.include_router(_mc.router)
from .routers import customViews as _cv  # noqa: E402
app.include_router(_cv.router)

# Seed database on startup
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "Generic Ordering Service Enhanced"}


@app.get("/api/stats")
def get_stats():
    """Dashboard statistics."""
    db = SessionLocal()
    try:
        from .models import User, Sector, Item, Order
        return {
            "total_users": db.query(User).count(),
            "total_sectors": db.query(Sector).count(),
            "total_items": db.query(Item).count(),
            "total_orders": db.query(Order).count(),
            "pending_orders": db.query(Order).filter(Order.status == "pending").count(),
            "completed_orders": db.query(Order).filter(Order.status == "completed").count(),
        }
    finally:
        db.close()


# Serve React frontend static files (preferred) — falls back to the
# bundled minimal HTML/JS dev console under backend/app/static/ if the
# React build is not available.
frontend_build = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "dist")
minimal_static = os.path.join(os.path.dirname(__file__), "static")

# Always expose the bundled minimal AI console at /ai-console so it's
# reachable even when the React build is present at /.
if os.path.exists(minimal_static):
    @app.get("/ai-console")
    async def serve_ai_console():
        return FileResponse(os.path.join(minimal_static, "index.html"))


if os.path.exists(frontend_build):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_build, "assets")), name="static")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_build, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_build, "index.html"))
elif os.path.exists(minimal_static):
    app.mount("/static", StaticFiles(directory=minimal_static), name="minimal_static")

    @app.get("/")
    async def serve_minimal_index():
        return FileResponse(os.path.join(minimal_static, "index.html"))
