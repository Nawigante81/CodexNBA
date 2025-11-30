import asyncio
from datetime import datetime
from typing import Dict, List

import httpx
from bs4 import BeautifulSoup

from data.sample_data import SAMPLE_CLOSING_LINES, SAMPLE_INJURIES, SAMPLE_RECENT_GAMES

USER_AGENT = {"User-Agent": "Mozilla/5.0 (CodexNBA analytics bot)"}


async def fetch_basketball_reference_snapshot(allow_network: bool = True) -> Dict:
    fallback_games = SAMPLE_RECENT_GAMES
    url = "https://www.basketball-reference.com/boxscores/"
    if not allow_network:
        return {
            "source": "basketball_reference",
            "status": "offline",
            "fetched_at": datetime.utcnow().isoformat(),
            "games": fallback_games,
            "note": "Offline mode — using bundled sample games",
        }

    try:
        async with httpx.AsyncClient(timeout=5.0, headers=USER_AGENT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return {
            "source": "basketball_reference",
            "status": "failed",
            "error": str(exc),
            "fetched_at": datetime.utcnow().isoformat(),
            "games": fallback_games,
        }

    soup = BeautifulSoup(resp.text, "html.parser")
    games: List[Dict] = []
    for summary in soup.select("div.game_summary"):
        teams = summary.select("table.teams tr")
        if len(teams) < 2:
            continue
        away_row, home_row = teams[0], teams[1]
        away_name = away_row.find("a").text if away_row.find("a") else ""
        home_name = home_row.find("a").text if home_row.find("a") else ""
        scores = summary.select("td.right")
        if len(scores) < 2:
            continue
        try:
            away_score = int(scores[0].text.strip())
            home_score = int(scores[1].text.strip())
        except ValueError:
            continue
        games.append(
            {
                "home": home_name,
                "away": away_name,
                "home_score": home_score,
                "away_score": away_score,
                "date": datetime.utcnow().date().isoformat(),
            }
        )
    if not games:
        games = fallback_games
    return {
        "source": "basketball_reference",
        "status": "ok",
        "fetched_at": datetime.utcnow().isoformat(),
        "games": games,
    }


async def fetch_vegasinsider_lines(allow_network: bool = True) -> Dict:
    fallback_lines = SAMPLE_CLOSING_LINES
    url = "https://www.vegasinsider.com/nba/odds/las-vegas/"
    if not allow_network:
        return {
            "source": "vegasinsider",
            "status": "offline",
            "fetched_at": datetime.utcnow().isoformat(),
            "lines": fallback_lines,
            "note": "Offline mode — using bundled sample odds",
        }

    try:
        async with httpx.AsyncClient(timeout=5.0, headers=USER_AGENT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return {
            "source": "vegasinsider",
            "status": "failed",
            "error": str(exc),
            "fetched_at": datetime.utcnow().isoformat(),
            "lines": fallback_lines,
        }

    soup = BeautifulSoup(resp.text, "html.parser")
    lines: List[Dict] = []
    for row in soup.select("table tbody tr"):
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        matchup = cells[0].get_text(strip=True)
        spread = cells[1].get_text(strip=True)
        total = cells[2].get_text(strip=True)
        moneyline = cells[3].get_text(strip=True)
        if matchup:
            lines.append(
                {
                    "matchup": matchup,
                    "sportsbook": "VegasInsider",
                    "spread": spread or "N/A",
                    "total": total or "N/A",
                    "moneyline": moneyline or "N/A",
                    "result": "TBD",
                }
            )
        if len(lines) >= 6:
            break
    if not lines:
        lines = fallback_lines
    return {
        "source": "vegasinsider",
        "status": "ok",
        "fetched_at": datetime.utcnow().isoformat(),
        "lines": lines,
    }


async def fetch_nba_injuries(allow_network: bool = True) -> Dict:
    fallback_injuries = SAMPLE_INJURIES
    url = "https://cdn.nba.com/static/json/injury/injury_2023-24.json"
    if not allow_network:
        return {
            "source": "nba.com",
            "status": "offline",
            "fetched_at": datetime.utcnow().isoformat(),
            "injuries": fallback_injuries,
            "note": "Offline mode — using bundled injuries",
        }

    try:
        async with httpx.AsyncClient(timeout=5.0, headers=USER_AGENT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return {
            "source": "nba.com",
            "status": "failed",
            "error": str(exc),
            "fetched_at": datetime.utcnow().isoformat(),
            "injuries": fallback_injuries,
        }

    payload = resp.json()
    items = payload.get("league", {}).get("standard", []) if isinstance(payload, dict) else []
    injuries = []
    for entry in items:
        team = entry.get("teamTricode")
        player = entry.get("firstName", "") + " " + entry.get("lastName", "")
        status = entry.get("status")
        note = entry.get("note", "")
        if team and player.strip():
            injuries.append(
                {
                    "team": team,
                    "player": player.strip(),
                    "status": status or "TBD",
                    "note": note or "",
                }
            )
        if len(injuries) >= 25:
            break
    if not injuries:
        injuries = fallback_injuries
    return {
        "source": "nba.com",
        "status": "ok",
        "fetched_at": datetime.utcnow().isoformat(),
        "injuries": injuries,
    }


async def run_parallel(*tasks):
    return await asyncio.gather(*tasks)
