import asyncio
from datetime import datetime
from typing import Dict, List

import httpx
from bs4 import BeautifulSoup

from data.sample_data import SAMPLE_CLOSING_LINES, SAMPLE_INJURIES, SAMPLE_RECENT_GAMES

USER_AGENT = {"User-Agent": "Mozilla/5.0 (CodexNBA analytics bot)"}


async def fetch_basketball_reference_snapshot(allow_network: bool = True) -> Dict:
    url = "https://www.basketball-reference.com/boxscores/"
    if not allow_network:
        return {
            "source": "basketball_reference",
            "status": "offline",
            "fetched_at": datetime.utcnow().isoformat(),
            "games": SAMPLE_RECENT_GAMES,
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
            "games": [],
            "note": "Live fetch failed; no sample data used when network is enabled",
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
    return {
        "source": "basketball_reference",
        "status": "ok" if games else "empty",
        "fetched_at": datetime.utcnow().isoformat(),
        "games": games,
        "note": None if games else "No games parsed from live source",
    }


async def fetch_vegasinsider_lines(allow_network: bool = True) -> Dict:
    url = "https://www.vegasinsider.com/nba/odds/las-vegas/"
    if not allow_network:
        return {
            "source": "vegasinsider",
            "status": "offline",
            "fetched_at": datetime.utcnow().isoformat(),
            "lines": SAMPLE_CLOSING_LINES,
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
            "lines": [],
            "note": "Live fetch failed; odds not replaced with sample data",
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
    return {
        "source": "vegasinsider",
        "status": "ok" if lines else "empty",
        "fetched_at": datetime.utcnow().isoformat(),
        "lines": lines,
        "note": None if lines else "No odds parsed from live source",
    }


async def fetch_nba_injuries(allow_network: bool = True) -> Dict:
    url = "https://cdn.nba.com/static/json/injury/injury_2023-24.json"
    if not allow_network:
        return {
            "source": "nba.com",
            "status": "offline",
            "fetched_at": datetime.utcnow().isoformat(),
            "injuries": SAMPLE_INJURIES,
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
            "injuries": [],
            "note": "Live fetch failed; injury list empty until network succeeds",
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
    return {
        "source": "nba.com",
        "status": "ok" if injuries else "empty",
        "fetched_at": datetime.utcnow().isoformat(),
        "injuries": injuries,
        "note": None if injuries else "No injuries parsed from live source",
    }


async def run_parallel(*tasks):
    return await asyncio.gather(*tasks)
