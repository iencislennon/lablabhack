"""
main.py — FastAPI orchestrator.
Runs all 5 agents in parallel, coordinates via the Band Room,
streams events over WebSocket, and generates a Markdown+JSON report.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from loguru import logger
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse
from pydantic import BaseModel

from backend.agents.farmer import FarmerAgent
from backend.agents.logistics import LogisticsAgent
from backend.agents.energy import EnergyAgent
from backend.agents.market import MarketAgent
from backend.agents.regulator import RegulatorAgent
from backend.band.coordinator import BandCoordinator
from backend.report import generate_report
from backend.schemas import BandRoomState

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# ── WebSocket connection manager ───────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)
        logger.info(f"WS connected ({len(self.active_connections)} total)")

    def disconnect(self, ws: WebSocket):
        if ws in self.active_connections:
            self.active_connections.remove(ws)

    async def broadcast(self, data: dict):
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


# ── Pipeline ───────────────────────────────────────────────────────────────────

async def run_pipeline(scenario: str, broadcast) -> BandRoomState:
    """
    5-phase pipeline:
    1. Farmer + Energy in parallel (independent)
    2. Logistics + Market in parallel (use phase 1 outputs)
    3. Coordinator conflict detection
    4. Regulator final decision
    5. Report generation + broadcast
    """
    coordinator = BandCoordinator()

    await broadcast({"event": "pipeline_start", "scenario": scenario})

    # ── Phase 1 ───────────────────────────────────────────────────────────────
    await broadcast({"event": "phase", "phase": 1, "label": "Independent agents"})

    farmer_task = asyncio.create_task(FarmerAgent().analyze(scenario))
    energy_task = asyncio.create_task(EnergyAgent().analyze(scenario))
    farmer_result, energy_result = await asyncio.gather(farmer_task, energy_task)

    coordinator.receive("farmer", farmer_result)
    await broadcast({"event": "agent_done", "agent": "farmer", "data": farmer_result.model_dump()})

    coordinator.receive("energy", energy_result)
    await broadcast({"event": "agent_done", "agent": "energy", "data": energy_result.model_dump()})

    # ── Phase 2 ───────────────────────────────────────────────────────────────
    await broadcast({"event": "phase", "phase": 2, "label": "Dependent agents"})

    logistics_task = asyncio.create_task(
        LogisticsAgent().analyze(scenario, farmer_context=farmer_result.model_dump())
    )
    market_task = asyncio.create_task(
        MarketAgent().analyze(scenario, energy_context=energy_result.model_dump())
    )
    logistics_result, market_result = await asyncio.gather(logistics_task, market_task)

    coordinator.receive("logistics", logistics_result)
    await broadcast({"event": "agent_done", "agent": "logistics", "data": logistics_result.model_dump()})

    coordinator.receive("market", market_result)
    await broadcast({"event": "agent_done", "agent": "market", "data": market_result.model_dump()})

    # ── Phase 3 ───────────────────────────────────────────────────────────────
    await broadcast({"event": "phase", "phase": 3, "label": "Conflict detection"})

    conflicts = coordinator.detect_conflicts()
    await broadcast({"event": "band_room_conflicts", "conflicts": conflicts, "count": len(conflicts)})

    # ── Phase 4 ───────────────────────────────────────────────────────────────
    await broadcast({"event": "phase", "phase": 4, "label": "Regulator decision"})

    regulator_result = await RegulatorAgent().analyze(coordinator.state)
    coordinator.receive("regulator", regulator_result)
    await broadcast({"event": "agent_done", "agent": "regulator", "data": regulator_result.model_dump()})

    # ── Phase 5: report ────────────────────────────────────────────────────────
    coordinator.state.final_decision_ready = True
    audit = coordinator.generate_audit_report()

    report_path = generate_report(coordinator.state, scenario, audit)
    session_id  = coordinator.state.session_id
    logger.info(f"📄 Report saved: {report_path}")

    await broadcast({
        "event": "pipeline_complete",
        "final_decision":   regulator_result.policy_recommendation,
        "escalate_to_human": regulator_result.escalate_to_human,
        "escalation_reason": regulator_result.escalation_reason,
        "confidence_score":  regulator_result.confidence_score,
        "import_trigger":    regulator_result.import_trigger,
        "price_controls":    regulator_result.price_controls,
        "emergency_reserves": regulator_result.emergency_reserves_release,
        "subsidy_plan":      [s.model_dump() for s in regulator_result.subsidy_plan],
        "conflicts":         conflicts,
        "session_id":        session_id,
        "report_url":        f"/report/{session_id}",
        "audit_trail":       audit,
    })

    logger.info("✅ Pipeline complete")
    return coordinator.state


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "ok", "service": "FoodEnergyMAS"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/run")
async def run_sync(request: RunRequest):
    """Synchronous pipeline run — returns full result including report URL."""
    events = []

    async def collect(data: dict):
        events.append(data)

    state = await run_pipeline(request.scenario, collect)
    sid   = state.session_id

    return {
        "session_id":       sid,
        "report_url":       f"/report/{sid}",
        "final_decision":   state.regulator.policy_recommendation if state.regulator else None,
        "escalate_to_human": state.regulator.escalate_to_human if state.regulator else False,
        "confidence_score": state.regulator.confidence_score if state.regulator else 0,
        "conflicts":        state.conflicts,
        "events":           events,
    }


@app.get("/report/{session_id}", response_class=PlainTextResponse)
async def get_report_md(session_id: str):
    """Return the Markdown report for a given session."""
    sid  = session_id[:8]
    path = REPORTS_DIR / f"report_{sid}.md"
    if not path.exists():
        return PlainTextResponse("Report not found", status_code=404)
    return PlainTextResponse(path.read_text(encoding="utf-8"), media_type="text/markdown")


@app.get("/report/{session_id}/json")
async def get_report_json(session_id: str):
    """Return the raw JSON data for a given session."""
    sid  = session_id[:8]
    path = REPORTS_DIR / f"report_{sid}.json"
    if not path.exists():
        return {"error": "Report not found"}
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/reports")
async def list_reports():
    """List all available reports."""
    files = sorted(REPORTS_DIR.glob("report_*.md"), reverse=True)
    return [
        {"session_id": f.stem.replace("report_", ""), "url": f"/report/{f.stem.replace('report_', '')}"}
        for f in files[:20]
    ]


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint — streams pipeline events in real time."""
    await manager.connect(websocket)
    try:
        while True:
            data     = await websocket.receive_text()
            request  = json.loads(data)
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
    import uvicorn, os
    uvicorn.run(
        "backend.main:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True,
    )


@app.get("/report/{session_id}/pdf")
async def get_report_pdf(session_id: str):
    """Generate and download a PDF version of the report."""
    from backend.report import generate_pdf
    from fastapi.responses import FileResponse as FR
    pdf_path = generate_pdf(session_id)
    if not pdf_path:
        return PlainTextResponse(
            "PDF generation requires weasyprint.\nRun: pip install weasyprint",
            status_code=501
        )
    sid = session_id[:8]
    return FR(
        pdf_path,
        media_type="application/pdf",
        filename=f"FoodEnergyMAS_report_{sid}.pdf",
        headers={"Content-Disposition": f"attachment; filename=FoodEnergyMAS_report_{sid}.pdf"},
    )