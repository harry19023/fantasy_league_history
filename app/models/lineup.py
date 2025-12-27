from sqlalchemy import Column, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Lineup(Base):
    __tablename__ = "lineup"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    franchise_id = Column(Integer, ForeignKey("franchise.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    score = Column(Float, nullable=True)
    position = Column(
        String, nullable=True
    )  # "QB", "RB", "WR", "TE", "K", "DEF", "BENCH", etc.

    # Relationships
    game = relationship("Game", backref="lineups")
    franchise = relationship("Franchise", backref="lineups")
    player = relationship("Player", backref="lineups")

    # Ensure unique player per game per franchise
    __table_args__ = (
        UniqueConstraint(
            "game_id", "franchise_id", "player_id", name="unique_game_franchise_player"
        ),
    )
