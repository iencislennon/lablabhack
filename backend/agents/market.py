"""
agents/market.py — Market & Pricing Agent.
"""

import asyncio
import os
from dotenv import load_dotenv
from loguru import logger

from band import Agent
from band.adapters import AnthropicAdapter
from band.config import load_agent_config

from backend.agents.base_agent import BaseAgent
from backend.schemas import MarketPayload
from backend.config import SYSTEM_PROMPTS

load_dotenv()


class MarketAgent(BaseAgent):
    def __init__(self):
        super().__init__("market")

    async def analyze(self, scenario: str, energy_context: dict = None) -> MarketPayload:
        """
        Analyse market conditions, optionally incorporating Energy Agent data.
        """
        extra_context = ""
        if energy_context:
            price = energy_context.get("energy_price_usd_kwh", "N/A")
            alert = energy_context.get("shortage_alert", "none")
            extra_context = (
                f"\nEnergy Agent data: price ${price}/kWh, shortage_alert={alert}. "
                "Factor this into cost-of-production estimates."
            )

        result = await super().analyze(scenario + extra_context)

        try:
            payload = MarketPayload(**result)
            logger.info(
                f"[market] ✅ demand={payload.demand_signal} | "
                f"stock_days={payload.stock_level_days} | "
                f"inflation_risk={payload.inflation_risk}"
            )

            if payload.stock_level_days < 14:
                logger.warning(f"🔴 [market] Critical stock level: {payload.stock_level_days} days!")

            return payload
        except Exception as e:
            logger.error(f"[market] Pydantic validation error: {e}")
            raise


async def run_market_band_agent():
    load_dotenv()
    agent_id, api_key = load_agent_config("market_agent")

    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",
        custom_section=SYSTEM_PROMPTS["market"] + """

BAND ROOM INSTRUCTIONS:
Analyse market conditions using data from other agents.
stock_level_days < 14 is a critical threshold — flag it explicitly.
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

    logger.info("📈 Market Agent connected to Band. Listening...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(run_market_band_agent())