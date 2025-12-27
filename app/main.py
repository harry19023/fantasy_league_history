from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db

# Import models to ensure they're registered
from app.models import (
    Franchise,
    League,
    Season,
)


def init_db():
    """Initialize database tables. Call this explicitly when needed."""
    Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Fantasy League History API",
    description="API for tracking fantasy league statistics and history",
    version="0.1.0",
)

# CORS middleware (configure as needed)
app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Fantasy League History API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/leagues")
async def get_leagues(db: Session = Depends(get_db)):
    """Get all leagues"""
    leagues = db.query(League).all()
    return [
        {
            "id": league.id,
            "name": league.name,
            "settings": league.settings,
        }
        for league in leagues
    ]


@app.get("/leagues/{league_id}/franchises")
async def get_franchises(league_id: int, db: Session = Depends(get_db)):
    """Get all franchises for a league"""
    franchises = db.query(Franchise).filter(Franchise.league_id == league_id).all()
    return [
        {
            "id": franchise.id,
            "name": franchise.name,
            "league_id": franchise.league_id,
        }
        for franchise in franchises
    ]


@app.get("/leagues/{league_id}/seasons")
async def get_seasons(league_id: int, db: Session = Depends(get_db)):
    """Get all seasons for a league"""
    seasons = db.query(Season).filter(Season.league_id == league_id).all()
    return [
        {
            "id": season.id,
            "year": season.year,
            "start_date": season.start_date.isoformat() if season.start_date else None,
            "end_date": season.end_date.isoformat() if season.end_date else None,
            "league_id": season.league_id,
        }
        for season in seasons
    ]
