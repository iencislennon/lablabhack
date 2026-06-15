"""
agents/market.py — Market & Pricing Agent.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from loguru import logger
from backend.agents.base_agent import BaseAgent
from backend.schemas import MarketPayload
from backend.config import SYSTEM_PROMPTS


class MarketAgent(BaseAgent):
    def __init__(self):
        super().__init__("market")

    async def analyze(self, scenario: str, energy_context: dict = None) -> MarketPayload:
        extra = ""
        if energy_context:
            price = energy_context.get("energy_price_usd_kwh", "N/A")
            alert = energy_context.get("shortage_alert", "none")
            extra = f"\nEnergy context: ${price}/kWh, shortage_alert={alert}. Factor into cost estimates."
        result = await super().analyze(scenario + extra)
        try:
            payload = MarketPayload(**result)
            logger.info(f"[market] ✅ demand={payload.demand_signal} | stock={payload.stock_level_days}d")
            if payload.stock_level_days < 14:
                logger.warning(f"🔴 [market] Critical stock: {payload.stock_level_days} days!")
            return payload
        except Exception as e:
            logger.error(f"[market] Pydantic validation error: {e}")
            raise


async def run_market_band_agent():
    """Band platform mode — only used by launch_all_band_agents.py."""
    from thenvoi import Agent
    from thenvoi.adapters import AnthropicAdapter
    from thenvoi.config import load_agent_config

    agent_id, api_key = load_agent_config("market_agent")
    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",
        custom_section=SYSTEM_PROMPTS["market"] + "\nAfter analysis mention @Coordinator.",
    )
    agent = Agent.create(
        adapter=adapter, agent_id=agent_id, api_key=api_key,
        ws_url=os.getenv("THENVOI_WS_URL"), rest_url=os.getenv("THENVOI_REST_URL"),
    )
    logger.info("📈 Market Agent connected to Band. Listening...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(run_market_band_agent())