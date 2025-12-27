"""Test script for ESPN Fantasy API integration."""

import argparse
import json
import os
import sys

import httpx


def test_espn_endpoint(url: str, cookies: dict | None = None):
    """Test ESPN Fantasy API endpoint."""
    print(f"Testing endpoint: {url}")
    print("-" * 80)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.espn.com/",
    }

    try:
        response = httpx.get(url, headers=headers, cookies=cookies, timeout=10.0)
        print(f"\nStatus Code: {response.status_code}")
        print(f"X-Fantasy-Role: {response.headers.get('x-fantasy-role', 'N/A')}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(
                    f"\n✅ Success! Response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}"
                )
                print("\nResponse preview:")
                print(json.dumps(data, indent=2)[:1000])
                return data
            except Exception:
                print(f"\nResponse (first 500 chars): {response.text[:500]}")
                return response.text
        else:
            print("\n❌ Error Response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except Exception:
                print(response.text[:500])
            return None
    except Exception as e:
        print(f"\n❌ Request Error: {e}")
        return None


def main():
    """Main function to test ESPN API."""
    parser = argparse.ArgumentParser(description="Test ESPN Fantasy API endpoint")
    parser.add_argument(
        "--league-id",
        type=int,
        default=777493,
        help="ESPN league ID (default: 777493)",
    )
    parser.add_argument(
        "--scoring-period-id",
        type=int,
        default=5,
        help="Scoring period ID (default: 5)",
    )
    args = parser.parse_args()

    league_id = args.league_id
    scoring_period_id = args.scoring_period_id
    url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{league_id}?scoringPeriodId={scoring_period_id}"

    # Check for cookies from environment
    swid = os.getenv("ESPN_SWID")
    espn_s2 = os.getenv("ESPN_S2")

    cookies = None
    if swid or espn_s2:
        cookies = {}
        if swid:
            cookies["SWID"] = swid
        if espn_s2:
            cookies["espn_s2"] = espn_s2
        print("Using cookies from environment variables")
    else:
        print("No cookies found in environment variables")
        print("\nTo test with authentication, set:")
        print("  export ESPN_SWID='your-swid-value'")
        print("  export ESPN_S2='your-espn-s2-value'")
        print("\nYou can find these cookies in your browser's developer tools:")
        print("  1. Open ESPN Fantasy site")
        print("  2. Open Developer Tools (F12)")
        print("  3. Go to Application/Storage > Cookies")
        print("  4. Look for 'SWID' and 'espn_s2' cookies")
        sys.exit(1)

    result = test_espn_endpoint(url, cookies)
    return result


if __name__ == "__main__":
    main()
