from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class FranchiseSeason(Base):
    __tablename__ = "franchise_seasons"

    id = Column(Integer, primary_key=True, index=True)
    franchise_id = Column(Integer, ForeignKey("franchises.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("managers.id"), nullable=False)

    # Regular season stats
    regular_wins = Column(Integer, default=0, nullable=False)
    regular_losses = Column(Integer, default=0, nullable=False)

    # Playoff stats - winners bracket
    playoff_winners_wins = Column(Integer, default=0, nullable=False)
    playoff_winners_losses = Column(Integer, default=0, nullable=False)

    # Playoff stats - losers bracket
    playoff_losers_wins = Column(Integer, default=0, nullable=False)
    playoff_losers_losses = Column(Integer, default=0, nullable=False)

    # Total points
    points_for = Column(Float, default=0.0, nullable=False)
    points_against = Column(Float, default=0.0, nullable=False)

    # Final standings and prizes
    final_standing = Column(Integer, nullable=True)
    prize_money = Column(Float, default=0.0, nullable=False)
    won_championship = Column(Boolean, default=False, nullable=False)
    won_draft_lottery = Column(Boolean, default=False, nullable=False)
    lost_beer_mile = Column(Boolean, default=False, nullable=False)

    # Relationships
    franchise = relationship("Franchise", backref="franchise_seasons")
    season = relationship("Season", backref="franchise_seasons")
    manager = relationship("Manager", backref="franchise_seasons")

    # Ensure unique franchise per season
    __table_args__ = (
        UniqueConstraint("franchise_id", "season_id", name="unique_franchise_season"),
    )
