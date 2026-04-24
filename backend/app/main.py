from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .database import engine, Base, SessionLocal
from .middleware.error_handler import GlobalErrorHandlerMiddleware
from .middleware.rate_limiter import RateLimitMiddleware
from .middleware.security import SecurityHeadersMiddleware, InputSanitizationMiddleware
from .routers import auth, users, sectors, items, orders, export
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


# Serve React frontend static files
frontend_build = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "dist")
if os.path.exists(frontend_build):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_build, "assets")), name="static")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_build, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_build, "index.html"))
