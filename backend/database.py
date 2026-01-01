from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bowlpicks.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String(10), unique=True, index=True)  # e.g., "2024-25"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    games = relationship("Game", back_populates="season")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    picks = relationship("Pick", back_populates="user")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    bowl_name = Column(String(100))
    home_team = Column(String(100))
    away_team = Column(String(100))
    spread = Column(Float, nullable=True)  # Negative = home favored
    over_under = Column(Float, nullable=True)
    game_time = Column(DateTime, nullable=True)
    winner = Column(String(100), nullable=True)  # Actual winner
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    is_playoff = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    season = relationship("Season", back_populates="games")
    picks = relationship("Pick", back_populates="game")


class Pick(Base):
    __tablename__ = "picks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_id = Column(Integer, ForeignKey("games.id"))
    picked_team = Column(String(100))
    is_locked = Column(Boolean, default=False)
    is_correct = Column(Boolean, nullable=True)  # Set when game ends
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="picks")
    game = relationship("Game", back_populates="picks")


class ArchivedSeason(Base):
    __tablename__ = "archived_seasons"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String(10), index=True)
    results_json = Column(Text)  # JSON blob of full season results
    final_standings = Column(Text)  # JSON blob of final leaderboard
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables and seed initial data."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if users already exist
        if db.query(User).count() == 0:
            # Seed family members
            family_members = [
                "John", "Jean", "Emily", "Sarah",
                "Matt", "Billy", "Papa Jack", "Coconut"
            ]
            for name in family_members:
                db.add(User(name=name))
            db.commit()
            print("Seeded family members")

        # Check if current season exists
        current_season = "2024-25"
        if db.query(Season).filter(Season.year == current_season).count() == 0:
            db.add(Season(year=current_season, is_active=True))
            db.commit()
            print(f"Created season {current_season}")
    finally:
        db.close()


def get_db():
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
