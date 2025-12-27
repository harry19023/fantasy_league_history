from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db

# Import models to ensure they're registered
from app.models import League, Matchup, Player, Team

# Create database tables
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
            "year": league.year,
            "settings": league.settings,
        }
        for league in leagues
    ]


@app.get("/leagues/{league_id}/teams")
async def get_teams(league_id: int, db: Session = Depends(get_db)):
    """Get all teams for a league"""
    teams = db.query(Team).filter(Team.league_id == league_id).all()
    return [
        {
            "id": team.id,
            "name": team.name,
            "owner_name": team.owner_name,
            "league_id": team.league_id,
        }
        for team in teams
    ]


@app.get("/teams/{team_id}/players")
async def get_team_players(team_id: int, db: Session = Depends(get_db)):
    """Get all players for a team"""
    players = db.query(Player).filter(Player.team_id == team_id).all()
    return [
        {
            "id": player.id,
            "name": player.name,
            "position": player.position,
            "team_id": player.team_id,
        }
        for player in players
    ]


@app.get("/leagues/{league_id}/matchups")
async def get_matchups(league_id: int, db: Session = Depends(get_db)):
    """Get all matchups for a league"""
    matchups = db.query(Matchup).filter(Matchup.league_id == league_id).all()
    return [
        {
            "id": matchup.id,
            "week": matchup.week,
            "team1_id": matchup.team1_id,
            "team2_id": matchup.team2_id,
            "team1_score": matchup.team1_score,
            "team2_score": matchup.team2_score,
        }
        for matchup in matchups
    ]


@app.get("/leagues/{league_id}/matchups/week/{week}")
async def get_week_matchups(league_id: int, week: int, db: Session = Depends(get_db)):
    """Get matchups for a specific week"""
    matchups = (
        db.query(Matchup)
        .filter(Matchup.league_id == league_id, Matchup.week == week)
        .all()
    )
    return [
        {
            "id": matchup.id,
            "week": matchup.week,
            "team1_id": matchup.team1_id,
            "team2_id": matchup.team2_id,
            "team1_score": matchup.team1_score,
            "team2_score": matchup.team2_score,
        }
        for matchup in matchups
    ]
