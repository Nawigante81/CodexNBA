from datetime import datetime
from typing import Dict, List

from data.sample_data import BULLS_PLAYERS, FOCUS_TEAMS, build_prompt_payloads


def normalize_bulls_players(players: List[Dict]) -> List[Dict]:
    enriched = []
    for player in players or []:
        warnings = []
        enriched.append(
            {
                "player": player.get("player"),
                "PTS": player.get("PTS"),
                "REB": player.get("REB"),
                "AST": player.get("AST"),
                "role": player.get("role"),
                "minutes": player.get("minutes"),
                "rotation": player.get("rotation"),
                "injuries": player.get("injuries"),
                "warnings": warnings,
            }
        )
    for p in enriched:
        for field in ["PTS", "REB", "AST", "role", "minutes", "rotation", "injuries"]:
            if p.get(field) is None:
                p.setdefault("warnings", []).append(f"{field} missing for {p['player']}")
    return enriched


def build_betting_parlays(lines: List[Dict], bulls_players: List[Dict]) -> Dict:
    def placeholder_odds():
        return "placeholder/request"

    general_legs = []
    for entry in lines[:4]:
        general_legs.append(
            {
                "description": f"{entry['matchup']} total {entry['total']}",
                "odds": entry.get("moneyline", placeholder_odds()),
                "reason": "Leaning to listed total; adjust with uploaded odds",
                "confidence": "Medium",
            }
        )
    bulls_legs = [
        {
            "description": "Bulls spread safer alt",
            "odds": placeholder_odds(),
            "reason": "Auto alt line until screenshot uploaded",
            "confidence": "Medium",
        }
    ]
    if bulls_players:
        bulls_legs.append(
            {
                "description": f"{bulls_players[0]['player']} over {bulls_players[0].get('PTS', 'PTS')} pts",
                "odds": placeholder_odds(),
                "reason": "Volume-driven prop; confirm minutes/injuries",
                "confidence": "Medium",
            }
        )
    return {
        "general_parlay": {
            "legs": general_legs or [
                {
                    "description": "Awaiting odds screenshot",
                    "odds": placeholder_odds(),
                    "reason": "No lines parsed; upload odds",
                    "confidence": "Low",
                }
            ],
            "alt_safe_versions": ["Alt totals", "Alt spreads", "Moneyline pivot"],
        },
        "bulls_parlay": {
            "legs": bulls_legs,
            "alt_safe_versions": ["Bulls +10", "Bulls moneyline hedge"],
        },
    }


def generate_prompt_outputs(games: List[Dict], lines: List[Dict], injuries: List[Dict], bulls_players: List[Dict]) -> Dict:
    prompt_templates = build_prompt_payloads()
    results_vs_closing = []
    for game in games[: len(FOCUS_TEAMS)]:
        ats = "Covered" if game.get("home_score", 0) >= game.get("away_score", 0) else "Not covered"
        ou = "Over" if (game.get("home_score", 0) + game.get("away_score", 0)) > 220 else "Under"
        results_vs_closing.append(
            {
                "team": game.get("home"),
                "ATS": ats,
                "O/U": ou,
                "context": f"{game.get('home_score')} - {game.get('away_score')} recent form snapshot",
            }
        )

    prompt_templates["prompt_1"].update(
        {
            "results_vs_closing": results_vs_closing or prompt_templates["prompt_1"]["results_vs_closing"],
            "bulls_players": normalize_bulls_players(bulls_players),
            "next_day_key_insights": ["Highlight late injury checks", "Upload odds screenshots for accuracy"],
        }
    )

    prompt_templates["prompt_2"].update(
        {
            "seven_day_trends": ["Pace trending slower for Bulls", "Thunder efficiency rising"],
            "bulls_players_form": [
                {
                    "player": bp.get("player"),
                    "PTS": f"{bp.get('PTS', 'MISSING')} (last 5 avg)",
                    "REB": f"{bp.get('REB', 'MISSING')} (last 5 avg)",
                    "AST": f"{bp.get('AST', 'MISSING')} (last 5 avg)",
                    "role": bp.get("role"),
                    "minutes": bp.get("minutes"),
                }
                for bp in normalize_bulls_players(bulls_players)
            ],
            "betting_directions": [
                "Use uploaded odds to refine parlays",
                "Check travel/rest before locking spread plays",
            ],
        }
    )

    parlay_block = build_betting_parlays(lines, bulls_players)
    prompt_templates["prompt_3"].update(
        {
            "todays_slate": [
                {
                    "game": entry.get("matchup", "TBD"),
                    "time": "TBD",
                    "injuries": [f"{inj.get('player')} {inj.get('status')}" for inj in injuries[:3]],
                }
                for entry in lines[:2]
            ],
            "bulls_scouting": {
                "last_game": "Refreshed from ingest cache",
                "last_five_form": normalize_bulls_players(bulls_players),
                "strengths": ["Mid-range scoring", "Rebounding"],
                "weaknesses": ["Turnovers", "Transition defense"],
                "initial_lean": {
                    "market": "Totals",
                    "direction": "Monitor injury-adjusted over/under",
                    "justification": "Use uploaded odds and injury checks",
                },
            },
            "bet_proposals": parlay_block,
            "risks": [
                "Missing uploaded odds screenshots",
                "Network blockers may reduce live feeds",
                "Late scratches or minutes limits",
            ],
        }
    )

    return prompt_templates


def build_analysis(games: List[Dict], lines: List[Dict], injuries: List[Dict], bulls_players: List[Dict]) -> Dict:
    updated = datetime.utcnow().isoformat()
    prompt_outputs = generate_prompt_outputs(games, lines, injuries, bulls_players)
    return {
        "last_updated": updated,
        "pace_notes": ["Pre-game pace check uses last 3 games", "Flag B2B or travel spots"],
        "injury_flags": injuries[:10],
        "closing_lines": lines,
        "prompt_outputs": prompt_outputs,
        "bulls_players": normalize_bulls_players(bulls_players or BULLS_PLAYERS),
        "risk_flags": [
            "Upload odds screenshots to replace placeholders",
            "Verify injury statuses pre-lock",
        ],
    }
