"""
agents/regulator.py — Regulator Agent. Final decision-maker.
"""

import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from loguru import logger
from backend.agents.base_agent import BaseAgent
from backend.schemas import RegulatorPayload, BandRoomState
from backend.config import SYSTEM_PROMPTS, ESCALATION_THRESHOLDS


class RegulatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("regulator")

    async def analyze(self, band_room_state: BandRoomState) -> RegulatorPayload:
        sources, context = await self.get_rag_context()

        agents_data = {}
        for name in ["farmer", "logistics", "energy", "market"]:
            val = getattr(band_room_state, name, None)
            if val:
                agents_data[name] = val.model_dump()

        user_message = f"""ALL AGENT DATA (Band Room State):
{json.dumps(agents_data, ensure_ascii=False, indent=2)}

CONFLICTS DETECTED: {band_room_state.conflicts}
DEBATE ROUNDS: {band_room_state.debate_rounds}

Analyse all data, resolve conflicts, issue the final policy decision.
Populate rag_sources with: {sources}
Return ONLY the JSON object."""

        result = await self.run_llm(user_message, context)
        result["rag_sources"] = sources

        try:
            payload = RegulatorPayload(**result)
            t = ESCALATION_THRESHOLDS

            if payload.confidence_score < t["regulator_confidence_min"]:
                payload.escalate_to_human = True
                payload.escalation_reason = f"Confidence {payload.confidence_score:.2f} below threshold {t['regulator_confidence_min']}"

            if band_room_state.farmer and band_room_state.farmer.deficit_pct > t["farmer_deficit_pct_max"]:
                payload.escalate_to_human = True
                payload.escalation_reason = f"Deficit {band_room_state.farmer.deficit_pct}% exceeds threshold {t['farmer_deficit_pct_max']}%"

            if band_room_state.energy and band_room_state.energy.shortage_alert == t["energy_shortage_critical"]:
                payload.escalate_to_human = True
                payload.escalation_reason = "Critical energy shortage — cascading food risk"

            if band_room_state.market and band_room_state.market.stock_level_days < t["market_stock_days_min"]:
                payload.escalate_to_human = True
                payload.escalation_reason = f"Stock {band_room_state.market.stock_level_days}d below critical {t['market_stock_days_min']}d"

            logger.info(f"[regulator] ✅ confidence={payload.confidence_score:.2f} | escalate={payload.escalate_to_human}")
            if payload.escalate_to_human:
                logger.warning(f"🚨 ESCALATION: {payload.escalation_reason}")
            return payload

        except Exception as e:
            logger.error(f"[regulator] Pydantic validation error: {e}")
            raise


async def run_regulator_band_agent():
    """Band platform mode — only used by launch_all_band_agents.py."""
    from thenvoi import Agent
    from thenvoi.adapters import AnthropicAdapter
    from thenvoi.config import load_agent_config

    agent_id, api_key = load_agent_config("regulator_agent")
    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",
        custom_section=SYSTEM_PROMPTS["regulator"] + "\nWait for all agents, then issue the final decision.",
    )
    agent = Agent.create(
        adapter=adapter, agent_id=agent_id, api_key=api_key,
        ws_url=os.getenv("THENVOI_WS_URL"), rest_url=os.getenv("THENVOI_REST_URL"),
    )
    logger.info("🏛️ Regulator Agent connected to Band. Listening...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(run_regulator_band_agent())