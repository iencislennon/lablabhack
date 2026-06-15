"""
schemas.py — Pydantic models for all agent payloads.
Each agent publishes a strictly typed object to the Band Room.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


# ── Shared types ───────────────────────────────────────────────────────────────

class RiskLevel(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Farmer agent ───────────────────────────────────────────────────────────────

class CropForecast(BaseModel):
    crop_type: str                          # e.g. "wheat", "corn", "rice"
    region: str
    expected_yield_tons: float
    vs_last_year_pct: float                 # % change vs previous year
    harvest_date: str


class FarmerPayload(BaseModel):
    agent: Literal["farmer"] = "farmer"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])

    crop_forecast: list[CropForecast]
    risk_flags: list[str]                   # e.g. ["drought_risk", "frost_risk"]
    deficit_regions: list[str]              # regions with deficit > 20%
    deficit_pct: float                      # maximum regional deficit %
    climate_risk_score: float               # 0.0 – 1.0
    rag_sources: list[str] = []             # source doc IDs from ChromaDB


# ── Logistics agent ────────────────────────────────────────────────────────────

class Route(BaseModel):
    from_region: str
    to_region: str
    transport_mode: str                     # "rail", "road", "sea"
    capacity_tons: float
    estimated_days: int
    cost_per_ton_usd: float


class LogisticsPayload(BaseModel):
    agent: Literal["logistics"] = "logistics"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])

    route_plan: list[Route]
    loss_estimate_pct: float                # % loss in the supply chain
    bottlenecks: list[str]                  # e.g. ["port_odessa", "rail_kharkiv"]
    storage_capacity_available_tons: float
    logistics_risk_score: float             # 0.0 – 1.0
    rag_sources: list[str] = []


# ── Energy agent ───────────────────────────────────────────────────────────────

class EnergyPayload(BaseModel):
    agent: Literal["energy"] = "energy"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])

    energy_price_usd_kwh: float             # current electricity price
    energy_price_trend: str                 # "rising", "stable", "falling"
    grid_load_pct: float                    # grid utilisation 0–100%
    shortage_alert: str                     # "none", "warning", "critical"
    renewable_share_pct: float              # share of renewable energy
    impact_on_food_production: str          # description of impact on agriculture
    energy_risk_score: float                # 0.0 – 1.0
    rag_sources: list[str] = []


# ── Market agent ───────────────────────────────────────────────────────────────

class PriceRecommendation(BaseModel):
    commodity: str
    current_price_usd: float
    recommended_price_usd: float
    rationale: str


class MarketPayload(BaseModel):
    agent: Literal["market"] = "market"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])

    price_recommendations: list[PriceRecommendation]
    demand_signal: str                      # "high", "normal", "low"
    demand_trend: str                       # "increasing", "stable", "decreasing"
    stock_level_days: float                 # days of supply remaining
    inflation_risk: str                     # "low", "medium", "high"
    speculation_detected: bool
    market_risk_score: float                # 0.0 – 1.0
    rag_sources: list[str] = []


# ── Regulator agent ────────────────────────────────────────────────────────────

class SubsidyPlan(BaseModel):
    target: str                             # e.g. "wheat_farmers", "fuel_subsidies"
    amount_usd_million: float
    duration_months: int
    rationale: str


class RegulatorPayload(BaseModel):
    agent: Literal["regulator"] = "regulator"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])

    policy_recommendation: str             # main policy decision in plain text
    subsidy_plan: list[SubsidyPlan]
    import_trigger: bool                   # whether emergency import is needed
    import_details: Optional[str] = None
    price_controls: bool                   # whether price controls are needed
    emergency_reserves_release: bool
    confidence_score: float                # 0.0 – 1.0
    escalate_to_human: bool               # human-in-the-loop trigger
    escalation_reason: Optional[str] = None
    conflicts_detected: list[str] = []    # conflicts identified between agents
    rag_sources: list[str] = []


# ── Band Room — aggregated state ───────────────────────────────────────────────

class BandRoomState(BaseModel):
    """Full Band Room state after all agents have published."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    farmer: Optional[FarmerPayload] = None
    logistics: Optional[LogisticsPayload] = None
    energy: Optional[EnergyPayload] = None
    market: Optional[MarketPayload] = None
    regulator: Optional[RegulatorPayload] = None

    conflicts: list[str] = []
    debate_rounds: int = 0
    final_decision_ready: bool = False