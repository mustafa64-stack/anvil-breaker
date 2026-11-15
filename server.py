# server.py
"""
Anvil Breaker™ Server
Modular ASGI application serving high-performance algorithmic engineering APIs and private developer vaults.
Architected by Mustafa Marjani.
"""
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import database
from app.core.config import settings
from app.core.security import SecurityHeadersMiddleware

# Import Modular API Routers (Phase 3 Architecture)
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.sheets import router as sheets_router
from app.api.endpoints.progress import router as progress_router
from app.api.endpoints.browser import router as browser_router
from app.api.endpoints.badge import router as badge_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="High-throughput algorithmic engineering system with 15-minute protocol and private developer vaults."
)

# CORS Security: strictly restricted to settings.CORS_ORIGINS (Phase 1 Security Gate)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount security headers middleware (HSTS, CSP, X-Frame-Options)
app.add_middleware(SecurityHeadersMiddleware)

# Mount Modular API Routers under /api
app.include_router(auth_router, prefix="/api")
app.include_router(sheets_router, prefix="/api")
app.include_router(progress_router, prefix="/api")
app.include_router(browser_router, prefix="/api")
app.include_router(badge_router, prefix="/api")

# Initialize SQLite database and run one-time migrations
database.init_db()
database.migrate_json_to_sqlite()

# Mount Static Assets
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# ==================== HTML PAGE ROUTES ====================

# Official Home & Landing Vault
@app.get("/")
@app.get("/home")
@app.get("/welcome")
@app.get("/landing")
@app.get("/login")
@app.get("/register")
@app.get("/signup")
def serve_home():
    landing_file = os.path.join(settings.STATIC_DIR, "landing.html")
    if os.path.exists(landing_file):
        return FileResponse(landing_file)
    return FileResponse(os.path.join(settings.STATIC_DIR, "index.html"))

# Private Workspace Command Center (Authenticated Personal Vault)
@app.get("/app")
@app.get("/workspace")
@app.get("/solver")
@app.get("/dashboard")
def serve_app():
    index_file = os.path.join(settings.STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"message": f"{settings.PROJECT_NAME} API Ready"})

# Floating Pop-Up Mini HUD Endpoint
@app.get("/mini-hud")
@app.get("/mini")
def serve_mini_hud():
    mini_file = os.path.join(settings.STATIC_DIR, "mini.html")
    if os.path.exists(mini_file):
        return FileResponse(mini_file)
    return FileResponse(os.path.join(settings.STATIC_DIR, "index.html"))

# Cloud Health Check Endpoint (Render, Railway, Fly.io, Kubernetes)
@app.get("/healthz")
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "domain": settings.DOMAIN,
        "base_url": settings.BASE_URL,
        "founder": settings.FOUNDER,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8765))
    print(f"Starting {settings.PROJECT_NAME} on http://{host}:{port}")
    uvicorn.run("server:app", host=host, port=port, log_level="info")
