"""Script to import ESPN league data into the database."""

import argparse
import sys

from app.database import SessionLocal
from app.services.espn_importer import ESPNImporter


def main():
    """Import ESPN league data."""
    parser = argparse.ArgumentParser(
        description="Import ESPN league data into database"
    )
    parser.add_argument(
        "--league-id",
        type=int,
        required=True,
        help="ESPN league ID",
    )
    parser.add_argument(
        "--scoring-period-id",
        type=int,
        default=None,
        help="Scoring period ID (optional)",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        importer = ESPNImporter()
        result = importer.import_league_first_season(
            db, args.league_id, args.scoring_period_id
        )

        print(f"✅ Successfully imported league: {result['league'].name}")
        print(f"   Season: {result['season'].year}")
        print(f"   Franchises: {len(result['franchises'])}")
        print(f"   Managers: {len(result['managers'])}")
        print(f"   Franchise Seasons: {len(result['franchise_seasons'])}")

        print("\nFranchises:")
        for franchise in result["franchises"]:
            print(f"  - {franchise.name} (ID: {franchise.id})")

        print("\nManagers:")
        for manager in result["managers"]:
            print(f"  - {manager.name} (ID: {manager.id})")

        print("\nFranchise Seasons:")
        for fs in result["franchise_seasons"]:
            franchise = fs.franchise
            manager = fs.manager
            print(f"  - {franchise.name} -> {manager.name}")

    except Exception as e:
        print(f"❌ Error importing league: {e}", file=sys.stderr)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
