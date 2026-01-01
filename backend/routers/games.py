from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import get_db, Game, Season, Pick
from routers.auth import verify_token

router = APIRouter(prefix="/games", tags=["games"])


class GameCreate(BaseModel):
    bowl_name: str
    home_team: str
    away_team: str
    spread: Optional[float] = None
    over_under: Optional[float] = None
    game_time: Optional[datetime] = None
    is_playoff: bool = False


class GameUpdate(BaseModel):
    bowl_name: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    spread: Optional[float] = None
    over_under: Optional[float] = None
    game_time: Optional[datetime] = None
    winner: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None


class GameResponse(BaseModel):
    id: int
    bowl_name: str
    home_team: str
    away_team: str
    spread: Optional[float]
    over_under: Optional[float]
    game_time: Optional[datetime]
    winner: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]
    is_playoff: bool
    is_locked: bool

    class Config:
        from_attributes = True


def get_active_season(db: Session) -> Season:
    """Get the current active season."""
    season = db.query(Season).filter(Season.is_active == True).first()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active season found"
        )
    return season


@router.get("/", response_model=List[GameResponse])
async def get_games(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Get all games for the current season."""
    season = get_active_season(db)
    games = db.query(Game).filter(Game.season_id == season.id).order_by(Game.game_time).all()

    result = []
    now = datetime.utcnow()
    for game in games:
        game_dict = {
            "id": game.id,
            "bowl_name": game.bowl_name,
            "home_team": game.home_team,
            "away_team": game.away_team,
            "spread": game.spread,
            "over_under": game.over_under,
            "game_time": game.game_time,
            "winner": game.winner,
            "home_score": game.home_score,
            "away_score": game.away_score,
            "is_playoff": game.is_playoff,
            "is_locked": game.game_time is not None and game.game_time <= now
        }
        result.append(GameResponse(**game_dict))

    return result


@router.post("/", response_model=GameResponse)
async def create_game(
    game: GameCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Create a new game."""
    season = get_active_season(db)

    db_game = Game(
        season_id=season.id,
        bowl_name=game.bowl_name,
        home_team=game.home_team,
        away_team=game.away_team,
        spread=game.spread,
        over_under=game.over_under,
        game_time=game.game_time,
        is_playoff=game.is_playoff
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)

    now = datetime.utcnow()
    return GameResponse(
        id=db_game.id,
        bowl_name=db_game.bowl_name,
        home_team=db_game.home_team,
        away_team=db_game.away_team,
        spread=db_game.spread,
        over_under=db_game.over_under,
        game_time=db_game.game_time,
        winner=db_game.winner,
        home_score=db_game.home_score,
        away_score=db_game.away_score,
        is_playoff=db_game.is_playoff,
        is_locked=db_game.game_time is not None and db_game.game_time <= now
    )


@router.put("/{game_id}", response_model=GameResponse)
async def update_game(
    game_id: int,
    game_update: GameUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Update a game (set winner, scores, etc.)."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    update_data = game_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(game, field, value)

    # If winner is set, update all picks for this game
    if game_update.winner:
        picks = db.query(Pick).filter(Pick.game_id == game_id).all()
        for pick in picks:
            pick.is_correct = pick.picked_team == game_update.winner
            pick.is_locked = True

    db.commit()
    db.refresh(game)

    now = datetime.utcnow()
    return GameResponse(
        id=game.id,
        bowl_name=game.bowl_name,
        home_team=game.home_team,
        away_team=game.away_team,
        spread=game.spread,
        over_under=game.over_under,
        game_time=game.game_time,
        winner=game.winner,
        home_score=game.home_score,
        away_score=game.away_score,
        is_playoff=game.is_playoff,
        is_locked=game.game_time is not None and game.game_time <= now
    )


@router.delete("/{game_id}")
async def delete_game(
    game_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Delete a game."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    # Delete associated picks first
    db.query(Pick).filter(Pick.game_id == game_id).delete()
    db.delete(game)
    db.commit()

    return {"message": "Game deleted"}
