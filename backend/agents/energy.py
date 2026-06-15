"""
agents/energy.py — Energy Agent.
"""

import asyncio
import os
from dotenv import load_dotenv
from loguru import logger

from band import Agent
from band.adapters import AnthropicAdapter
from band.config import load_agent_config

from backend.agents.base_agent import BaseAgent
from backend.schemas import EnergyPayload
from backend.config import SYSTEM_PROMPTS

load_dotenv()


class EnergyAgent(BaseAgent):
    def __init__(self):
        super().__init__("energy")

    async def analyze(self, scenario: str) -> EnergyPayload:
        result = await super().analyze(scenario)

        try:
            payload = EnergyPayload(**result)
            logger.info(
                f"[energy] ✅ price=${payload.energy_price_usd_kwh}/kWh | "
                f"grid_load={payload.grid_load_pct}% | "
                f"shortage_alert={payload.shortage_alert}"
            )

            # Warn loudly on critical shortage — triggers human escalation
            if payload.shortage_alert == "critical":
                logger.warning("⚡ [energy] CRITICAL shortage alert! Human escalation required.")

            return payload
        except Exception as e:
            logger.error(f"[energy] Pydantic validation error: {e}")
            raise


async def run_energy_band_agent():
    load_dotenv()
    agent_id, api_key = load_agent_config("energy_agent")

    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",
        custom_section=SYSTEM_PROMPTS["energy"] + """

BAND ROOM INSTRUCTIONS:
Analyse the energy situation and its impact on food production.
shortage_alert = "critical" means immediate escalation to a human decision-maker.
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

    logger.info("⚡ Energy Agent connected to Band. Listening...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(run_energy_band_agent())