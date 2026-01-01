"""
Script to import existing bowl picks from Google Spreadsheet data.
Run this after starting the backend server for the first time.

Usage: python scripts/import_spreadsheet.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, Game, User, Pick, Season, init_db
from datetime import datetime

# Data from the spreadsheet (2024-25 season)
# Format: (bowl_name, away_team, home_team, spread, winner, picks_dict)
# picks_dict = {user_name: picked_team}

BOWL_GAMES = [
    # Playoff Games (from spreadsheet)
    ("CFP Quarterfinal", "Oklahoma", "Alabama", None, None, {
        "John": "Alabama", "Jean": "Alabama", "Emily": "Oklahoma",
        "Sarah": "Alabama", "Matt": "Oklahoma", "Billy": "Alabama",
        "Papa Jack": "Alabama", "Coconut": "Alabama"
    }),
    ("CFP Quarterfinal", "Texas A&M", "Miami", None, None, {
        "John": "Miami", "Jean": "Miami", "Emily": "Texas A&M",
        "Sarah": "Miami", "Matt": "Miami", "Billy": "Miami",
        "Papa Jack": "Texas A&M", "Coconut": "Miami"
    }),
    ("CFP Quarterfinal", "Ohio State", "Miami", -9.5, None, {}),
    ("CFP Quarterfinal", "Texas Tech", "Oregon", 2.5, None, {}),
    ("CFP Quarterfinal", "Indiana", "Alabama", -6.5, None, {}),
    ("CFP Semifinal", "Georgia", "Ole Miss", -6.5, None, {}),

    # Regular Bowl Games
    ("Sugar Bowl", "Ole Miss", "Tulane", None, None, {}),
    ("Fiesta Bowl", "Oregon", "JMU", None, None, {}),
    ("LA Bowl", "Cal", "Hawaii", None, None, {}),
    ("Quick Lane Bowl", "Central Michigan", "Northwestern", None, None, {}),
    ("New Mexico Bowl", "New Mexico", "Minnesota", None, None, {}),
    ("Frisco Bowl", "FIU", "UTSA", None, None, {}),
    ("Birmingham Bowl", "Pitt", "ECU", None, None, {}),
    ("Orange Bowl", "Penn State", "Clemson", None, None, {}),
    ("Fenway Bowl", "UConn", "Army", None, None, {}),
    ("Alamo Bowl", "Georgia Tech", "BYU", None, None, {}),
    ("Famous Idaho Potato Bowl", "Miami (OH)", "Fresno State", None, None, {}),
    ("New Orleans Bowl", "North Texas", "San Diego State", None, None, {}),
    ("ReliaQuest Bowl", "UVA", "Mizzou", None, None, {}),
    ("Texas Bowl", "LSU", "Houston", None, None, {}),
    ("Camellia Bowl", "Georgia Southern", "App State", None, None, {}),
    ("R+L Carriers Bowl", "Coastal Carolina", "Louisiana Tech", None, None, {}),
    ("Citrus Bowl", "Tennessee", "Illinois", None, None, {}),
    ("Holiday Bowl", "USC", "TCU", None, None, {}),
    ("Music City Bowl", "Iowa", "Vanderbilt", None, None, {}),
    ("Peach Bowl", "Arizona State", "Duke", None, None, {}),
    ("Rose Bowl", "Michigan", "Texas", None, None, {}),
    ("Sun Bowl", "Nebraska", "Utah", None, None, {}),
    ("First Responder Bowl", "Rice", "Texas State", None, None, {}),
    ("Armed Forces Bowl", "Navy", "Cincinnati", None, None, {}),
    ("Birmingham Bowl", "Wake Forest", "Mississippi State", None, None, {}),
    ("Pinstripe Bowl", "Arizona", "SMU", None, None, {}),
]


def import_data():
    """Import spreadsheet data into the database."""
    init_db()

    db = SessionLocal()
    try:
        # Get the active season
        season = db.query(Season).filter(Season.year == "2024-25").first()
        if not season:
            print("Creating 2024-25 season...")
            season = Season(year="2024-25", is_active=True)
            db.add(season)
            db.commit()

        # Get users
        users = {u.name: u for u in db.query(User).all()}

        games_added = 0
        picks_added = 0

        for bowl_name, away_team, home_team, spread, winner, picks_dict in BOWL_GAMES:
            # Check if game already exists
            existing = db.query(Game).filter(
                Game.season_id == season.id,
                Game.home_team == home_team,
                Game.away_team == away_team
            ).first()

            if existing:
                print(f"Game already exists: {away_team} vs {home_team}")
                game = existing
            else:
                # Determine if playoff game
                is_playoff = "CFP" in bowl_name or "Semifinal" in bowl_name or "Championship" in bowl_name

                game = Game(
                    season_id=season.id,
                    bowl_name=bowl_name,
                    home_team=home_team,
                    away_team=away_team,
                    spread=spread,
                    winner=winner,
                    is_playoff=is_playoff
                )
                db.add(game)
                db.flush()  # Get the game ID
                games_added += 1
                print(f"Added game: {bowl_name} - {away_team} vs {home_team}")

            # Add picks
            for user_name, picked_team in picks_dict.items():
                user = users.get(user_name)
                if not user:
                    print(f"  Warning: User '{user_name}' not found")
                    continue

                # Check if pick already exists
                existing_pick = db.query(Pick).filter(
                    Pick.user_id == user.id,
                    Pick.game_id == game.id
                ).first()

                if existing_pick:
                    print(f"  Pick already exists: {user_name} -> {picked_team}")
                else:
                    pick = Pick(
                        user_id=user.id,
                        game_id=game.id,
                        picked_team=picked_team,
                        is_correct=winner == picked_team if winner else None
                    )
                    db.add(pick)
                    picks_added += 1
                    print(f"  Added pick: {user_name} -> {picked_team}")

        db.commit()
        print(f"\nImport complete! Added {games_added} games and {picks_added} picks.")

    finally:
        db.close()


if __name__ == "__main__":
    import_data()
