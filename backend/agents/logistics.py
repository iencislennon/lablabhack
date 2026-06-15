"""
agents/logistics.py — Logistics Agent.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from loguru import logger
from backend.agents.base_agent import BaseAgent
from backend.schemas import LogisticsPayload
from backend.config import SYSTEM_PROMPTS


class LogisticsAgent(BaseAgent):
    def __init__(self):
        super().__init__("logistics")

    async def analyze(self, scenario: str, farmer_context: dict = None) -> LogisticsPayload:
        extra = ""
        if farmer_context:
            regions = farmer_context.get("deficit_regions", [])
            extra = f"\nDeficit regions from Farmer Agent: {regions}. Prioritise these in the route plan."
        result = await super().analyze(scenario + extra)
        try:
            payload = LogisticsPayload(**result)
            logger.info(f"[logistics] ✅ routes={len(payload.route_plan)} | loss={payload.loss_estimate_pct}%")
            return payload
        except Exception as e:
            logger.error(f"[logistics] Pydantic validation error: {e}")
            raise


async def run_logistics_band_agent():
    """Band platform mode — only used by launch_all_band_agents.py."""
    from thenvoi import Agent
    from thenvoi.adapters import AnthropicAdapter
    from thenvoi.config import load_agent_config

    agent_id, api_key = load_agent_config("logistics_agent")
    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",
        custom_section=SYSTEM_PROMPTS["logistics"] + "\nAfter analysis mention @Coordinator.",
    )
    agent = Agent.create(
        adapter=adapter, agent_id=agent_id, api_key=api_key,
        ws_url=os.getenv("THENVOI_WS_URL"), rest_url=os.getenv("THENVOI_REST_URL"),
    )
    logger.info("🚛 Logistics Agent connected to Band. Listening...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(run_logistics_band_agent())