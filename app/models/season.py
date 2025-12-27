from sqlalchemy import Column, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Season(Base):
    __tablename__ = "season"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("league.id"), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    # Relationships
    league = relationship("League", backref="seasons")

    # Ensure unique year per league
    __table_args__ = (UniqueConstraint("league_id", "year", name="unique_league_year"),)
