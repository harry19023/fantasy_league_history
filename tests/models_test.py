"""Tests for database models."""

import pytest
from sqlalchemy.orm import Session

from app.models import (
    Franchise,
    FranchiseSeason,
    Game,
    League,
    Lineup,
    Manager,
    Player,
    Season,
)


def test_models_import():
    """Test that models can be imported."""
    assert True


@pytest.fixture
def sample_league(db_session: Session) -> League:
    """Create a sample league."""
    league = League(name="Test League", settings={"scoring": "PPR"})
    db_session.add(league)
    db_session.commit()
    db_session.refresh(league)
    return league


@pytest.fixture
def sample_manager(db_session: Session) -> Manager:
    """Create a sample manager."""
    manager = Manager(name="John Doe")
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)
    return manager


@pytest.fixture
def sample_season(db_session: Session, sample_league: League) -> Season:
    """Create a sample season."""
    season = Season(league_id=sample_league.id, year=2024)
    db_session.add(season)
    db_session.commit()
    db_session.refresh(season)
    return season


@pytest.fixture
def sample_franchise(db_session: Session, sample_league: League) -> Franchise:
    """Create a sample franchise."""
    franchise = Franchise(league_id=sample_league.id, name="The Warriors")
    db_session.add(franchise)
    db_session.commit()
    db_session.refresh(franchise)
    return franchise


@pytest.fixture
def sample_player(db_session: Session) -> Player:
    """Create a sample player."""
    player = Player(name="Patrick Mahomes", position="QB", nfl_team="KC")
    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)
    return player


@pytest.fixture
def sample_game(
    db_session: Session, sample_season: Season, sample_franchise: Franchise
) -> Game:
    """Create a sample game."""
    franchise2 = Franchise(league_id=sample_franchise.league_id, name="The Rivals")
    db_session.add(franchise2)
    db_session.commit()

    game = Game(
        season_id=sample_season.id,
        week=1,
        game_type="REGULAR",
        franchise1_id=sample_franchise.id,
        franchise2_id=franchise2.id,
        franchise1_score=120.5,
        franchise2_score=98.3,
    )
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)
    return game


class LeagueTest:
    """Tests for League model."""

    def test_create_league(self, db_session: Session):
        """Test creating a league."""
        league = League(name="My League", settings={"draft_date": "2024-08-01"})
        db_session.add(league)
        db_session.commit()

        assert league.id is not None
        assert league.name == "My League"
        assert league.settings == {"draft_date": "2024-08-01"}

    def test_league_has_seasons(self, db_session: Session, sample_league: League):
        """Test league-seasons relationship."""
        season1 = Season(league_id=sample_league.id, year=2024)
        season2 = Season(league_id=sample_league.id, year=2023)
        db_session.add_all([season1, season2])
        db_session.commit()

        assert len(sample_league.seasons) == 2
        assert {s.year for s in sample_league.seasons} == {2024, 2023}

    def test_league_has_franchises(self, db_session: Session, sample_league: League):
        """Test league-franchises relationship."""
        franchise1 = Franchise(league_id=sample_league.id, name="Team 1")
        franchise2 = Franchise(league_id=sample_league.id, name="Team 2")
        db_session.add_all([franchise1, franchise2])
        db_session.commit()

        assert len(sample_league.franchises) == 2
        assert {f.name for f in sample_league.franchises} == {"Team 1", "Team 2"}


class ManagerTest:
    """Tests for Manager model."""

    def test_create_manager(self, db_session: Session):
        """Test creating a manager."""
        manager = Manager(name="Jane Smith")
        db_session.add(manager)
        db_session.commit()

        assert manager.id is not None
        assert manager.name == "Jane Smith"


class SeasonTest:
    """Tests for Season model."""

    def test_create_season(self, db_session: Session, sample_league: League):
        """Test creating a season."""
        season = Season(
            league_id=sample_league.id,
            year=2024,
            start_date=None,
            end_date=None,
        )
        db_session.add(season)
        db_session.commit()

        assert season.id is not None
        assert season.year == 2024
        assert season.league_id == sample_league.id

    def test_unique_league_year(self, db_session: Session, sample_league: League):
        """Test that same year cannot be used twice for same league."""
        season1 = Season(league_id=sample_league.id, year=2024)
        db_session.add(season1)
        db_session.commit()

        season2 = Season(league_id=sample_league.id, year=2024)
        db_session.add(season2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
        db_session.rollback()


class FranchiseTest:
    """Tests for Franchise model."""

    def test_create_franchise(self, db_session: Session, sample_league: League):
        """Test creating a franchise."""
        franchise = Franchise(league_id=sample_league.id, name="The Warriors")
        db_session.add(franchise)
        db_session.commit()

        assert franchise.id is not None
        assert franchise.name == "The Warriors"
        assert franchise.league_id == sample_league.id


class FranchiseSeasonTest:
    """Tests for FranchiseSeason model."""

    def test_create_franchise_season(
        self,
        db_session: Session,
        sample_franchise: Franchise,
        sample_season: Season,
        sample_manager: Manager,
    ):
        """Test creating a franchise season."""
        fs = FranchiseSeason(
            franchise_id=sample_franchise.id,
            season_id=sample_season.id,
            manager_id=sample_manager.id,
            regular_wins=10,
            regular_losses=4,
            playoff_winners_wins=2,
            playoff_winners_losses=1,
            final_standing=1,
            won_championship=True,
            prize_money=500.0,
        )
        db_session.add(fs)
        db_session.commit()

        assert fs.id is not None
        assert fs.regular_wins == 10
        assert fs.regular_losses == 4
        assert fs.playoff_winners_wins == 2
        assert fs.won_championship is True
        assert fs.prize_money == 500.0

    def test_unique_franchise_season(
        self,
        db_session: Session,
        sample_franchise: Franchise,
        sample_season: Season,
        sample_manager: Manager,
    ):
        """Test that same franchise-season combination is unique."""
        fs1 = FranchiseSeason(
            franchise_id=sample_franchise.id,
            season_id=sample_season.id,
            manager_id=sample_manager.id,
        )
        db_session.add(fs1)
        db_session.commit()

        fs2 = FranchiseSeason(
            franchise_id=sample_franchise.id,
            season_id=sample_season.id,
            manager_id=sample_manager.id,
        )
        db_session.add(fs2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
        db_session.rollback()

    def test_franchise_season_relationships(
        self,
        db_session: Session,
        sample_franchise: Franchise,
        sample_season: Season,
        sample_manager: Manager,
    ):
        """Test FranchiseSeason relationships."""
        fs = FranchiseSeason(
            franchise_id=sample_franchise.id,
            season_id=sample_season.id,
            manager_id=sample_manager.id,
        )
        db_session.add(fs)
        db_session.commit()

        assert fs.franchise.id == sample_franchise.id
        assert fs.season.id == sample_season.id
        assert fs.manager.id == sample_manager.id


class GameTest:
    """Tests for Game model."""

    def test_create_regular_game(
        self,
        db_session: Session,
        sample_season: Season,
        sample_franchise: Franchise,
    ):
        """Test creating a regular season game."""
        franchise2 = Franchise(league_id=sample_franchise.league_id, name="The Rivals")
        db_session.add(franchise2)
        db_session.commit()

        game = Game(
            season_id=sample_season.id,
            week=1,
            game_type="REGULAR",
            franchise1_id=sample_franchise.id,
            franchise2_id=franchise2.id,
            franchise1_score=120.5,
            franchise2_score=98.3,
        )
        db_session.add(game)
        db_session.commit()

        assert game.id is not None
        assert game.game_type == "REGULAR"
        assert game.franchise1_score == 120.5
        assert game.franchise2_score == 98.3

    def test_create_playoff_game(
        self,
        db_session: Session,
        sample_season: Season,
        sample_franchise: Franchise,
    ):
        """Test creating a playoff game."""
        franchise2 = Franchise(league_id=sample_franchise.league_id, name="The Rivals")
        db_session.add(franchise2)
        db_session.commit()

        game = Game(
            season_id=sample_season.id,
            week=15,
            game_type="PLAYOFF_WINNERS",
            franchise1_id=sample_franchise.id,
            franchise2_id=franchise2.id,
            franchise1_score=150.0,
            franchise2_score=145.5,
        )
        db_session.add(game)
        db_session.commit()

        assert game.game_type == "PLAYOFF_WINNERS"
        assert game.week == 15


class PlayerTest:
    """Tests for Player model."""

    def test_create_player(self, db_session: Session):
        """Test creating a player."""
        player = Player(name="Travis Kelce", position="TE", nfl_team="KC")
        db_session.add(player)
        db_session.commit()

        assert player.id is not None
        assert player.name == "Travis Kelce"
        assert player.position == "TE"
        assert player.nfl_team == "KC"


class LineupTest:
    """Tests for Lineup model."""

    def test_create_lineup(
        self,
        db_session: Session,
        sample_game: Game,
        sample_franchise: Franchise,
        sample_player: Player,
    ):
        """Test creating a lineup entry."""
        lineup = Lineup(
            game_id=sample_game.id,
            franchise_id=sample_franchise.id,
            player_id=sample_player.id,
            score=25.5,
            position="QB",
        )
        db_session.add(lineup)
        db_session.commit()

        assert lineup.id is not None
        assert lineup.score == 25.5
        assert lineup.position == "QB"

    def test_create_bench_lineup(
        self,
        db_session: Session,
        sample_game: Game,
        sample_franchise: Franchise,
        sample_player: Player,
    ):
        """Test creating a bench lineup entry."""
        lineup = Lineup(
            game_id=sample_game.id,
            franchise_id=sample_franchise.id,
            player_id=sample_player.id,
            score=18.0,
            position="BENCH",
        )
        db_session.add(lineup)
        db_session.commit()

        assert lineup.position == "BENCH"

    def test_unique_lineup_entry(
        self,
        db_session: Session,
        sample_game: Game,
        sample_franchise: Franchise,
        sample_player: Player,
    ):
        """Test that same player cannot be in lineup twice for same game/franchise."""
        lineup1 = Lineup(
            game_id=sample_game.id,
            franchise_id=sample_franchise.id,
            player_id=sample_player.id,
            score=25.5,
        )
        db_session.add(lineup1)
        db_session.commit()

        lineup2 = Lineup(
            game_id=sample_game.id,
            franchise_id=sample_franchise.id,
            player_id=sample_player.id,
            score=30.0,
        )
        db_session.add(lineup2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
        db_session.rollback()
