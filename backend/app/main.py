import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app.seed_data import seed_database
from app.models import Incident
from app.constants import API_PREFIX
from app.routers import incidents, baselines, tech_debt, demo

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IncidentLoop API",
    description="Production-Incident Memory System with Similarity Engine & Anomaly Detection",
    version="2.0.0"
)

# Enable CORS for local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-seed database on first startup if empty
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        count = db.query(Incident).count()
        if count == 0:
            print("Auto-seeding empty database...")
            seed_database(db)
    finally:
        db.close()

# Register API Routers
app.include_router(incidents.router, prefix=API_PREFIX)
app.include_router(baselines.router, prefix=API_PREFIX)
app.include_router(tech_debt.router, prefix=API_PREFIX)
app.include_router(demo.router, prefix=API_PREFIX)

@app.get("/")
def root():
    return {
        "system": "IncidentLoop Backend",
        "status": "ONLINE",
        "docs_url": "/docs",
        "api_prefix": API_PREFIX
    }
