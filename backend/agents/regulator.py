"""
agents/regulator.py — Regulator Agent. Final decision-maker.
Synthesises data from all four agents and issues the policy decision.
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
from backend.schemas import RegulatorPayload, BandRoomState
from backend.config import SYSTEM_PROMPTS, ESCALATION_THRESHOLDS

load_dotenv()


class RegulatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("regulator")

    async def analyze(self, band_room_state: BandRoomState) -> RegulatorPayload:
        """
        The Regulator receives the full Band Room state and issues a policy decision.
        """
        sources, context = await self.get_rag_context()

        # Compile all agent outputs into a single prompt
        agents_data = {}
        if band_room_state.farmer:
            agents_data["farmer"] = band_room_state.farmer.model_dump()
        if band_room_state.logistics:
            agents_data["logistics"] = band_room_state.logistics.model_dump()
        if band_room_state.energy:
            agents_data["energy"] = band_room_state.energy.model_dump()
        if band_room_state.market:
            agents_data["market"] = band_room_state.market.model_dump()

        user_message = f"""
ALL AGENT DATA (Band Room State):
{json.dumps(agents_data, ensure_ascii=False, indent=2)}

CONFLICTS DETECTED BY COORDINATOR:
{band_room_state.conflicts}

DEBATE ROUNDS COMPLETED: {band_room_state.debate_rounds}

Your tasks:
1. Analyse ALL data above
2. Identify and resolve conflicts between agents
3. Issue the final policy decision
4. Determine whether human escalation is required

Return JSON matching the RegulatorPayload schema.
Populate rag_sources with: {sources}
"""

        result = await self.run_llm(user_message, context)
        result["rag_sources"] = sources

        try:
            payload = RegulatorPayload(**result)

            # Enforce escalation thresholds regardless of the model's own assessment
            thresholds = ESCALATION_THRESHOLDS

            if payload.confidence_score < thresholds["regulator_confidence_min"]:
                payload.escalate_to_human = True
                payload.escalation_reason = (
                    f"Confidence {payload.confidence_score:.2f} is below threshold "
                    f"{thresholds['regulator_confidence_min']}"
                )

            if band_room_state.farmer and band_room_state.farmer.deficit_pct > thresholds["farmer_deficit_pct_max"]:
                payload.escalate_to_human = True
                payload.escalation_reason = (
                    f"Regional deficit {band_room_state.farmer.deficit_pct}% exceeds "
                    f"threshold {thresholds['farmer_deficit_pct_max']}%"
                )

            if band_room_state.energy and band_room_state.energy.shortage_alert == thresholds["energy_shortage_critical"]:
                payload.escalate_to_human = True
                payload.escalation_reason = "Critical energy shortage — cascading risk to food production"

            if band_room_state.market and band_room_state.market.stock_level_days < thresholds["market_stock_days_min"]:
                payload.escalate_to_human = True
                payload.escalation_reason = (
                    f"Stock level {band_room_state.market.stock_level_days} days is below "
                    f"critical threshold of {thresholds['market_stock_days_min']} days"
                )

            logger.info(
                f"[regulator] ✅ confidence={payload.confidence_score:.2f} | "
                f"escalate={payload.escalate_to_human} | "
                f"import_trigger={payload.import_trigger}"
            )

            if payload.escalate_to_human:
                logger.warning(f"🚨 [regulator] ESCALATION TO HUMAN: {payload.escalation_reason}")

            return payload

        except Exception as e:
            logger.error(f"[regulator] Pydantic validation error: {e}")
            raise


async def run_regulator_band_agent():
    load_dotenv()
    agent_id, api_key = load_agent_config("regulator_agent")

    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",
        custom_section=SYSTEM_PROMPTS["regulator"] + """

BAND ROOM INSTRUCTIONS:
You are the final decision-maker. Wait for data from all four agents:
@FarmerAgent, @LogisticsAgent, @EnergyAgent, @MarketAgent.
When @Coordinator passes you the full context, issue the final policy decision.
If escalation is required, state the reason explicitly in your response.
""",
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("THENVOI_WS_URL"),
        rest_url=os.getenv("THENVOI_REST_URL"),
    )

    logger.info("🏛️ Regulator Agent connected to Band. Listening...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(run_regulator_band_agent())