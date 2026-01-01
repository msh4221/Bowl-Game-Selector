from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import get_db, Game, User, Pick, Season

from routers.auth import verify_token

router = APIRouter(prefix="/picks", tags=["picks"])


class PickCreate(BaseModel):
    game_id: int
    user_name: str
    picked_team: str


class PickResponse(BaseModel):
    id: int
    game_id: int
    user_name: str
    picked_team: str
    is_locked: bool
    is_correct: Optional[bool]

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    user_name: str
    correct_picks: int
    total_picks: int
    pending_picks: int


@router.get("/users")
async def get_users(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Get all family members."""
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name} for u in users]


@router.get("/", response_model=List[PickResponse])
async def get_picks(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Get all picks for the current season."""
    season = db.query(Season).filter(Season.is_active == True).first()
    if not season:
        return []

    picks = (
        db.query(Pick)
        .join(Game)
        .join(User)
        .filter(Game.season_id == season.id)
        .all()
    )

    now = datetime.utcnow()
    result = []
    for pick in picks:
        game_locked = pick.game.game_time is not None and pick.game.game_time <= now
        result.append(PickResponse(
            id=pick.id,
            game_id=pick.game_id,
            user_name=pick.user.name,
            picked_team=pick.picked_team,
            is_locked=pick.is_locked or game_locked,
            is_correct=pick.is_correct
        ))

    return result


@router.post("/", response_model=PickResponse)
async def create_or_update_pick(
    pick_data: PickCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Create or update a pick for a user."""
    # Get user
    user = db.query(User).filter(User.name == pick_data.user_name).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{pick_data.user_name}' not found"
        )

    # Get game
    game = db.query(Game).filter(Game.id == pick_data.game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    # Check if game is locked
    now = datetime.utcnow()
    if game.game_time and game.game_time <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game has already started, picks are locked"
        )

    # Validate picked team
    if pick_data.picked_team not in [game.home_team, game.away_team]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid team. Must be '{game.home_team}' or '{game.away_team}'"
        )

    # Check for existing pick
    existing_pick = db.query(Pick).filter(
        Pick.user_id == user.id,
        Pick.game_id == game.id
    ).first()

    if existing_pick:
        if existing_pick.is_locked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pick is already locked"
            )
        existing_pick.picked_team = pick_data.picked_team
        existing_pick.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_pick)
        pick = existing_pick
    else:
        pick = Pick(
            user_id=user.id,
            game_id=game.id,
            picked_team=pick_data.picked_team
        )
        db.add(pick)
        db.commit()
        db.refresh(pick)

    return PickResponse(
        id=pick.id,
        game_id=pick.game_id,
        user_name=user.name,
        picked_team=pick.picked_team,
        is_locked=pick.is_locked,
        is_correct=pick.is_correct
    )


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Get the current leaderboard."""
    season = db.query(Season).filter(Season.is_active == True).first()
    if not season:
        return []

    users = db.query(User).all()
    leaderboard = []

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
        pending = sum(1 for p in picks if p.is_correct is None)

        leaderboard.append(LeaderboardEntry(
            user_name=user.name,
            correct_picks=correct,
            total_picks=total,
            pending_picks=pending
        ))

    # Sort by correct picks descending
    leaderboard.sort(key=lambda x: x.correct_picks, reverse=True)

    return leaderboard
