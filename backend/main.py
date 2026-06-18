"""
main.py — FastAPI orchestrator.
"""

import asyncio
import json
import os
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
from backend.report import generate_report, generate_pdf
from backend.schemas import BandRoomState

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Detect public backend URL (Render sets RENDER_EXTERNAL_URL automatically)
BACKEND_URL = (
    os.getenv("RENDER_EXTERNAL_URL")        # set by Render automatically
    or os.getenv("BACKEND_PUBLIC_URL")      # manual override
    or "http://localhost:8000"              # local fallback
).rstrip("/")


# ── WebSocket manager ──────────────────────────────────────────────────────────

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


# ── App ────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 CrisisNet starting up | public URL: {BACKEND_URL}")

    # Auto-seed ChromaDB on startup if env var is set (useful on Render)
    if os.getenv("SEED_ON_STARTUP", "").lower() in ("1", "true", "yes"):
        logger.info("🌱 SEED_ON_STARTUP=true — seeding ChromaDB...")
        try:
            from backend.vector_db.seed_data import seed_all
            seed_all()
        except Exception as e:
            logger.warning(f"Seeding failed (non-fatal): {e}")

    yield
    logger.info("👋 CrisisNet shutting down")


app = FastAPI(
    title="CrisisNet",
    description="Multi-Agent Crisis Intelligence System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    scenario: str = "Analyse current food and energy security conditions"


# ── Pipeline ───────────────────────────────────────────────────────────────────

async def run_pipeline(scenario: str, broadcast) -> BandRoomState:
    coordinator = BandCoordinator()
    await broadcast({"event": "pipeline_start", "scenario": scenario})

    # Phase 1 — independent
    await broadcast({"event": "phase", "phase": 1, "label": "Independent agents"})
    farmer_task = asyncio.create_task(FarmerAgent().analyze(scenario))
    energy_task = asyncio.create_task(EnergyAgent().analyze(scenario))
    farmer_result, energy_result = await asyncio.gather(farmer_task, energy_task)

    coordinator.receive("farmer", farmer_result)
    await broadcast({"event": "agent_done", "agent": "farmer", "data": farmer_result.model_dump()})
    coordinator.receive("energy", energy_result)
    await broadcast({"event": "agent_done", "agent": "energy", "data": energy_result.model_dump()})

    # Phase 2 — dependent
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

    # Phase 3 — conflicts
    await broadcast({"event": "phase", "phase": 3, "label": "Conflict detection"})
    conflicts = coordinator.detect_conflicts()
    await broadcast({"event": "band_room_conflicts", "conflicts": conflicts, "count": len(conflicts)})

    # Phase 4 — regulator
    await broadcast({"event": "phase", "phase": 4, "label": "Regulator decision"})
    regulator_result = await RegulatorAgent().analyze(coordinator.state)
    coordinator.receive("regulator", regulator_result)
    await broadcast({"event": "agent_done", "agent": "regulator", "data": regulator_result.model_dump()})

    # Phase 5 — report
    coordinator.state.final_decision_ready = True
    audit = coordinator.generate_audit_report()
    report_path = generate_report(coordinator.state, scenario, audit)
    session_id = coordinator.state.session_id
    logger.info(f"📄 Report saved: {report_path}")

    await broadcast({
        "event":              "pipeline_complete",
        "final_decision":     regulator_result.policy_recommendation,
        "escalate_to_human":  regulator_result.escalate_to_human,
        "escalation_reason":  regulator_result.escalation_reason,
        "confidence_score":   regulator_result.confidence_score,
        "import_trigger":     regulator_result.import_trigger,
        "price_controls":     regulator_result.price_controls,
        "emergency_reserves": regulator_result.emergency_reserves_release,
        "subsidy_plan":       [s.model_dump() for s in regulator_result.subsidy_plan],
        "conflicts":          conflicts,
        "session_id":         session_id,
        "report_url":         f"{BACKEND_URL}/report/{session_id}/pdf",
        "audit_trail":        audit,
    })

    logger.info("✅ Pipeline complete")
    return coordinator.state


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "ok", "service": "CrisisNet", "backend_url": BACKEND_URL}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/run")
async def run_sync(request: RunRequest):
    events = []
    async def collect(data: dict):
        events.append(data)
    state = await run_pipeline(request.scenario, collect)
    sid = state.session_id
    return {
        "session_id":        sid,
        "report_url":        f"{BACKEND_URL}/report/{sid}/pdf",
        "final_decision":    state.regulator.policy_recommendation if state.regulator else None,
        "escalate_to_human": state.regulator.escalate_to_human if state.regulator else False,
        "confidence_score":  state.regulator.confidence_score if state.regulator else 0,
        "conflicts":         state.conflicts,
        "events":            events,
    }


@app.get("/report/{session_id}", response_class=PlainTextResponse)
async def get_report_md(session_id: str):
    sid  = session_id[:8]
    path = REPORTS_DIR / f"report_{sid}.md"
    if not path.exists():
        return PlainTextResponse("Report not found", status_code=404)
    return PlainTextResponse(path.read_text(encoding="utf-8"), media_type="text/markdown")


@app.get("/report/{session_id}/pdf")
async def get_report_pdf(session_id: str):
    sid      = session_id[:8]
    pdf_path = generate_pdf(session_id)
    if not pdf_path:
        return PlainTextResponse(
            "PDF generation requires weasyprint. Run: pip install weasyprint",
            status_code=501,
        )
    filename = f"CrisisNet_report_{sid}.pdf"
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/report/{session_id}/json")
async def get_report_json(session_id: str):
    sid  = session_id[:8]
    path = REPORTS_DIR / f"report_{sid}.json"
    if not path.exists():
        return {"error": "Report not found"}
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/reports")
async def list_reports():
    files = sorted(REPORTS_DIR.glob("report_*.md"), reverse=True)
    return [
        {
            "session_id": f.stem.replace("report_", ""),
            "url":        f"/report/{f.stem.replace('report_', '')}",
            "pdf_url":    f"{BACKEND_URL}/report/{f.stem.replace('report_', '')}/pdf",
        }
        for f in files[:20]
    ]


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
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
                logger.error(f"Pipeline error: {e}")
                await websocket.send_text(json.dumps({"event": "error", "message": str(e)}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WS client disconnected")