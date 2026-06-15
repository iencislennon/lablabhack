"""
agents/energy.py — Energy Agent.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from loguru import logger
from backend.agents.base_agent import BaseAgent
from backend.schemas import EnergyPayload
from backend.config import SYSTEM_PROMPTS


class EnergyAgent(BaseAgent):
    def __init__(self):
        super().__init__("energy")

    async def analyze(self, scenario: str) -> EnergyPayload:
        result = await super().analyze(scenario)
        try:
            payload = EnergyPayload(**result)
            logger.info(f"[energy] ✅ price=${payload.energy_price_usd_kwh}/kWh | alert={payload.shortage_alert}")
            if payload.shortage_alert == "critical":
                logger.warning("⚡ [energy] CRITICAL shortage — human escalation required")
            return payload
        except Exception as e:
            logger.error(f"[energy] Pydantic validation error: {e}")
            raise


async def run_energy_band_agent():
    """Band platform mode — only used by launch_all_band_agents.py."""
    from thenvoi import Agent
    from thenvoi.adapters import AnthropicAdapter
    from thenvoi.config import load_agent_config

    agent_id, api_key = load_agent_config("energy_agent")
    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",
        custom_section=SYSTEM_PROMPTS["energy"] + "\nAfter analysis mention @Coordinator.",
    )
    agent = Agent.create(
        adapter=adapter, agent_id=agent_id, api_key=api_key,
        ws_url=os.getenv("THENVOI_WS_URL"), rest_url=os.getenv("THENVOI_REST_URL"),
    )
    logger.info("⚡ Energy Agent connected to Band. Listening...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(run_energy_band_agent())