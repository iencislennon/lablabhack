"""
agents/logistics.py — Logistics Agent.
"""

import asyncio
import os
from dotenv import load_dotenv
from loguru import logger

from band import Agent
from band.adapters import AnthropicAdapter
from band.config import load_agent_config

from backend.agents.base_agent import BaseAgent
from backend.schemas import LogisticsPayload
from backend.config import SYSTEM_PROMPTS

load_dotenv()


class LogisticsAgent(BaseAgent):
    def __init__(self):
        super().__init__("logistics")

    async def analyze(self, scenario: str, farmer_context: dict = None) -> LogisticsPayload:
        """
        Analyse logistics, optionally incorporating Farmer Agent data.
        farmer_context — FarmerPayload.dict() if already available.
        """
        extra_context = ""
        if farmer_context:
            deficit_regions = farmer_context.get("deficit_regions", [])
            extra_context = (
                f"\nDeficit regions from Farmer Agent: {deficit_regions}\n"
                "Prioritise these regions when building the route plan."
            )

        result = await super().analyze(scenario + extra_context)

        try:
            payload = LogisticsPayload(**result)
            logger.info(
                f"[logistics] ✅ routes={len(payload.route_plan)} | "
                f"loss={payload.loss_estimate_pct}% | "
                f"bottlenecks={payload.bottlenecks}"
            )
            return payload
        except Exception as e:
            logger.error(f"[logistics] Pydantic validation error: {e}")
            raise


async def run_logistics_band_agent():
    load_dotenv()
    agent_id, api_key = load_agent_config("logistics_agent")

    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",
        custom_section=SYSTEM_PROMPTS["logistics"] + """

BAND ROOM INSTRUCTIONS:
When mentioned, analyse supply chain logistics using context from other agents.
Incorporate deficit regions flagged by @FarmerAgent when building routes.
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

    logger.info("🚛 Logistics Agent connected to Band. Listening...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(run_logistics_band_agent())