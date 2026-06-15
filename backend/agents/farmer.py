"""
agents/farmer.py — Farmer Agent.
Uses Featherless AI + ChromaDB RAG for local analysis (FastAPI pipeline).
Band SDK integration is in run_farmer_band_agent() — only needed for launch_all_band_agents.py.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from loguru import logger
from backend.agents.base_agent import BaseAgent
from backend.schemas import FarmerPayload
from backend.config import SYSTEM_PROMPTS


class FarmerAgent(BaseAgent):
    def __init__(self):
        super().__init__("farmer")

    async def analyze(self, scenario: str) -> FarmerPayload:
        result = await super().analyze(scenario)
        try:
            payload = FarmerPayload(**result)
            logger.info(
                f"[farmer] ✅ crops={len(payload.crop_forecast)} | "
                f"deficit_pct={payload.deficit_pct}% | "
                f"risk_score={payload.climate_risk_score}"
            )
            return payload
        except Exception as e:
            logger.error(f"[farmer] Pydantic validation error: {e}")
            raise


async def run_farmer_band_agent():
    """Band platform mode — only used by launch_all_band_agents.py."""
    # Band SDK imports deferred here so they don't break the FastAPI pipeline
    from thenvoi import Agent
    from thenvoi.adapters import AnthropicAdapter
    from thenvoi.config import load_agent_config

    agent_id, api_key = load_agent_config("farmer_agent")
    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",
        custom_section=SYSTEM_PROMPTS["farmer"] + """
BAND ROOM INSTRUCTIONS:
When mentioned (@FarmerAgent), analyse the scenario and return JSON.
After completing, mention @Coordinator with your results.
""",
    )
    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("THENVOI_WS_URL"),
        rest_url=os.getenv("THENVOI_REST_URL"),
    )
    logger.info("🌾 Farmer Agent connected to Band. Listening...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(run_farmer_band_agent())