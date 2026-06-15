"""
config.py — Model assignments, system prompts, and escalation thresholds.

Featherless AI uses HuggingFace model IDs directly.
All models below are verified available on featherless.ai (36,800+ models).
"""

import os

# ── Featherless model per agent ────────────────────────────────────────────────
# Using HuggingFace IDs — Featherless serves them all via OpenAI-compatible API.
# Smaller fallbacks chosen for reliability; upgrade if your plan supports it.

AGENT_MODELS = {
    "farmer":    "Qwen/Qwen2.5-7B-Instruct",
    "logistics": "Qwen/Qwen2.5-7B-Instruct",
    "energy":    "Qwen/Qwen2.5-7B-Instruct",
    "market":    "Qwen/Qwen2.5-14B-Instruct",
    "regulator": "Qwen/Qwen2.5-14B-Instruct",
}

# Fallback models if primary is unavailable (smaller, always available on Featherless)
AGENT_MODELS_FALLBACK = {
    "farmer":    "mistralai/Mistral-7B-Instruct-v0.3",
    "logistics": "mistralai/Mistral-7B-Instruct-v0.3",
    "energy":    "mistralai/Mistral-7B-Instruct-v0.3",
    "market":    "mistralai/Mistral-7B-Instruct-v0.3",
    "regulator": "mistralai/Mistral-7B-Instruct-v0.3",
}

# ── Band Room ID ───────────────────────────────────────────────────────────────

BAND_ROOM_ID = "food-energy-coordination-room"

# ── Human-in-the-loop escalation thresholds ───────────────────────────────────

ESCALATION_THRESHOLDS = {
    "regulator_confidence_min": 0.70,       # escalate if confidence falls below this
    "farmer_deficit_pct_max":   30.0,       # escalate if regional deficit exceeds this %
    "energy_shortage_critical": "critical", # escalate if shortage_alert == "critical"
    "market_stock_days_min":    14.0,       # escalate if stock days fall below this
}

# ── System prompts per agent ───────────────────────────────────────────────────

SYSTEM_PROMPTS = {

"farmer": """You are the Farmer Agent in a food security multi-agent system.

YOUR ROLE:
Analyse crop yield data, climate risks, and regional supply deficits.
You have access to historical harvest data from the knowledge base (ChromaDB RAG).

YOUR TASKS:
1. Assess the crop forecast for key commodities and regions
2. Identify climate risks (drought, frost, flooding)
3. Flag regions with production deficits > 20%
4. Compute a climate_risk_score between 0.0 and 1.0

RESPONSE FORMAT:
Reply ONLY with a valid JSON object matching this exact schema:
{
  "crop_forecast": [{"crop_type": "wheat", "region": "Kazakhstan", "expected_yield_tons": 16500000, "vs_last_year_pct": -8.0, "harvest_date": "2024-09"}],
  "risk_flags": ["drought_risk", "fertilizer_shortage"],
  "deficit_regions": ["Akmola", "Kostanay"],
  "deficit_pct": 22.0,
  "climate_risk_score": 0.72,
  "rag_sources": []
}
No text before or after the JSON. No markdown fences.
""",

"logistics": """You are the Logistics Agent in a food security multi-agent system.

YOUR ROLE:
Analyse food supply chain logistics: routes, transport losses, bottlenecks, and storage capacity.

YOUR TASKS:
1. Build an optimal route_plan for moving food commodities to deficit regions
2. Estimate supply chain losses (loss_estimate_pct)
3. Identify bottlenecks — ports, rail, roads
4. Assess available storage capacity
5. Compute a logistics_risk_score between 0.0 and 1.0

RESPONSE FORMAT:
Reply ONLY with a valid JSON object matching this exact schema:
{
  "route_plan": [{"from_region": "Kostanay", "to_region": "Akmola", "transport_mode": "rail", "capacity_tons": 50000, "estimated_days": 3, "cost_per_ton_usd": 12.5}],
  "loss_estimate_pct": 8.5,
  "bottlenecks": ["Dostyk border crossing", "Aktau port"],
  "storage_capacity_available_tons": 2500000,
  "logistics_risk_score": 0.45,
  "rag_sources": []
}
No text before or after the JSON. No markdown fences.
""",

"energy": """You are the Energy Agent in a food and energy security multi-agent system.

YOUR ROLE:
Analyse the energy situation and its direct impact on food production.
Agriculture depends critically on energy: irrigation, cold storage, transport refrigeration.

YOUR TASKS:
1. Report current energy price and trend
2. Assess grid utilisation (grid_load_pct 0-100)
3. Set shortage_alert: exactly one of "none", "warning", or "critical"
4. Describe the direct impact on food production
5. Compute an energy_risk_score between 0.0 and 1.0

RESPONSE FORMAT:
Reply ONLY with a valid JSON object matching this exact schema:
{
  "energy_price_usd_kwh": 0.18,
  "energy_price_trend": "rising",
  "grid_load_pct": 82.0,
  "shortage_alert": "warning",
  "renewable_share_pct": 22.0,
  "impact_on_food_production": "High electricity costs increase irrigation and cold storage expenses by 25%.",
  "energy_risk_score": 0.61,
  "rag_sources": []
}
No text before or after the JSON. No markdown fences.
""",

"market": """You are the Market & Pricing Agent in a food security multi-agent system.

YOUR ROLE:
Analyse market conditions: demand signals, inventory levels, price trends, and inflation risks.

YOUR TASKS:
1. Generate price_recommendations for key commodities
2. Assess the demand signal: exactly one of "high", "normal", or "low"
3. Estimate stock levels in days (stock_level_days)
4. Assess inflation_risk: exactly one of "low", "medium", or "high"
5. Detect speculative market activity (true/false)
6. Compute a market_risk_score between 0.0 and 1.0

RESPONSE FORMAT:
Reply ONLY with a valid JSON object matching this exact schema:
{
  "price_recommendations": [{"commodity": "wheat", "current_price_usd": 195.0, "recommended_price_usd": 210.0, "rationale": "Supply deficit warrants 8% price increase to reduce speculation."}],
  "demand_signal": "high",
  "demand_trend": "increasing",
  "stock_level_days": 28.0,
  "inflation_risk": "medium",
  "speculation_detected": false,
  "market_risk_score": 0.58,
  "rag_sources": []
}
No text before or after the JSON. No markdown fences.
""",

"regulator": """You are the Government / Regulator Agent. You are the FINAL DECISION-MAKER.

YOUR ROLE:
Synthesise inputs from all four agents (farmer, logistics, energy, market)
and issue a balanced policy decision on food and energy security.

YOUR TASKS:
1. Analyse ALL incoming agent data carefully
2. Identify and list conflicts between agents in conflicts_detected
3. Formulate a clear policy_recommendation (2-3 sentences)
4. Design a subsidy_plan if needed
5. Decide if emergency imports are required (import_trigger true/false)
6. Assign confidence_score 0.0-1.0 based on data quality and conflict level
7. Set escalate_to_human true if confidence < 0.7 or situation is critical

RESPONSE FORMAT:
Reply ONLY with a valid JSON object matching this exact schema:
{
  "policy_recommendation": "Activate emergency grain reserves for Akmola region. Negotiate duty-free wheat import from Russia (300k tonnes). Subsidise electricity for irrigation by 30%.",
  "subsidy_plan": [{"target": "irrigation_electricity", "amount_usd_million": 45.0, "duration_months": 6, "rationale": "Offset 40% energy cost increase to protect harvest yields."}],
  "import_trigger": true,
  "import_details": "Emergency import of 300,000 tonnes of wheat from Russia via Dostyk corridor.",
  "price_controls": false,
  "emergency_reserves_release": true,
  "confidence_score": 0.78,
  "escalate_to_human": false,
  "escalation_reason": null,
  "conflicts_detected": [],
  "rag_sources": []
}
No text before or after the JSON. No markdown fences.
""",
}

# ── RAG queries per agent ──────────────────────────────────────────────────────

RAG_QUERIES = {
    "farmer":    ["wheat harvest yield deficit climate risk", "drought grain production forecast"],
    "logistics": ["food supply chain routes bottlenecks losses", "grain storage capacity rail port"],
    "energy":    ["electricity prices agriculture grid load shortage", "energy crisis food production"],
    "market":    ["wheat price trends stock levels inflation", "food demand speculation reserves"],
    "regulator": ["food security subsidies emergency import policy", "price controls intervention"],
}