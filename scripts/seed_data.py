"""Script to seed the database with sample fantasy league data."""

from app.database import Base, SessionLocal, engine
from app.models import League, Matchup, Player, Team

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if data already exists
    existing_league = db.query(League).first()
    if existing_league:
        print("Sample data already exists. Skipping seed.")
        exit(0)

    # Create a league
    league = League(
        name="Fantasy Football League 2024",
        year=2024,
        settings={"scoring_type": "PPR", "teams": 8},
    )
    db.add(league)
    db.flush()

    # Create teams
    teams_data = [
        {"name": "Thunder Bolts", "owner_name": "Alice"},
        {"name": "Fire Dragons", "owner_name": "Bob"},
        {"name": "Ice Warriors", "owner_name": "Charlie"},
        {"name": "Storm Riders", "owner_name": "Diana"},
        {"name": "Lightning Strikes", "owner_name": "Eve"},
        {"name": "Blaze Runners", "owner_name": "Frank"},
        {"name": "Frost Giants", "owner_name": "Grace"},
        {"name": "Wind Walkers", "owner_name": "Henry"},
    ]

    teams = []
    for team_data in teams_data:
        team = Team(
            league_id=league.id,
            name=team_data["name"],
            owner_name=team_data["owner_name"],
        )
        db.add(team)
        teams.append(team)

    db.flush()

    # Create players
    players_data = [
        {"name": "Patrick Mahomes", "position": "QB"},
        {"name": "Josh Allen", "position": "QB"},
        {"name": "Lamar Jackson", "position": "QB"},
        {"name": "Jalen Hurts", "position": "QB"},
        {"name": "Christian McCaffrey", "position": "RB"},
        {"name": "Austin Ekeler", "position": "RB"},
        {"name": "Derrick Henry", "position": "RB"},
        {"name": "Saquon Barkley", "position": "RB"},
        {"name": "Tyreek Hill", "position": "WR"},
        {"name": "Davante Adams", "position": "WR"},
        {"name": "Stefon Diggs", "position": "WR"},
        {"name": "Cooper Kupp", "position": "WR"},
        {"name": "Travis Kelce", "position": "TE"},
        {"name": "Mark Andrews", "position": "TE"},
        {"name": "T.J. Hockenson", "position": "TE"},
    ]

    players = []
    for i, player_data in enumerate(players_data):
        player = Player(
            name=player_data["name"],
            position=player_data["position"],
            team_id=teams[i % len(teams)].id,  # Distribute players across teams
        )
        db.add(player)
        players.append(player)

    db.flush()

    # Create matchups for weeks 1-3
    import random

    random.seed(42)  # For reproducible results

    for week in range(1, 4):
        # Create matchups between teams
        team_indices = list(range(len(teams)))
        random.shuffle(team_indices)

        for i in range(0, len(teams), 2):
            team1 = teams[team_indices[i]]
            team2 = teams[team_indices[i + 1]]

            matchup = Matchup(
                league_id=league.id,
                week=week,
                team1_id=team1.id,
                team2_id=team2.id,
                team1_score=round(random.uniform(80, 150), 2),
                team2_score=round(random.uniform(80, 150), 2),
            )
            db.add(matchup)

    db.commit()
    print("✅ Successfully seeded database with sample data!")
    print(f"   - Created 1 league: {league.name}")
    print(f"   - Created {len(teams)} teams")
    print(f"   - Created {len(players)} players")
    print("   - Created matchups for weeks 1-3")

except Exception as e:
    db.rollback()
    print(f"❌ Error seeding database: {e}")
    raise
finally:
    db.close()
