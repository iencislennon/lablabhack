# 🌾⚡ FoodEnergyMAS

**Multi-Agent System for Food and Energy Security Coordination**

> Five AI agents analyse a crisis scenario simultaneously, detect conflicts between their findings, and produce a final policy recommendation with a downloadable PDF report — in minutes instead of days.

---

## What is this?

FoodEnergyMAS is an AI-powered decision support system built for food and energy security analysts, government advisors, and crisis response teams. You describe a situation — a drought, an energy price spike, a supply chain disruption, or a combination of all three — and the system deploys five specialised AI agents that work in parallel, each focused on their domain.

The agents share their findings in a coordination layer called the **Band Room**, where conflicts between signals are automatically detected. A Regulator agent then synthesises everything into a final policy recommendation. If the system is not confident enough to act — due to conflicting signals or critical thresholds being breached — it escalates to a human decision-maker with a clear explanation of why.

The result is a structured PDF report with crop forecasts, logistics route plans, price recommendations, subsidy proposals, and import trigger assessments.

---

## The five agents

| Agent | Domain | What it analyses |
|---|---|---|
| 🌾 **Farmer** | Agriculture | Crop yields, climate risks, regional deficits |
| 🚛 **Logistics** | Supply chain | Routes, transport losses, storage, bottlenecks |
| ⚡ **Energy** | Power & fuel | Grid load, energy prices, shortage alerts |
| 📈 **Market** | Commodities | Demand signals, stock levels, price trends, speculation |
| 🏛️ **Regulator** | Policy | Final decision — subsidies, imports, reserves, escalation |

---

## Pipeline flow

```
You enter a scenario
        │
        ▼
Phase 1 ── 🌾 Farmer Agent    ─┐  (parallel)
        └── ⚡ Energy Agent   ─┘
        │
        ▼
Phase 2 ── 🚛 Logistics Agent  ─┐  (parallel, uses Phase 1 outputs)
        └── 📈 Market Agent    ─┘
        │
        ▼
Phase 3 ── Coordinator detects conflicts between agents
        │
        ▼
Phase 4 ── 🏛️ Regulator issues final policy decision
        │
        ▼
Phase 5 ── PDF + JSON report generated and saved
```

---

## Human-in-the-loop escalation

The system automatically escalates to a human when:

- Regulator confidence score < **70%**
- Regional food deficit > **30%**
- Energy shortage alert = **critical**
- Stock levels < **14 days**

When escalated, the report clearly states the reason and flags the decision for human review.

---

## Tech stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, WebSocket |
| **AI agents** | Featherless AI (OpenAI-compatible API, open-source LLMs) |
| **Knowledge base** | ChromaDB vector database + RAG (retrieval-augmented generation) |
| **Agent coordination** | Band AI platform (thenvoi SDK) |
| **PDF reports** | WeasyPrint |
| **Frontend** | React 18, CrisisNet Design System |

**Models used:**
- Farmer, Logistics, Energy: `Qwen/Qwen2.5-7B-Instruct`
- Market, Regulator: `Qwen/Qwen2.5-14B-Instruct`
- Fallback (all agents): `mistralai/Mistral-7B-Instruct-v0.3`

---

## Project structure

```
lablab/
├── backend/
│   ├── main.py                    # FastAPI server + pipeline orchestrator
│   ├── schemas.py                 # Typed Pydantic models for all agent payloads
│   ├── config.py                  # Models, system prompts, escalation thresholds
│   ├── report.py                  # Markdown + PDF report generator
│   ├── agents/
│   │   ├── base_agent.py          # Featherless AI + ChromaDB RAG base class
│   │   ├── farmer.py              # Farmer agent
│   │   ├── logistics.py           # Logistics agent
│   │   ├── energy.py              # Energy agent
│   │   ├── market.py              # Market agent
│   │   └── regulator.py           # Regulator agent (final decision-maker)
│   ├── band/
│   │   ├── coordinator.py         # Conflict detection + audit trail
│   │   └── room.py                # In-memory Band Room pub/sub
│   └── vector_db/
│       ├── setup.py               # ChromaDB collection management (singleton)
│       └── seed_data.py           # 30 realistic documents for RAG
├── frontend/
│   └── dashboard.jsx              # React dashboard component
├── design-system/
│   └── ui_kits/foodenergymas/
│       └── index.html             # Full dashboard (open directly in browser)
├── reports/                       # Generated reports saved here
├── chroma_db/                     # Vector database (auto-created)
├── launch_all_band_agents.py      # Start all 5 agents on Band platform
├── agent_config.yaml              # Band agent credentials
├── .env                           # API keys
├── .gitignore
└── requirements.txt
```

---

## Setup

### Prerequisites

- Python 3.11
- Node.js (optional, only for Vite frontend)
- A [Featherless AI](https://featherless.ai) account with API access
- A [Band AI](https://app.band.ai) account with 5 Remote Agents created (optional — only needed for Band platform mode)

### 1. Clone and install

```bash
git clone https://github.com/iencislennon/lablabhack.git
cd lablabhack

python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

pip install -r requirements.txt
pip install weasyprint             # for PDF generation
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
# Featherless AI
FEATHERLESS_API_KEY=your_featherless_api_key_here
FEATHERLESS_BASE_URL=https://api.featherless.ai/v1

# Band Platform (only needed for Band agent mode)
THENVOI_REST_URL=https://app.thenvoi.com/
THENVOI_WS_URL=wss://app.thenvoi.com/api/v1/socket/websocket

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db
```

Get your Featherless API key at [featherless.ai](https://featherless.ai) → Account → API Keys.

### 3. Seed the knowledge base

This loads ~30 realistic documents (FAO data, USDA reports, Central Asia agricultural data) into ChromaDB. Run once:

```bash
python -m backend.vector_db.seed_data
```

Expected output:
```
✅ farmer: 7 documents
✅ logistics: 6 documents
✅ energy: 5 documents
✅ market: 6 documents
✅ regulator: 6 documents
🎉 ChromaDB seeding complete!
```

### 4. Start the backend

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend is now running at `http://localhost:8000`.

### 5. Open the dashboard

```bash
open design-system/ui_kits/foodenergymas/index.html
```

Or with Vite (if you prefer `localhost:5173`):

```bash
cd frontend-app
npm run dev
```

---

## How to use

1. Open the dashboard in your browser
2. Type or select a scenario in the **Scenario** input
3. Click **Run Pipeline**
4. Watch the five agents work in real time in the **Band Room** terminal
5. When complete, the **Final Decision** card appears with the policy recommendation
6. Click **Download Report** to save the PDF to your device

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/health` | Health check |
| `POST` | `/run` | Run full pipeline (synchronous) |
| `WS` | `/ws` | Run pipeline with real-time streaming |
| `GET` | `/reports` | List all generated reports |
| `GET` | `/report/{id}` | View Markdown report |
| `GET` | `/report/{id}/pdf` | Download PDF report |
| `GET` | `/report/{id}/json` | Get raw JSON data |

### Quick test

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"scenario": "Drought in Kazakhstan reduced wheat harvest by 25%. Energy prices up 40%."}'
```

### Download a report

```bash
# List available reports
curl http://localhost:8000/reports

# Download PDF (replace SESSION_ID with actual id)
curl -o report.pdf "http://localhost:8000/report/SESSION_ID/pdf"
```

---

## Band platform mode (optional)

If you want agents to live on the Band platform and respond to @mentions in a shared room:

### 1. Create agents on Band

Go to [app.band.ai/agents](https://app.band.ai/agents) → New Agent → Remote Agent.
Create five agents: `farmer_agent`, `logistics_agent`, `energy_agent`, `market_agent`, `regulator_agent`.
Copy the UUID and API Key for each.

### 2. Fill in agent_config.yaml

```yaml
farmer_agent:
  agent_id: "YOUR_FARMER_AGENT_UUID"
  api_key: "YOUR_FARMER_AGENT_API_KEY"

logistics_agent:
  agent_id: "YOUR_LOGISTICS_AGENT_UUID"
  api_key: "YOUR_LOGISTICS_AGENT_API_KEY"

energy_agent:
  agent_id: "YOUR_ENERGY_AGENT_UUID"
  api_key: "YOUR_ENERGY_AGENT_API_KEY"

market_agent:
  agent_id: "YOUR_MARKET_AGENT_UUID"
  api_key: "YOUR_MARKET_AGENT_API_KEY"

regulator_agent:
  agent_id: "YOUR_REGULATOR_AGENT_UUID"
  api_key: "YOUR_REGULATOR_AGENT_API_KEY"
```

### 3. Launch Band agents

```bash
python launch_all_band_agents.py
```

All five agents connect to the Band platform via WebSocket and listen for messages.

---

## Two modes of operation

| Mode | Command | When to use |
|---|---|---|
| **Local pipeline** | `uvicorn backend.main:app --reload` | Demo, testing, hackathon |
| **Band platform** | `python launch_all_band_agents.py` | Production, live Band Room |

For a full demo you only need the backend + dashboard. Band agents are optional.

---

## Escalation thresholds

Configured in `backend/config.py`:

```python
ESCALATION_THRESHOLDS = {
    "regulator_confidence_min": 0.70,   # escalate if confidence < 70%
    "farmer_deficit_pct_max":   30.0,   # escalate if regional deficit > 30%
    "energy_shortage_critical": "critical",
    "market_stock_days_min":    14.0,   # escalate if stock < 14 days
}
```

---

## Example scenarios

```
Drought in Central Asia reduced wheat harvest by 25%. Energy prices up 40%. Assess food and energy security.

Suez Canal blocked — grain shipments to Middle East disrupted. Local reserves critically low.

Speculative trading pushed wheat prices to a 3-year high. Small farmers cannot afford inputs.

Ukraine conflict escalation cuts corn exports by 35%. Energy grid attacks reduce cold chain capacity.
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `All models failed` | Featherless API key expired or plan issue | Check billing at featherless.ai |
| `ModuleNotFoundError: loguru` | Running wrong Python (system vs venv) | Use `python -m uvicorn ...` not `uvicorn ...` |
| `ChromaDB collection empty` | seed_data.py not run | Run `python -m backend.vector_db.seed_data` |
| `Illegal header value` | Trailing space in agent API key | Open `agent_config.yaml` and remove spaces after keys |
| `PDF not downloading` | weasyprint not installed | Run `pip install weasyprint` |
| `401 Unauthorized (Band)` | Wrong agent credentials | Re-check UUIDs and API keys in `agent_config.yaml` |

---

## Built at

**lablab.ai Hackathon** — Band AI Track

**Stack:** Band AI · Featherless AI · ChromaDB · FastAPI · React · WeasyPrint

**Team:** Ansar Tleubayev

---

*FoodEnergyMAS — turning crisis scenarios into policy recommendations, one agent at a time.*
