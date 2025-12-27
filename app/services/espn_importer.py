"""Service for importing ESPN Fantasy data into the database."""

from typing import Any

from sqlalchemy.orm import Session

from app.models.franchise import Franchise
from app.models.franchise_season import FranchiseSeason
from app.models.league import League
from app.models.manager import Manager
from app.models.season import Season
from app.services.espn_client import ESPNClient


class ESPNImporter:
    """Service for importing ESPN Fantasy data."""

    def __init__(self, client: ESPNClient | None = None):
        """Initialize importer with ESPN client.

        Args:
            client: ESPN client instance. If None, creates a new one.
        """
        self.client = client or ESPNClient()

    def import_league_first_season(
        self, db: Session, league_id: int, scoring_period_id: int | None = None
    ) -> dict[str, Any]:
        """Import league, first season, teams, and managers from ESPN.

        Args:
            db: Database session
            league_id: ESPN league ID
            scoring_period_id: Optional scoring period ID

        Returns:
            Dictionary with imported entities:
            {
                "league": League,
                "season": Season,
                "franchises": list[Franchise],
                "managers": list[Manager],
                "franchise_seasons": list[FranchiseSeason],
            }
        """
        # Fetch league history from ESPN
        history = self.client.get_league_history(league_id, scoring_period_id)
        if not history:
            raise ValueError(f"No league history found for league_id {league_id}")

        # Get first season (sorted by seasonId)
        first_season_data = sorted(history, key=lambda x: x["seasonId"])[0]

        # Create or get League
        league_name = first_season_data["settings"]["name"]
        league = db.query(League).filter(League.name == league_name).first()
        if not league:
            league = League(
                name=league_name, settings=first_season_data.get("settings")
            )
            db.add(league)
            db.flush()  # Flush to get league.id

        # Create Season
        season_year = first_season_data["seasonId"]
        season = (
            db.query(Season)
            .filter(Season.league_id == league.id, Season.year == season_year)
            .first()
        )
        if not season:
            season = Season(league_id=league.id, year=season_year)
            db.add(season)
            db.flush()  # Flush to get season.id

        # Create or get Managers from members
        managers_by_espn_id: dict[str, Manager] = {}
        for member in first_season_data.get("members", []):
            espn_id = member["id"]
            display_name = member["displayName"]

            # Check if manager already exists by name
            manager = db.query(Manager).filter(Manager.name == display_name).first()
            if not manager:
                manager = Manager(name=display_name)
                db.add(manager)
                db.flush()  # Flush to get manager.id

            managers_by_espn_id[espn_id] = manager

        # Create or get Franchises from teams
        franchises: list[Franchise] = []
        franchise_seasons: list[FranchiseSeason] = []

        for team_data in first_season_data.get("teams", []):
            abbrev = team_data["abbrev"]
            owner_ids = team_data.get("owners", [])

            # Find or create franchise by abbreviation
            franchise = (
                db.query(Franchise)
                .filter(Franchise.league_id == league.id, Franchise.name == abbrev)
                .first()
            )
            if not franchise:
                franchise = Franchise(league_id=league.id, name=abbrev)
                db.add(franchise)
                db.flush()  # Flush to get franchise.id

            franchises.append(franchise)

            # Get manager for this franchise (first owner)
            manager = None
            if owner_ids:
                owner_espn_id = owner_ids[0]
                manager = managers_by_espn_id.get(owner_espn_id)

            if manager:
                # Create FranchiseSeason linking franchise, season, and manager
                franchise_season = (
                    db.query(FranchiseSeason)
                    .filter(
                        FranchiseSeason.franchise_id == franchise.id,
                        FranchiseSeason.season_id == season.id,
                    )
                    .first()
                )
                if not franchise_season:
                    franchise_season = FranchiseSeason(
                        franchise_id=franchise.id,
                        season_id=season.id,
                        manager_id=manager.id,
                    )
                    db.add(franchise_season)
                    db.flush()  # Flush to get franchise_season.id

                franchise_seasons.append(franchise_season)

        # Commit all changes
        db.commit()

        return {
            "league": league,
            "season": season,
            "franchises": franchises,
            "managers": list(managers_by_espn_id.values()),
            "franchise_seasons": franchise_seasons,
        }
