"""
main.py — FastAPI orchestrator.
Runs all 5 agents in parallel, coordinates via the Band Room,
and streams events to the frontend over WebSocket.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from loguru import logger
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents.farmer import FarmerAgent
from backend.agents.logistics import LogisticsAgent
from backend.agents.energy import EnergyAgent
from backend.agents.market import MarketAgent
from backend.agents.regulator import RegulatorAgent
from backend.band.coordinator import BandCoordinator
from backend.schemas import BandRoomState

load_dotenv()

# ── WebSocket connection manager ───────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)
        logger.info(f"WS connected ({len(self.active_connections)} total)")

    def disconnect(self, ws: WebSocket):
        self.active_connections.remove(ws)

    async def broadcast(self, data: dict):
        """Send an event to all connected clients."""
        message = json.dumps(data, ensure_ascii=False)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass


manager = ConnectionManager()


# ── FastAPI app ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 FoodEnergyMAS starting up...")
    yield
    logger.info("👋 FoodEnergyMAS shutting down")


app = FastAPI(
    title="FoodEnergyMAS",
    description="Multi-Agent System for Food & Energy Security",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request schema ─────────────────────────────────────────────────────────────

class RunRequest(BaseModel):
    scenario: str = "Analyse current food and energy security conditions"


# ── Main pipeline orchestrator ─────────────────────────────────────────────────

async def run_pipeline(scenario: str, broadcast) -> BandRoomState:
    """
    Full pipeline:
    Phase 1 — Parallel: FarmerAgent + EnergyAgent (independent)
    Phase 2 — Parallel: LogisticsAgent + MarketAgent (depend on Phase 1)
    Phase 3 — Coordinator: conflict detection
    Phase 4 — RegulatorAgent: final policy decision
    Phase 5 — Done: broadcast result and audit trail
    """
    coordinator = BandCoordinator()

    await broadcast({"event": "pipeline_start", "scenario": scenario})

    # ── Phase 1: independent agents run in parallel ────────────────────────────

    await broadcast({"event": "phase", "phase": 1, "label": "Independent agents"})

    farmer_agent = FarmerAgent()
    energy_agent = EnergyAgent()

    farmer_task = asyncio.create_task(farmer_agent.analyze(scenario))
    energy_task = asyncio.create_task(energy_agent.analyze(scenario))

    farmer_result, energy_result = await asyncio.gather(farmer_task, energy_task)

    coordinator.receive("farmer", farmer_result)
    await broadcast({"event": "agent_done", "agent": "farmer", "data": farmer_result.model_dump()})

    coordinator.receive("energy", energy_result)
    await broadcast({"event": "agent_done", "agent": "energy", "data": energy_result.model_dump()})

    # ── Phase 2: dependent agents use Phase 1 outputs ─────────────────────────

    await broadcast({"event": "phase", "phase": 2, "label": "Dependent agents"})

    logistics_agent = LogisticsAgent()
    market_agent = MarketAgent()

    logistics_task = asyncio.create_task(
        logistics_agent.analyze(scenario, farmer_context=farmer_result.model_dump())
    )
    market_task = asyncio.create_task(
        market_agent.analyze(scenario, energy_context=energy_result.model_dump())
    )

    logistics_result, market_result = await asyncio.gather(logistics_task, market_task)

    coordinator.receive("logistics", logistics_result)
    await broadcast({"event": "agent_done", "agent": "logistics", "data": logistics_result.model_dump()})

    coordinator.receive("market", market_result)
    await broadcast({"event": "agent_done", "agent": "market", "data": market_result.model_dump()})

    # ── Phase 3: conflict detection ────────────────────────────────────────────

    await broadcast({"event": "phase", "phase": 3, "label": "Band Room — conflict detection"})

    conflicts = coordinator.detect_conflicts()
    await broadcast({"event": "band_room_conflicts", "conflicts": conflicts, "count": len(conflicts)})

    # ── Phase 4: regulator issues final decision ───────────────────────────────

    await broadcast({"event": "phase", "phase": 4, "label": "Regulator making decision"})

    regulator_agent = RegulatorAgent()
    regulator_result = await regulator_agent.analyze(coordinator.state)

    coordinator.receive("regulator", regulator_result)
    await broadcast({"event": "agent_done", "agent": "regulator", "data": regulator_result.model_dump()})

    # ── Phase 5: finalise and broadcast audit ──────────────────────────────────

    coordinator.state.final_decision_ready = True
    audit = coordinator.generate_audit_report()

    await broadcast({
        "event": "pipeline_complete",
        "final_decision": regulator_result.policy_recommendation,
        "escalate_to_human": regulator_result.escalate_to_human,
        "escalation_reason": regulator_result.escalation_reason,
        "confidence_score": regulator_result.confidence_score,
        "audit_trail": audit,
    })

    logger.info("✅ Pipeline complete")
    return coordinator.state


# ── API endpoints ──────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "ok", "service": "FoodEnergyMAS"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/run")
async def run_sync(request: RunRequest):
    """Synchronous pipeline run (no WebSocket streaming)."""
    events = []

    async def collect(data: dict):
        events.append(data)

    state = await run_pipeline(request.scenario, collect)

    return {
        "session_id": state.session_id,
        "final_decision": state.regulator.policy_recommendation if state.regulator else None,
        "escalate_to_human": state.regulator.escalate_to_human if state.regulator else False,
        "confidence_score": state.regulator.confidence_score if state.regulator else 0,
        "conflicts": state.conflicts,
        "events": events,
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time Band Room event streaming.
    Client sends a scenario → server streams events as agents complete their work.
    """
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            scenario = request.get("scenario", "Analyse food security conditions")

            async def broadcast(event_data: dict):
                await websocket.send_text(json.dumps(event_data, ensure_ascii=False))

            try:
                await run_pipeline(scenario, broadcast)
            except Exception as e:
                await websocket.send_text(json.dumps({"event": "error", "message": str(e)}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WS client disconnected")


if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(
        "backend.main:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True,
    )