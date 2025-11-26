from datetime import datetime

FOCUS_TEAMS = [
    "Celtics",
    "Wolves",
    "Thunder",
    "Magic",
    "Cavs",
    "Kings",
    "Rockets",
    "Knicks",
    "Bulls",
]

BULLS_PLAYERS = [
    {
        "player": "Zach LaVine",
        "PTS": 24,
        "REB": 5,
        "AST": 4,
        "role": "Starter",
        "minutes": 34,
        "rotation": "Primary scorer, closing unit",
        "injuries": "None",
    },
    {
        "player": "DeMar DeRozan",
        "PTS": 23,
        "REB": 4,
        "AST": 5,
        "role": "Starter",
        "minutes": 35,
        "rotation": "Clutch mid-range, secondary playmaker",
        "injuries": "None",
    },
    {
        "player": "Nikola Vucevic",
        "PTS": 18,
        "REB": 11,
        "AST": 3,
        "role": "Starter",
        "minutes": 32,
        "rotation": "Starting center, defensive rebounds",
        "injuries": "None",
    },
]

SAMPLE_RECENT_GAMES = [
    {"home": "Bulls", "away": "Knicks", "home_score": 104, "away_score": 102, "date": "2024-03-10"},
    {"home": "Wolves", "away": "Kings", "home_score": 113, "away_score": 108, "date": "2024-03-10"},
    {"home": "Celtics", "away": "Cavs", "home_score": 118, "away_score": 114, "date": "2024-03-10"},
]

SAMPLE_CLOSING_LINES = [
    {
        "matchup": "Bulls @ Knicks",
        "sportsbook": "Bet365",
        "spread": "+3.5",
        "total": "214.5",
        "moneyline": "+135",
        "result": "Under, Bulls covered",
    },
    {
        "matchup": "Kings @ Wolves",
        "sportsbook": "Pinnacle",
        "spread": "-4.5",
        "total": "222.5",
        "moneyline": "-175",
        "result": "Under, Wolves covered",
    },
]

SAMPLE_INJURIES = [
    {"team": "Bulls", "player": "Lonzo Ball", "status": "OUT", "note": "Knee rehab"},
    {"team": "Knicks", "player": "RJ Barrett", "status": "Q", "note": "Illness"},
    {"team": "Wolves", "player": "Jaden McDaniels", "status": "Q", "note": "Ankle"},
]

SAMPLE_SCHEDULE = [
    {"team": "Bulls", "opponent": "Knicks", "date": "2024-03-12", "home": False},
    {"team": "Bulls", "opponent": "Magic", "date": "2024-03-14", "home": True},
]


def build_prompt_payloads():
    prompt_1 = {
        "results_vs_closing": [
            {
                "team": "Bulls",
                "ATS": "Covered",
                "O/U": "Under",
                "context": "Held opponents to 98 pts; +3.5 spread cashed",
            }
        ],
        "top_trends": [
            "Knicks three straight unders",
            "Wolves 4-1 ATS last five",
            "Thunder +8 rebounding margin over last 3",
        ],
        "bulls_players": [
            {
                "player": p["player"],
                "PTS": p["PTS"],
                "REB": p["REB"],
                "AST": p["AST"],
                "role": p["role"],
                "minutes": p["minutes"],
                "rotation": p["rotation"],
                "injuries": p["injuries"],
                "warnings": [],
            }
            for p in BULLS_PLAYERS
        ],
        "next_day_key_insights": [
            "Monitor back-to-back fatigue for Bulls",
            "Magic trending over on totals last 3",
        ],
    }

    prompt_2 = {
        "results_one_line": [
            "Bulls L 102-104, covered +3.5, Under",
            "Knicks W 112-107, covered -4, Over",
        ],
        "seven_day_trends": [
            "Bulls pace slow, defensive rating improving",
            "Thunder high usage for guards, strong AST%",
        ],
        "bulls_players_form": [
            {
                "player": p["player"],
                "PTS": f"{p['PTS']} (last 5 avg)",
                "REB": f"{p['REB']} (last 5 avg)",
                "AST": f"{p['AST']} (last 5 avg)",
                "role": p["role"],
                "minutes": p["minutes"],
            }
            for p in BULLS_PLAYERS
        ],
        "betting_directions": [
            "Lean Bulls +points if fatigue manageable",
            "Target Wolves unders vs slow teams",
        ],
        "odds_request": "Wrzuć świeże screeny z linii (DraftKings/Bet365) — placeholders used until upload",
    }

    prompt_3 = {
        "todays_slate": [
            {
                "game": "Bulls @ Knicks",
                "time": "7:30 PM ET",
                "injuries": ["LaVine O", "Barrett Q"],
            }
        ],
        "matchup_notes": [
            "Slow pace matchup; rim attempts limited by Knicks",
            "Knicks strong on glass; Bulls must gang rebound",
        ],
        "bulls_scouting": {
            "last_game": "Lost 102-104; offense stalled late",
            "last_five_form": BULLS_PLAYERS,
            "strengths": ["Mid-range scoring", "Defensive rebounding"],
            "weaknesses": ["Point-of-attack defense", "Bench creation"],
            "initial_lean": {
                "market": "Spread",
                "direction": "Bulls +points",
                "justification": "Knicks on 3in4; Bulls defense improving",
            },
        },
        "bet_proposals": {
            "general_parlay": {
                "legs": [
                    {
                        "description": "Knicks moneyline",
                        "odds": "placeholder",
                        "reason": "Home edge, rest advantage",
                        "confidence": "Medium",
                    },
                    {
                        "description": "Wolves-Kings Under",
                        "odds": "placeholder",
                        "reason": "Both on B2B",
                        "confidence": "Medium",
                    },
                    {
                        "description": "Magic +3.5",
                        "odds": "placeholder",
                        "reason": "Opponents missing starting PG",
                        "confidence": "High",
                    },
                ],
                "alt_safe_versions": [
                    "Knicks pk", "Wolves-Kings Under alt", "Magic +6",
                ],
            },
            "bulls_parlay": {
                "legs": [
                    {
                        "description": "Bulls +7.5",
                        "odds": "placeholder",
                        "reason": "Defense trending up",
                        "confidence": "Medium",
                    },
                    {
                        "description": "DeRozan over 22.5 pts",
                        "odds": "placeholder",
                        "reason": "Mid-range matchup favorable",
                        "confidence": "Medium",
                    },
                ],
                "alt_safe_versions": ["Bulls +10", "DeRozan 20+ pts"],
            },
        },
        "risks": [
            "Late scratches",
            "Missing uploaded odds screenshots",
            "Travel fatigue",
        ],
    }

    return {"prompt_1": prompt_1, "prompt_2": prompt_2, "prompt_3": prompt_3}


PROMPT_OUTPUTS = build_prompt_payloads()


PIPELINE_CACHE = {
    "last_run": None,
    "sources": {},
    "games": SAMPLE_RECENT_GAMES,
    "closing_lines": SAMPLE_CLOSING_LINES,
    "injuries": SAMPLE_INJURIES,
    "schedule": SAMPLE_SCHEDULE,
    "prompt_outputs": PROMPT_OUTPUTS,
    "bulls_players": BULLS_PLAYERS,
    "created_at": datetime.utcnow().isoformat(),
}
