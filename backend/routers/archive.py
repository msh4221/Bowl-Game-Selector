from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import json
from datetime import datetime

from database import get_db, Game, User, Pick, Season, ArchivedSeason
from routers.auth import verify_token

router = APIRouter(prefix="/archive", tags=["archive"])


class ArchivedSeasonSummary(BaseModel):
    id: int
    year: str
    created_at: datetime


class ArchivedSeasonDetail(BaseModel):
    id: int
    year: str
    games: list
    standings: list
    created_at: datetime


@router.get("/", response_model=List[ArchivedSeasonSummary])
async def get_archived_seasons(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Get list of all archived seasons."""
    archives = db.query(ArchivedSeason).order_by(ArchivedSeason.year.desc()).all()
    return [
        ArchivedSeasonSummary(
            id=a.id,
            year=a.year,
            created_at=a.created_at
        )
        for a in archives
    ]


@router.get("/{year}", response_model=ArchivedSeasonDetail)
async def get_archived_season(
    year: str,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Get details of a specific archived season."""
    archive = db.query(ArchivedSeason).filter(ArchivedSeason.year == year).first()
    if not archive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No archived data for season {year}"
        )

    return ArchivedSeasonDetail(
        id=archive.id,
        year=archive.year,
        games=json.loads(archive.results_json),
        standings=json.loads(archive.final_standings),
        created_at=archive.created_at
    )


@router.post("/create")
async def archive_current_season(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Archive the current season and create a new one."""
    # Get active season
    season = db.query(Season).filter(Season.is_active == True).first()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active season to archive"
        )

    # Check if already archived
    existing = db.query(ArchivedSeason).filter(ArchivedSeason.year == season.year).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Season {season.year} is already archived"
        )

    # Get all games with picks
    games = db.query(Game).filter(Game.season_id == season.id).all()
    users = db.query(User).all()

    # Build results JSON
    games_data = []
    for game in games:
        game_picks = {}
        for pick in game.picks:
            user = db.query(User).filter(User.id == pick.user_id).first()
            game_picks[user.name] = {
                "picked_team": pick.picked_team,
                "is_correct": pick.is_correct
            }

        games_data.append({
            "bowl_name": game.bowl_name,
            "home_team": game.home_team,
            "away_team": game.away_team,
            "spread": game.spread,
            "winner": game.winner,
            "home_score": game.home_score,
            "away_score": game.away_score,
            "picks": game_picks
        })

    # Build standings
    standings = []
    for user in users:
        picks = (
            db.query(Pick)
            .join(Game)
            .filter(
                Pick.user_id == user.id,
                Game.season_id == season.id
            )
            .all()
        )
        correct = sum(1 for p in picks if p.is_correct is True)
        total = len(picks)

        standings.append({
            "user_name": user.name,
            "correct_picks": correct,
            "total_picks": total
        })

    standings.sort(key=lambda x: x["correct_picks"], reverse=True)

    # Create archive
    archive = ArchivedSeason(
        year=season.year,
        results_json=json.dumps(games_data),
        final_standings=json.dumps(standings)
    )
    db.add(archive)

    # Mark season as inactive
    season.is_active = False

    # Calculate next season year
    current_year = int(season.year.split("-")[0])
    next_year = f"{current_year + 1}-{str(current_year + 2)[-2:]}"

    # Create new season
    new_season = Season(year=next_year, is_active=True)
    db.add(new_season)

    db.commit()

    return {
        "message": f"Season {season.year} archived successfully",
        "new_season": next_year
    }


@router.get("/seasons/all")
async def get_all_seasons(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Get list of all seasons (active and archived)."""
    seasons = db.query(Season).order_by(Season.year.desc()).all()
    archived = db.query(ArchivedSeason).all()
    archived_years = {a.year for a in archived}

    return [
        {
            "year": s.year,
            "is_active": s.is_active,
            "is_archived": s.year in archived_years
        }
        for s in seasons
    ]
