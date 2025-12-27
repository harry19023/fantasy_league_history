"""ESPN Fantasy API client."""

import os
from typing import Any

import httpx


class ESPNClient:
    """Client for interacting with ESPN Fantasy API."""

    BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3"

    def __init__(self, swid: str | None = None, espn_s2: str | None = None):
        """Initialize ESPN client with authentication cookies.

        Args:
            swid: ESPN SWID cookie value
            espn_s2: ESPN espn_s2 cookie value
        """
        self.swid = swid or os.getenv("ESPN_SWID", "")
        self.espn_s2 = espn_s2 or os.getenv("ESPN_S2", "")

        self.cookies = {}
        if self.swid:
            self.cookies["SWID"] = self.swid
        if self.espn_s2:
            self.cookies["espn_s2"] = self.espn_s2

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.espn.com/",
        }

    def _request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | list[Any]:
        """Make a request to the ESPN API.

        Args:
            endpoint: API endpoint (relative to BASE_URL)
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = httpx.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
            params=params,
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()

    def get_league_history(
        self, league_id: int, scoring_period_id: int | None = None
    ) -> list[dict[str, Any]]:
        """Get league history.

        Args:
            league_id: ESPN league ID
            scoring_period_id: Optional scoring period ID

        Returns:
            List of league history entries
        """
        endpoint = f"games/ffl/leagueHistory/{league_id}"
        params = {}
        if scoring_period_id:
            params["scoringPeriodId"] = scoring_period_id

        result = self._request(endpoint, params=params if params else None)
        # This endpoint always returns a list
        if isinstance(result, list):
            return result
        return [result] if isinstance(result, dict) else []
