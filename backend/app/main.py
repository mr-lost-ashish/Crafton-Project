import os

# Auto-load .env file if present
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import engine, Base, SessionLocal
from .seed_data import seed_database
from .routes import (
    auth, fields, scans, outbreaks, risk, voice, community, treatments, support, admin
)

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CropGuard API",
    description="Early detection and management of crop diseases and pest infestations (PRD v0.1 / v0.2)",
    version="0.2.0"
)

# Enable CORS for local development and PWA clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Hook: Seed Reference Data
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

# Include Routers
app.include_router(auth.router)
app.include_router(fields.router)
app.include_router(scans.router)
app.include_router(outbreaks.router)
app.include_router(risk.router)
app.include_router(voice.router)
app.include_router(community.router)
app.include_router(treatments.router)
app.include_router(support.router)
app.include_router(admin.router)

# Mount Static Directories
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_images")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/sample_images", StaticFiles(directory=SAMPLE_DIR), name="sample_images")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "app": "CropGuard API",
        "version": "0.2.0",
        "docs_url": "/docs",
        "status": "online",
        "message": "CropGuard backend is active. Load the frontend at /"
    }
