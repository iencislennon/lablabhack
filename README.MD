# 🌾⚡ FoodEnergyMAS

Multi-Agent System for food and energy security coordination.

**Stack:** Python · FastAPI · Band SDK (thenvoi) · Featherless AI · ChromaDB · React

---

## Project Structure

```
foodenergy-mas/
├── backend/
│   ├── main.py                    # FastAPI + WebSocket orchestrator
│   ├── schemas.py                 # Pydantic models for all agent payloads
│   ├── config.py                  # Models, prompts, escalation thresholds
│   ├── agents/
│   │   ├── base_agent.py          # Featherless AI + ChromaDB RAG base class
│   │   ├── farmer.py              # 🌾 Farmer agent
│   │   ├── logistics.py           # 🚛 Logistics agent
│   │   ├── energy.py              # ⚡ Energy agent
│   │   ├── market.py              # 📈 Market agent
│   │   └── regulator.py           # 🏛️ Regulator agent (final decision-maker)
│   ├── band/
│   │   └── coordinator.py         # Conflict detection, structured debate, audit trail
│   └── vector_db/
│       ├── setup.py               # ChromaDB collection management
│       └── seed_data.py           # Realistic seed data for RAG
├── frontend/
│   └── dashboard.jsx              # React dashboard with live Band Room feed
├── launch_all_band_agents.py      # Launch all 5 Band agents in parallel
├── agent_config.yaml              # Agent UUIDs and API keys (fill in!)
├── .env                           # API keys (fill in!)
└── requirements.txt
```

---

## Quick Start

### 1. Install dependencies

```bash
cd foodenergy-mas
pip install uv
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Band SDK with Anthropic adapter
uv add "band-sdk[claude-sdk]==1.0.0"
```

### 2. Configure environment

Fill in `.env`:
```env
FEATHERLESS_API_KEY=your_key_here
THENVOI_REST_URL=https://app.thenvoi.com/
THENVOI_WS_URL=wss://app.thenvoi.com/api/v1/socket/websocket
```

Fill in `agent_config.yaml` with UUIDs and API keys from app.band.ai/agents.

### 3. Create agents on Band platform

Go to https://app.thenvoi.com/agents → New Agent → Remote Agent.
Create 5 agents: `farmer_agent`, `logistics_agent`, `energy_agent`, `market_agent`, `regulator_agent`.
Copy each agent's UUID and API Key into `agent_config.yaml`.

### 4. Initialize ChromaDB

```bash
# Create collections and load seed data
python -m backend.vector_db.seed_data
```

### 5. Launch Band agents

```bash
# Terminal 1 — all 5 agents connect to the Band platform
python launch_all_band_agents.py
```

### 6. Start FastAPI server

```bash
# Terminal 2
uvicorn backend.main:app --reload
```

### 7. Frontend

Copy `frontend/dashboard.jsx` into a React project or open via Claude Artifacts.

---

## Pipeline Flow

```
Scenario input
   │
   ├── [Parallel] 🌾 FarmerAgent   → ChromaDB RAG → Featherless AI → Band Room
   │              ⚡ EnergyAgent   → ChromaDB RAG → Featherless AI → Band Room
   │
   ├── [Parallel] 🚛 LogisticsAgent (+ farmer data)  → Band Room
   │              📈 MarketAgent   (+ energy data)   → Band Room
   │
   ├── [Coordinator] Conflict detection between agents
   │
   └── 🏛️ RegulatorAgent → synthesize all data → final policy decision
              │
              └── confidence < 0.7 or deficit > 30% → 🚨 Human-in-the-loop
```

## API Endpoints

- `GET /` — health check
- `POST /run` — synchronous pipeline run
- `WS /ws` — real-time WebSocket streaming

---

## Band Room Architecture

Each agent:
1. Connects to Band via WebSocket (`thenvoi.Agent`)
2. Listens for @mentions in the shared room
3. Receives task from coordinator
4. Publishes a typed JSON payload to the Band Room
5. Regulator collects all signals and issues the final policy decision

Human-in-the-loop triggers (defined in `config.py`):
- `confidence_score < 0.70`
- `deficit_pct > 30%`
- `shortage_alert = "critical"`
- `stock_level_days < 14`