import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from data.sample_data import FOCUS_TEAMS, PIPELINE_CACHE, build_prompt_payloads
from backend.app.services import analytics, data_sources


class DataPipeline:
    def __init__(self, cache_path: Path, allow_network: bool = True) -> None:
        self.cache_path = cache_path
        self.allow_network = allow_network
        self.state: Dict = PIPELINE_CACHE.copy()
        self.state.setdefault("prompt_outputs", build_prompt_payloads())
        if cache_path.exists():
            try:
                self.state.update(json.loads(cache_path.read_text()))
            except Exception:  # noqa: BLE001
                pass

    async def refresh(self) -> Dict:
        tasks: List = [
            data_sources.fetch_basketball_reference_snapshot(self.allow_network),
            data_sources.fetch_vegasinsider_lines(self.allow_network),
            data_sources.fetch_nba_injuries(self.allow_network),
        ]
        br_data, vi_data, injuries_data = await data_sources.run_parallel(*tasks)

        games = br_data.get("games", [])
        lines = vi_data.get("lines", [])
        injuries = injuries_data.get("injuries", [])

        analysis = analytics.build_analysis(games, lines, injuries, self.state.get("bulls_players", []))

        self.state.update(
            {
                "last_run": datetime.utcnow().isoformat(),
                "sources": {
                    "basketball_reference": br_data,
                    "vegasinsider": vi_data,
                    "nba_injuries": injuries_data,
                },
                "games": games,
                "closing_lines": lines,
                "injuries": injuries,
                "prompt_outputs": analysis["prompt_outputs"],
                "focus_teams": FOCUS_TEAMS,
            }
        )

        self._persist()
        return self.state

    def _persist(self) -> None:
        try:
            self.cache_path.write_text(json.dumps(self.state, indent=2))
        except Exception:  # noqa: BLE001
            pass

    def get_status(self) -> Dict:
        return {
            "last_run": self.state.get("last_run"),
            "sources": self.state.get("sources", {}),
            "allow_network": self.allow_network,
        }

    def get_analysis(self) -> Dict:
        return analytics.build_analysis(
            self.state.get("games", []),
            self.state.get("closing_lines", []),
            self.state.get("injuries", []),
            self.state.get("bulls_players", []),
        )

    def prompt_payloads(self) -> Dict:
        return self.state.get("prompt_outputs", build_prompt_payloads())


def build_pipeline() -> DataPipeline:
    cache_path = Path(__file__).resolve().parents[2] / "data" / "pipeline_cache.json"
    allow_network = os.getenv("PIPELINE_OFFLINE", "0") != "1"
    pipeline = DataPipeline(cache_path=cache_path, allow_network=allow_network)
    return pipeline
