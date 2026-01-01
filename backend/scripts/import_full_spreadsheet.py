"""
Full import of bowl picks from Google Spreadsheet.
Run: python scripts/import_full_spreadsheet.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, Game, User, Pick, Season, init_db

# Complete data from spreadsheet
# Format: (home_team, away_team, spread, winner, picks)
# picks = {user: picked_team} - None means no pick

GAMES_DATA = [
    # Game 1: OKLA vs Alabama - Winner: Alabama
    ("Alabama", "Oklahoma", None, "Alabama", {
        "John": "Oklahoma", "Jean": "Alabama", "Emily": "Oklahoma", "Sarah": "Alabama",
        "Matt": "Alabama", "Billy": "Alabama", "Papa Jack": "Alabama", "Coconut": "Alabama"
    }),
    # Game 2: T A&M vs Miami - Winner: Miami
    ("Miami", "Texas A&M", None, "Miami", {
        "John": "Texas A&M", "Jean": "Texas A&M", "Emily": "Texas A&M", "Sarah": "Texas A&M",
        "Matt": "Texas A&M", "Billy": "Texas A&M", "Papa Jack": "Miami", "Coconut": "Miami"
    }),
    # Game 3: OSU vs Miami (CFP) - No winner yet
    ("Miami", "Ohio State", -9.5, None, {
        "John": "Ohio State", "Jean": "Ohio State", "Emily": "Ohio State", "Sarah": "Ohio State",
        "Matt": "Ohio State", "Billy": None, "Papa Jack": "Miami", "Coconut": None
    }),
    # Game 4: Texas Tech vs Oregon - No winner yet
    ("Oregon", "Texas Tech", 2.5, None, {
        "John": "Texas Tech", "Jean": "Oregon", "Emily": "Texas Tech", "Sarah": "Texas Tech",
        "Matt": "Oregon", "Billy": None, "Papa Jack": "Texas Tech", "Coconut": None
    }),
    # Game 5: Indiana vs Alabama - No winner yet
    ("Alabama", "Indiana", -6.5, None, {
        "John": "Indiana", "Jean": "Alabama", "Emily": "Indiana", "Sarah": "Indiana",
        "Matt": "Indiana", "Billy": "Alabama", "Papa Jack": "Alabama", "Coconut": None
    }),
    # Game 6: Georgia vs Ole Miss - No winner yet
    ("Ole Miss", "Georgia", -6.5, None, {
        "John": "Georgia", "Jean": "Ole Miss", "Emily": "Georgia", "Sarah": "Georgia",
        "Matt": "Georgia", "Billy": None, "Papa Jack": "Ole Miss", "Coconut": None
    }),
    # Game 7: Ole Miss vs Tulane - Winner: Ole Miss
    ("Tulane", "Ole Miss", -17.5, "Ole Miss", {
        "John": "Ole Miss", "Jean": "Ole Miss", "Emily": "Ole Miss", "Sarah": "Ole Miss",
        "Matt": "Ole Miss", "Billy": "Ole Miss", "Papa Jack": "Tulane", "Coconut": "Ole Miss"
    }),
    # Game 8: Oregon vs JMU - Winner: Oregon
    ("JMU", "Oregon", -21, "Oregon", {
        "John": "Oregon", "Jean": "Oregon", "Emily": "Oregon", "Sarah": "Oregon",
        "Matt": "Oregon", "Billy": "Oregon", "Papa Jack": "JMU", "Coconut": "Oregon"
    }),
    # Game 9: Cal vs Hawaii - Winner: Hawaii
    ("Hawaii", "Cal", 1.5, "Hawaii", {
        "John": "Cal", "Jean": "Cal", "Emily": "Hawaii", "Sarah": "Hawaii",
        "Matt": "Hawaii", "Billy": "Hawaii", "Papa Jack": "Cal", "Coconut": "Hawaii"
    }),
    # Game 10: Central Michigan vs Northwestern - Winner: Northwestern
    ("Northwestern", "Central Michigan", 10.5, "Northwestern", {
        "John": "Northwestern", "Jean": "Northwestern", "Emily": "Northwestern", "Sarah": "Northwestern",
        "Matt": "Northwestern", "Billy": None, "Papa Jack": "Central Michigan", "Coconut": "Northwestern"
    }),
    # Game 11: New Mexico vs Minnesota - Winner: Minnesota
    ("Minnesota", "New Mexico", 2.5, "Minnesota", {
        "John": "Minnesota", "Jean": "New Mexico", "Emily": "Minnesota", "Sarah": "Minnesota",
        "Matt": "New Mexico", "Billy": None, "Papa Jack": "New Mexico", "Coconut": "Minnesota"
    }),
    # Game 12: FIU vs UTSA - Winner: UTSA
    ("UTSA", "FIU", 6, "UTSA", {
        "John": "UTSA", "Jean": "UTSA", "Emily": "UTSA", "Sarah": "UTSA",
        "Matt": "UTSA", "Billy": None, "Papa Jack": "FIU", "Coconut": "UTSA"
    }),
    # Game 13: Pitt vs ECU - Winner: ECU
    ("ECU", "Pitt", -10, "ECU", {
        "John": "Pitt", "Jean": "Pitt", "Emily": "Pitt", "Sarah": "Pitt",
        "Matt": "Pitt", "Billy": None, "Papa Jack": "ECU", "Coconut": "ECU"
    }),
    # Game 14: Penn State vs Clemson - Winner: Penn State
    ("Clemson", "Penn State", 3, "Penn State", {
        "John": "Penn State", "Jean": "Clemson", "Emily": "Penn State", "Sarah": "Clemson",
        "Matt": "Clemson", "Billy": None, "Papa Jack": "Penn State", "Coconut": "Penn State"
    }),
    # Game 15: UConn vs Army - Winner: Army
    ("Army", "UConn", 9.5, "Army", {
        "John": "Army", "Jean": "Army", "Emily": "Army", "Sarah": "Army",
        "Matt": "Army", "Billy": None, "Papa Jack": "UConn", "Coconut": "Army"
    }),
    # Game 16: Georgia Tech vs BYU - Winner: BYU
    ("BYU", "Georgia Tech", 4.5, "BYU", {
        "John": "BYU", "Jean": "Georgia Tech", "Emily": "BYU", "Sarah": "Georgia Tech",
        "Matt": "Georgia Tech", "Billy": None, "Papa Jack": "Georgia Tech", "Coconut": "BYU"
    }),
    # Game 17: Miami (OH) vs Fresno State - Winner: Fresno State
    ("Fresno State", "Miami (OH)", 4.5, "Fresno State", {
        "John": "Fresno State", "Jean": "Fresno State", "Emily": "Fresno State", "Sarah": "Fresno State",
        "Matt": "Miami (OH)", "Billy": None, "Papa Jack": "Miami (OH)", "Coconut": "Fresno State"
    }),
    # Game 18: North Texas vs San Diego State - Winner: North Texas
    ("San Diego State", "North Texas", -3, "North Texas", {
        "John": "North Texas", "Jean": "North Texas", "Emily": "North Texas", "Sarah": "North Texas",
        "Matt": "North Texas", "Billy": None, "Papa Jack": "San Diego State", "Coconut": "North Texas"
    }),
    # Game 19: UVA vs Mizzou - Winner: UVA
    ("Mizzou", "UVA", 4, "UVA", {
        "John": "Mizzou", "Jean": "UVA", "Emily": "Mizzou", "Sarah": "Mizzou",
        "Matt": "UVA", "Billy": None, "Papa Jack": "UVA", "Coconut": "UVA"
    }),
    # Game 20: LSU vs Houston - Winner: Houston
    ("Houston", "LSU", 3, "Houston", {
        "John": "LSU", "Jean": "Houston", "Emily": "LSU", "Sarah": "LSU",
        "Matt": "LSU", "Billy": None, "Papa Jack": "LSU", "Coconut": "Houston"
    }),
    # Game 21: Georgia Southern vs App State - Winner: Georgia Southern
    ("App State", "Georgia Southern", -7.5, "Georgia Southern", {
        "John": "Georgia Southern", "Jean": "Georgia Southern", "Emily": "Georgia Southern", "Sarah": "Georgia Southern",
        "Matt": "Georgia Southern", "Billy": None, "Papa Jack": "App State", "Coconut": "Georgia Southern"
    }),
    # Game 22: Coastal Carolina vs Louisiana Tech - Winner: Louisiana Tech
    ("Louisiana Tech", "Coastal Carolina", 9.5, "Louisiana Tech", {
        "John": "Louisiana Tech", "Jean": "Louisiana Tech", "Emily": "Louisiana Tech", "Sarah": "Louisiana Tech",
        "Matt": "Louisiana Tech", "Billy": None, "Papa Jack": "Coastal Carolina", "Coconut": "Louisiana Tech"
    }),
    # Game 23: Tennessee vs Illinois - Winner: Illinois
    ("Illinois", "Tennessee", -2.5, "Illinois", {
        "John": "Tennessee", "Jean": "Tennessee", "Emily": "Tennessee", "Sarah": "Tennessee",
        "Matt": "Illinois", "Billy": "Illinois", "Papa Jack": "Illinois", "Coconut": "Illinois"
    }),
    # Game 24: USC vs TCU - Winner: TCU
    ("TCU", "USC", -7, "TCU", {
        "John": "USC", "Jean": "TCU", "Emily": "USC", "Sarah": "USC",
        "Matt": "TCU", "Billy": None, "Papa Jack": "TCU", "Coconut": "TCU"
    }),
    # Game 25: Iowa vs Vanderbilt - Winner: Iowa
    ("Vanderbilt", "Iowa", 5.5, "Iowa", {
        "John": "Vanderbilt", "Jean": "Vanderbilt", "Emily": "Vanderbilt", "Sarah": "Vanderbilt",
        "Matt": "Vanderbilt", "Billy": None, "Papa Jack": "Iowa", "Coconut": "Iowa"
    }),
    # Game 26: Arizona State vs Duke - Winner: Duke
    ("Duke", "Arizona State", 3, "Duke", {
        "John": "Duke", "Jean": "Arizona State", "Emily": "Duke", "Sarah": "Duke",
        "Matt": "Arizona State", "Billy": None, "Papa Jack": "Arizona State", "Coconut": "Duke"
    }),
    # Game 27: Michigan vs Texas - Winner: Texas
    ("Texas", "Michigan", 7.5, "Texas", {
        "John": "Texas", "Jean": "Texas", "Emily": "Texas", "Sarah": "Texas",
        "Matt": "Texas", "Billy": None, "Papa Jack": "Michigan", "Coconut": "Texas"
    }),
    # Game 28: Nebraska vs Utah - Winner: Utah
    ("Utah", "Nebraska", 16.5, "Utah", {
        "John": "Utah", "Jean": "Utah", "Emily": "Utah", "Sarah": "Utah",
        "Matt": "Utah", "Billy": None, "Papa Jack": "Nebraska", "Coconut": "Utah"
    }),
    # Game 29: Rice vs Texas State - No winner yet
    ("Texas State", "Rice", 11.5, None, {
        "John": "Texas State", "Jean": "Texas State", "Emily": "Texas State", "Sarah": "Texas State",
        "Matt": "Texas State", "Billy": None, "Papa Jack": "Rice", "Coconut": None
    }),
    # Game 30: Navy vs Cincinnati - No winner yet
    ("Cincinnati", "Navy", -7, None, {
        "John": "Navy", "Jean": "Navy", "Emily": "Navy", "Sarah": "Navy",
        "Matt": "Navy", "Billy": None, "Papa Jack": "Cincinnati", "Coconut": None
    }),
    # Game 31: Wake Forest vs Mississippi State - No winner yet
    ("Mississippi State", "Wake Forest", 4, None, {
        "John": "Mississippi State", "Jean": "Wake Forest", "Emily": "Wake Forest", "Sarah": "Wake Forest",
        "Matt": "Mississippi State", "Billy": None, "Papa Jack": "Wake Forest", "Coconut": None
    }),
    # Game 32: Arizona vs SMU - No winner yet
    ("SMU", "Arizona", -3, None, {
        "John": "Arizona", "Jean": "Arizona", "Emily": "SMU", "Sarah": "SMU",
        "Matt": "SMU", "Billy": None, "Papa Jack": "SMU", "Coconut": None
    }),
]

BOWL_NAMES = [
    "CFP Quarterfinal", "CFP Quarterfinal", "CFP Quarterfinal", "CFP Quarterfinal",
    "CFP Quarterfinal", "CFP Semifinal", "Sugar Bowl", "Fiesta Bowl",
    "LA Bowl", "Quick Lane Bowl", "New Mexico Bowl", "Frisco Bowl",
    "Birmingham Bowl", "Orange Bowl", "Fenway Bowl", "Alamo Bowl",
    "Famous Idaho Potato Bowl", "New Orleans Bowl", "ReliaQuest Bowl", "Texas Bowl",
    "Camellia Bowl", "R+L Carriers Bowl", "Citrus Bowl", "Holiday Bowl",
    "Music City Bowl", "Peach Bowl", "Rose Bowl", "Sun Bowl",
    "First Responder Bowl", "Armed Forces Bowl", "Birmingham Bowl", "Pinstripe Bowl"
]


def import_data():
    """Clear existing data and import fresh from spreadsheet."""
    init_db()

    db = SessionLocal()
    try:
        # Get season
        season = db.query(Season).filter(Season.year == "2024-25").first()
        if not season:
            season = Season(year="2024-25", is_active=True)
            db.add(season)
            db.commit()

        # Clear existing games and picks for this season
        existing_games = db.query(Game).filter(Game.season_id == season.id).all()
        for game in existing_games:
            db.query(Pick).filter(Pick.game_id == game.id).delete()
        db.query(Game).filter(Game.season_id == season.id).delete()
        db.commit()
        print("Cleared existing games and picks")

        # Get users
        users = {u.name: u for u in db.query(User).all()}

        games_added = 0
        picks_added = 0

        for i, (home_team, away_team, spread, winner, picks_dict) in enumerate(GAMES_DATA):
            bowl_name = BOWL_NAMES[i] if i < len(BOWL_NAMES) else f"Bowl Game {i+1}"
            is_playoff = "CFP" in bowl_name

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
            db.flush()
            games_added += 1

            # Add picks
            for user_name, picked_team in picks_dict.items():
                if picked_team is None:
                    continue

                user = users.get(user_name)
                if not user:
                    print(f"Warning: User '{user_name}' not found")
                    continue

                is_correct = None
                if winner:
                    is_correct = picked_team == winner

                pick = Pick(
                    user_id=user.id,
                    game_id=game.id,
                    picked_team=picked_team,
                    is_correct=is_correct
                )
                db.add(pick)
                picks_added += 1

        db.commit()
        print(f"\nImport complete!")
        print(f"Added {games_added} games")
        print(f"Added {picks_added} picks")

        # Show leaderboard
        print("\n--- Current Leaderboard ---")
        for user in users.values():
            picks = db.query(Pick).filter(Pick.user_id == user.id).all()
            correct = sum(1 for p in picks if p.is_correct is True)
            wrong = sum(1 for p in picks if p.is_correct is False)
            pending = sum(1 for p in picks if p.is_correct is None)
            print(f"{user.name}: {correct} correct, {wrong} wrong, {pending} pending")

    finally:
        db.close()


if __name__ == "__main__":
    import_data()
