from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("league.id"), nullable=False)
    name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)

    # Relationships
    league = relationship("League", backref="teams")
