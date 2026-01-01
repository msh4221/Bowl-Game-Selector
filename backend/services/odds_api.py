import httpx
from typing import List, Dict, Optional
from config import get_settings


class OddsAPIService:
    """Service for fetching betting odds from The Odds API."""

    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_ncaa_football_odds(self) -> List[Dict]:
        """
        Fetch current NCAA football odds.
        Returns a list of games with spreads and over/under.
        """
        settings = get_settings()

        if not settings.odds_api_key:
            print("No Odds API key configured")
            return []

        try:
            url = f"{self.BASE_URL}/sports/americanfootball_ncaaf/odds"
            params = {
                "apiKey": settings.odds_api_key,
                "regions": "us",
                "markets": "spreads,totals",
                "oddsFormat": "american"
            }

            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                return self._parse_odds(data)
            elif response.status_code == 401:
                print("Invalid Odds API key")
            elif response.status_code == 429:
                print("Odds API rate limit exceeded")
            else:
                print(f"Odds API error: {response.status_code}")

            return []

        except Exception as e:
            print(f"Error fetching odds: {e}")
            return []

    def _parse_odds(self, data: List[dict]) -> List[Dict]:
        """Parse odds data from API response."""
        games = []

        for game in data:
            home_team = game.get("home_team", "")
            away_team = game.get("away_team", "")

            # Get odds from first available bookmaker
            bookmakers = game.get("bookmakers", [])
            spread = None
            over_under = None

            for bookmaker in bookmakers:
                markets = bookmaker.get("markets", [])

                for market in markets:
                    if market.get("key") == "spreads":
                        outcomes = market.get("outcomes", [])
                        for outcome in outcomes:
                            if outcome.get("name") == home_team:
                                spread = outcome.get("point")
                                break

                    if market.get("key") == "totals":
                        outcomes = market.get("outcomes", [])
                        for outcome in outcomes:
                            if outcome.get("name") == "Over":
                                over_under = outcome.get("point")
                                break

                # Break after first bookmaker with data
                if spread is not None or over_under is not None:
                    break

            games.append({
                "home_team": home_team,
                "away_team": away_team,
                "spread": spread,
                "over_under": over_under,
                "commence_time": game.get("commence_time")
            })

        return games

    async def get_remaining_requests(self) -> Optional[int]:
        """Check remaining API requests."""
        settings = get_settings()

        if not settings.odds_api_key:
            return None

        try:
            url = f"{self.BASE_URL}/sports"
            params = {"apiKey": settings.odds_api_key}

            response = await self.client.get(url, params=params)

            # Remaining requests are in response headers
            remaining = response.headers.get("x-requests-remaining")
            return int(remaining) if remaining else None

        except Exception:
            return None

    async def close(self):
        await self.client.aclose()


# Singleton instance
odds_service = OddsAPIService()


async def get_odds_service():
    return odds_service
