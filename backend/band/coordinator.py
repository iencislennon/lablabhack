"""
band/coordinator.py — Band Room Coordinator.
Aggregates agent results, detects conflicts, and drives structured debate.
"""

import json
from loguru import logger
from backend.schemas import (
    BandRoomState,
    FarmerPayload,
    LogisticsPayload,
    EnergyPayload,
    MarketPayload,
    RegulatorPayload,
)


class BandCoordinator:
    """
    The Coordinator reads all agent publications from the Band Room,
    identifies conflicts, and aggregates them into a BandRoomState
    ready for the Regulator Agent.
    """

    def __init__(self):
        self.state = BandRoomState()
        self.audit_trail: list[dict] = []

    def log_action(self, agent: str, action: str, details: str = ""):
        """Record every action to the audit trail."""
        entry = {
            "agent": agent,
            "action": action,
            "details": details,
            "timestamp": self.state.created_at,
        }
        self.audit_trail.append(entry)
        logger.info(f"[coordinator] 📋 {agent} → {action} | {details}")

    def receive(self, agent_name: str, payload):
        """Accept a publication from an agent and store it in the room state."""
        if agent_name == "farmer":
            self.state.farmer = payload
        elif agent_name == "logistics":
            self.state.logistics = payload
        elif agent_name == "energy":
            self.state.energy = payload
        elif agent_name == "market":
            self.state.market = payload
        elif agent_name == "regulator":
            self.state.regulator = payload

        self.log_action(agent_name, "published", f"payload_id={payload.message_id}")

    def detect_conflicts(self) -> list[str]:
        """
        Detect contradictions between agent assessments.
        A conflict is any case where one agent's signal contradicts another's.
        """
        conflicts = []
        s = self.state

        # Conflict 1: logistics risk is low, but farmers report a deficit > 30%
        if s.farmer and s.logistics:
            if s.farmer.deficit_pct > 30 and s.logistics.logistics_risk_score < 0.3:
                conflicts.append(
                    f"CONFLICT: Farmer Agent reports a {s.farmer.deficit_pct}% deficit, "
                    f"but Logistics Agent rates risk as low ({s.logistics.logistics_risk_score}). "
                    "Logistics may be underestimating urgency."
                )

        # Conflict 2: market recommends price cuts while stock levels are critical
        if s.market:
            if s.market.stock_level_days < 14:
                for rec in s.market.price_recommendations:
                    if rec.recommended_price_usd < rec.current_price_usd:
                        conflicts.append(
                            f"CONFLICT: Market Agent recommends cutting the price of {rec.commodity} "
                            f"while stock levels are critical ({s.market.stock_level_days} days). "
                            "Lower prices during a shortage will amplify demand and worsen the situation."
                        )

        # Conflict 3: critical energy shortage, but regulator has not triggered reserves
        if s.energy and s.regulator:
            if s.energy.shortage_alert == "critical" and not s.regulator.emergency_reserves_release:
                conflicts.append(
                    "CONFLICT: Energy Agent signals a critical shortage, "
                    "but Regulator has not triggered emergency reserve release."
                )

        # Conflict 4: speculation detected but regulator is adding subsidies (risks amplifying speculation)
        if s.market and s.regulator:
            if s.market.speculation_detected and s.regulator.subsidy_plan:
                conflicts.append(
                    "CONFLICT: Market Agent detected speculative activity, "
                    "but Regulator proposes subsidies that could further fuel speculation."
                )

        self.state.conflicts = conflicts

        if conflicts:
            logger.warning(f"[coordinator] ⚠️ {len(conflicts)} conflict(s) detected")
            for c in conflicts:
                self.log_action("coordinator", "conflict_detected", c[:100])
        else:
            logger.info("[coordinator] ✅ No conflicts detected")

        return conflicts

    def is_ready_for_regulator(self) -> bool:
        """Returns True when all four primary agents have published."""
        s = self.state
        ready = all([s.farmer, s.logistics, s.energy, s.market])
        if ready:
            logger.info("[coordinator] ✅ All 4 agents published — ready for Regulator")
        return ready

    def get_summary_for_regulator(self) -> str:
        """Build a brief summary of the room state to hand off to the Regulator."""
        s = self.state
        lines = ["═══ BAND ROOM SUMMARY ═══"]

        if s.farmer:
            lines.append(f"🌾 Farmer:    deficit={s.farmer.deficit_pct}% | risk={s.farmer.climate_risk_score}")
        if s.logistics:
            lines.append(f"🚛 Logistics: loss={s.logistics.loss_estimate_pct}% | risk={s.logistics.logistics_risk_score}")
        if s.energy:
            lines.append(f"⚡ Energy:    price=${s.energy.energy_price_usd_kwh}/kWh | alert={s.energy.shortage_alert}")
        if s.market:
            lines.append(f"📈 Market:    demand={s.market.demand_signal} | stock={s.market.stock_level_days}d | inflation={s.market.inflation_risk}")

        if self.state.conflicts:
            lines.append(f"\n⚠️ CONFLICTS: {len(self.state.conflicts)}")
            for c in self.state.conflicts:
                lines.append(f"  • {c}")

        return "\n".join(lines)

    def generate_audit_report(self) -> dict:
        """Return the full audit trail for logging and compliance."""
        return {
            "session_id": self.state.session_id,
            "debate_rounds": self.state.debate_rounds,
            "conflicts_found": len(self.state.conflicts),
            "final_decision": self.state.regulator.policy_recommendation if self.state.regulator else None,
            "escalated": self.state.regulator.escalate_to_human if self.state.regulator else False,
            "audit_trail": self.audit_trail,
        }