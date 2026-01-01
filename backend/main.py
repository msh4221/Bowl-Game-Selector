from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database import init_db, get_db, Game, Season
from routers import auth, games, picks, archive
from routers.auth import verify_token
from services.ncaa_api import get_ncaa_service
from services.odds_api import get_odds_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("Database initialized")
    yield
    # Shutdown
    ncaa = await get_ncaa_service()
    odds = await get_odds_service()
    await ncaa.close()
    await odds.close()


app = FastAPI(
    title="Annual Bowl Picks",
    description="Family bowl game prediction tracker",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(games.router)
app.include_router(picks.router)
app.include_router(archive.router)


@app.get("/")
async def root():
    return {"message": "Annual Bowl Picks API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/admin/import-games")
async def import_games_from_ncaa(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Import bowl games from NCAA API."""
    ncaa = await get_ncaa_service()
    games_data = await ncaa.get_bowl_games()

    if not games_data:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch games from NCAA API"
        )

    # Get active season
    season = db.query(Season).filter(Season.is_active == True).first()
    if not season:
        raise HTTPException(
            status_code=404,
            detail="No active season found"
        )

    imported = 0
    for game_data in games_data:
        # Check if game already exists
        existing = db.query(Game).filter(
            Game.season_id == season.id,
            Game.home_team == game_data["home_team"],
            Game.away_team == game_data["away_team"]
        ).first()

        if not existing:
            game = Game(
                season_id=season.id,
                bowl_name=game_data["bowl_name"],
                home_team=game_data["home_team"],
                away_team=game_data["away_team"],
                game_time=game_data.get("game_time"),
                is_playoff=game_data.get("is_playoff", False),
                winner=game_data.get("winner"),
                home_score=game_data.get("home_score"),
                away_score=game_data.get("away_score")
            )
            db.add(game)
            imported += 1

    db.commit()

    return {"message": f"Imported {imported} new games", "total_fetched": len(games_data)}


@app.post("/admin/refresh-odds")
async def refresh_odds(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """Refresh betting odds for all games."""
    odds_service = await get_odds_service()
    odds_data = await odds_service.get_ncaa_football_odds()

    if not odds_data:
        return {"message": "No odds data available or API key not configured", "updated": 0}

    # Get active season
    season = db.query(Season).filter(Season.is_active == True).first()
    if not season:
        raise HTTPException(
            status_code=404,
            detail="No active season found"
        )

    updated = 0
    for odds in odds_data:
        # Find matching game
        game = db.query(Game).filter(
            Game.season_id == season.id,
            Game.home_team == odds["home_team"],
            Game.away_team == odds["away_team"]
        ).first()

        if game:
            if odds.get("spread") is not None:
                game.spread = odds["spread"]
            if odds.get("over_under") is not None:
                game.over_under = odds["over_under"]
            updated += 1

    db.commit()

    # Get remaining API requests
    remaining = await odds_service.get_remaining_requests()

    return {
        "message": f"Updated odds for {updated} games",
        "api_requests_remaining": remaining
    }


@app.get("/admin/api-status")
async def get_api_status(
    _: dict = Depends(verify_token)
):
    """Check API status and remaining requests."""
    odds_service = await get_odds_service()
    remaining = await odds_service.get_remaining_requests()

    return {
        "odds_api": {
            "configured": remaining is not None,
            "requests_remaining": remaining
        },
        "ncaa_api": {
            "configured": True,
            "note": "Public API, rate limited to 5 req/sec"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
