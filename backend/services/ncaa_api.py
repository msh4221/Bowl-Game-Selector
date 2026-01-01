import httpx
from typing import List, Dict, Optional
from datetime import datetime
import re


class NCAAAPIService:
    """Service for fetching bowl game data from NCAA API."""

    BASE_URL = "https://ncaa-api.henrygd.me"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_bowl_games(self, year: str = "2024") -> List[Dict]:
        """
        Fetch bowl games for a given year.
        Returns a list of games with team names, dates, etc.
        """
        try:
            # Try the scoreboard endpoint for football
            url = f"{self.BASE_URL}/scoreboard/football/fbs/{year}"
            response = await self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                return self._parse_games(data)

            # Fallback: try schedule endpoint
            url = f"{self.BASE_URL}/schedule/football/fbs/{year}"
            response = await self.client.get(url)

            if response.status_code == 200:
                data = response.json()
                return self._parse_schedule(data)

            return []

        except Exception as e:
            print(f"Error fetching NCAA games: {e}")
            return []

    def _parse_games(self, data: dict) -> List[Dict]:
        """Parse game data from scoreboard response."""
        games = []

        if not isinstance(data, dict):
            return games

        game_list = data.get("games", [])

        for game_data in game_list:
            game = game_data.get("game", {})

            # Extract team names
            home = game.get("home", {})
            away = game.get("away", {})

            home_team = home.get("names", {}).get("short", "") or home.get("names", {}).get("full", "")
            away_team = away.get("names", {}).get("short", "") or away.get("names", {}).get("full", "")

            # Extract bowl name from title
            title = game.get("title", "")
            bowl_name = title if "bowl" in title.lower() or "playoff" in title.lower() else f"{away_team} vs {home_team}"

            # Extract game time
            start_time = game.get("startTime", "")
            game_time = None
            if start_time:
                try:
                    game_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                except:
                    pass

            # Check if playoff
            is_playoff = "playoff" in title.lower() or "semifinal" in title.lower() or "championship" in title.lower()

            # Extract scores if available
            home_score = home.get("score")
            away_score = away.get("score")

            # Determine winner if game is final
            winner = None
            if game.get("gameState") == "final":
                if home_score is not None and away_score is not None:
                    if int(home_score) > int(away_score):
                        winner = home_team
                    else:
                        winner = away_team

            if home_team and away_team:
                games.append({
                    "bowl_name": bowl_name,
                    "home_team": home_team,
                    "away_team": away_team,
                    "game_time": game_time,
                    "is_playoff": is_playoff,
                    "home_score": int(home_score) if home_score else None,
                    "away_score": int(away_score) if away_score else None,
                    "winner": winner
                })

        return games

    def _parse_schedule(self, data: dict) -> List[Dict]:
        """Parse game data from schedule response."""
        games = []

        if not isinstance(data, dict):
            return games

        # Schedule structure may vary
        weeks = data.get("weeks", [])

        for week in weeks:
            week_games = week.get("games", [])
            for game in week_games:
                home_team = game.get("home", {}).get("name", "")
                away_team = game.get("away", {}).get("name", "")

                if home_team and away_team:
                    games.append({
                        "bowl_name": game.get("name", f"{away_team} vs {home_team}"),
                        "home_team": home_team,
                        "away_team": away_team,
                        "game_time": None,
                        "is_playoff": False,
                        "home_score": None,
                        "away_score": None,
                        "winner": None
                    })

        return games

    async def close(self):
        await self.client.aclose()


# Singleton instance
ncaa_service = NCAAAPIService()


async def get_ncaa_service():
    return ncaa_service
