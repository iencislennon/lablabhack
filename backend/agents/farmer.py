"""
agents/farmer.py — Farmer Agent.
Connects to Band via AnthropicAdapter; uses Featherless AI for analysis.
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from loguru import logger

from band import Agent
from band.adapters import AnthropicAdapter
from band.config import load_agent_config

from backend.agents.base_agent import BaseAgent
from backend.schemas import FarmerPayload
from backend.config import SYSTEM_PROMPTS

load_dotenv()


class FarmerAgent(BaseAgent):
    def __init__(self):
        super().__init__("farmer")

    async def analyze(self, scenario: str) -> FarmerPayload:
        result = await super().analyze(scenario)
        # Validate against the Pydantic schema
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


# ── Band SDK — run agent as a persistent Band platform participant ──────────────

async def run_farmer_band_agent():
    """
    Starts the Farmer Agent as a persistent Band agent.
    The agent listens on the Band Room and responds to @mentions.
    """
    load_dotenv()
    agent_id, api_key = load_agent_config("farmer_agent")

    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",  # Band protocol fallback model
        custom_section=SYSTEM_PROMPTS["farmer"] + """

BAND ROOM INSTRUCTIONS:
When mentioned (@FarmerAgent or @farmer), run your analysis on the given scenario.
Return structured JSON with crop forecasts, risk flags, and regional deficits.
After completing your analysis, mention @Coordinator with your results.
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