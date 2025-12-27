"""Tests for complex queries from schema proposal."""

import pytest
from sqlalchemy.orm import Session

from app.models import Franchise, Game, League, Lineup, Player, Season


@pytest.fixture
def db_session():
    """Get database session."""
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_data(db_session: Session):
    """Create sample data for query tests."""
    # Create league
    league = League(name="Test League")
    db_session.add(league)
    db_session.commit()

    # Create franchises
    franchise1 = Franchise(league_id=league.id, name="The Warriors")
    franchise2 = Franchise(league_id=league.id, name="The Rivals")
    db_session.add_all([franchise1, franchise2])
    db_session.commit()

    # Create seasons
    season2023 = Season(league_id=league.id, year=2023)
    season2024 = Season(league_id=league.id, year=2024)
    db_session.add_all([season2023, season2024])
    db_session.commit()

    # Create players
    player1 = Player(name="Patrick Mahomes", position="QB", nfl_team="KC")
    player2 = Player(name="Travis Kelce", position="TE", nfl_team="KC")
    db_session.add_all([player1, player2])
    db_session.commit()

    # Create games
    game1 = Game(
        season_id=season2024.id,
        week=1,
        game_type="REGULAR",
        franchise1_id=franchise1.id,
        franchise2_id=franchise2.id,
        franchise1_score=120.5,
        franchise2_score=98.3,
    )
    game2 = Game(
        season_id=season2024.id,
        week=2,
        game_type="REGULAR",
        franchise1_id=franchise1.id,
        franchise2_id=franchise2.id,
        franchise1_score=110.0,
        franchise2_score=115.5,
    )
    game3 = Game(
        season_id=season2024.id,
        week=15,
        game_type="PLAYOFF_WINNERS",
        franchise1_id=franchise1.id,
        franchise2_id=franchise2.id,
        franchise1_score=150.0,
        franchise2_score=145.5,
    )
    db_session.add_all([game1, game2, game3])
    db_session.commit()

    # Create lineups
    lineup1 = Lineup(
        game_id=game1.id,
        franchise_id=franchise1.id,
        player_id=player1.id,
        score=25.5,
        position="QB",
    )
    lineup2 = Lineup(
        game_id=game2.id,
        franchise_id=franchise1.id,
        player_id=player1.id,
        score=22.0,
        position="QB",
    )
    lineup3 = Lineup(
        game_id=game1.id,
        franchise_id=franchise1.id,
        player_id=player2.id,
        score=18.0,
        position="TE",
    )
    lineup4 = Lineup(
        game_id=game3.id,
        franchise_id=franchise1.id,
        player_id=player1.id,
        score=30.0,
        position="QB",
    )
    db_session.add_all([lineup1, lineup2, lineup3, lineup4])
    db_session.commit()

    return {
        "league": league,
        "franchise1": franchise1,
        "franchise2": franchise2,
        "season2023": season2023,
        "season2024": season2024,
        "player1": player1,
        "player2": player2,
        "game1": game1,
        "game2": game2,
        "game3": game3,
    }


class PlayerHistoryQueriesTest:
    """Test queries for player history by franchise."""

    def test_which_franchises_player_been_on(
        self, db_session: Session, sample_data: dict
    ):
        """Test query: Which franchises has a player been on?"""
        player = sample_data["player1"]
        franchise1 = sample_data["franchise1"]

        # Query: distinct franchises player has been on
        lineups = db_session.query(Lineup).filter(Lineup.player_id == player.id).all()
        franchise_ids = {lineup.franchise_id for lineup in lineups}
        franchises = (
            db_session.query(Franchise).filter(Franchise.id.in_(franchise_ids)).all()
        )

        assert len(franchises) == 1
        assert franchises[0].id == franchise1.id
        assert franchises[0].name == "The Warriors"

    def test_player_total_points_per_franchise(
        self, db_session: Session, sample_data: dict
    ):
        """Test query: Total points scored by player per franchise."""
        player = sample_data["player1"]
        franchise1 = sample_data["franchise1"]

        # Query: sum of scores grouped by franchise
        from sqlalchemy import func

        result = (
            db_session.query(
                Franchise.id,
                Franchise.name,
                func.sum(Lineup.score).label("total_points"),
                func.count(Lineup.id).label("games_played"),
            )
            .join(Lineup, Franchise.id == Lineup.franchise_id)
            .filter(Lineup.player_id == player.id)
            .group_by(Franchise.id, Franchise.name)
            .all()
        )

        assert len(result) == 1
        assert result[0].id == franchise1.id
        assert result[0].total_points == 77.5  # 25.5 + 22.0 + 30.0
        assert result[0].games_played == 3

    def test_player_wins_per_franchise(self, db_session: Session, sample_data: dict):
        """Test query: How many games did a player win for each franchise?"""
        player = sample_data["player1"]
        franchise1 = sample_data["franchise1"]

        # Query: count wins where player's franchise won
        from sqlalchemy import func

        wins = (
            db_session.query(
                Franchise.id,
                Franchise.name,
                func.count(Lineup.id).label("wins"),
            )
            .join(Lineup, Franchise.id == Lineup.franchise_id)
            .join(Game, Lineup.game_id == Game.id)
            .filter(Lineup.player_id == player.id)
            .filter(
                (
                    (Lineup.franchise_id == Game.franchise1_id)
                    & (Game.franchise1_score > Game.franchise2_score)
                )
                | (
                    (Lineup.franchise_id == Game.franchise2_id)
                    & (Game.franchise2_score > Game.franchise1_score)
                )
            )
            .group_by(Franchise.id, Franchise.name)
            .all()
        )

        assert len(wins) == 1
        assert wins[0].id == franchise1.id
        # Player was in 3 games, franchise won 2 (game1 and game3)
        assert wins[0].wins == 2

    def test_player_stats_per_franchise_per_season(
        self, db_session: Session, sample_data: dict
    ):
        """Test query: Player stats per franchise per season."""
        player = sample_data["player1"]

        from sqlalchemy import case, func

        stats = (
            db_session.query(
                Franchise.name.label("franchise"),
                Season.year.label("season"),
                func.count(Lineup.id).label("weeks_on_roster"),
                func.count(case((Lineup.position != "BENCH", 1))).label(
                    "games_started"
                ),
                func.count(case((Lineup.position == "BENCH", 1))).label(
                    "weeks_on_bench"
                ),
                func.sum(Lineup.score).label("total_points"),
                func.avg(Lineup.score).label("avg_points"),
            )
            .join(Lineup, Franchise.id == Lineup.franchise_id)
            .join(Game, Lineup.game_id == Game.id)
            .join(Season, Game.season_id == Season.id)
            .filter(Lineup.player_id == player.id)
            .group_by(Franchise.id, Franchise.name, Season.id, Season.year)
            .all()
        )

        assert len(stats) == 1
        assert stats[0].franchise == "The Warriors"
        assert stats[0].season == 2024
        assert stats[0].weeks_on_roster == 3
        assert stats[0].games_started == 3  # All were starters
        assert stats[0].weeks_on_bench == 0
        assert stats[0].total_points == 77.5
        assert stats[0].avg_points == pytest.approx(25.83, rel=0.01)


class PlayoffQueriesTest:
    """Test queries for playoff tracking."""

    def test_regular_vs_playoff_wins(self, db_session: Session, sample_data: dict):
        """Test query: Regular season wins vs playoff wins."""
        player = sample_data["player1"]

        from sqlalchemy import case, func

        wins_by_type = (
            db_session.query(
                Franchise.name,
                func.count(
                    case(
                        (
                            (Game.game_type == "REGULAR")
                            & (
                                (
                                    (Lineup.franchise_id == Game.franchise1_id)
                                    & (Game.franchise1_score > Game.franchise2_score)
                                )
                                | (
                                    (Lineup.franchise_id == Game.franchise2_id)
                                    & (Game.franchise2_score > Game.franchise1_score)
                                )
                            ),
                            1,
                        )
                    )
                ).label("regular_wins"),
                func.count(
                    case(
                        (
                            (Game.game_type.in_(["PLAYOFF_WINNERS", "PLAYOFF_LOSERS"]))
                            & (
                                (
                                    (Lineup.franchise_id == Game.franchise1_id)
                                    & (Game.franchise1_score > Game.franchise2_score)
                                )
                                | (
                                    (Lineup.franchise_id == Game.franchise2_id)
                                    & (Game.franchise2_score > Game.franchise1_score)
                                )
                            ),
                            1,
                        )
                    )
                ).label("playoff_wins"),
            )
            .join(Lineup, Franchise.id == Lineup.franchise_id)
            .join(Game, Lineup.game_id == Game.id)
            .filter(Lineup.player_id == player.id)
            .group_by(Franchise.id, Franchise.name)
            .all()
        )

        assert len(wins_by_type) == 1
        assert wins_by_type[0].regular_wins == 1  # Won game1
        assert wins_by_type[0].playoff_wins == 1  # Won game3
