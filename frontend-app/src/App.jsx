import { useState, useEffect, useRef, useCallback } from "react";

// ── Agent config ───────────────────────────────────────────────────────────────
const AGENTS = {
  farmer:    { label: "Farmer",    icon: "🌾", model: "Mixtral-8x7B",    color: "#0F6E56", bg: "#E1F5EE", border: "#6DCFB0", tag: "Production" },
  logistics: { label: "Logistics", icon: "🚛", model: "Llama-3.3-70B",   color: "#085041", bg: "#C8EDE0", border: "#4DB896", tag: "Supply Chain" },
  energy:    { label: "Energy",    icon: "⚡", model: "Llama-3.3-70B",   color: "#633806", bg: "#FAEEDA", border: "#FAC775", tag: "Grid & Power" },
  market:    { label: "Market",    icon: "📈", model: "Qwen2.5-72B",     color: "#712B13", bg: "#FAECE7", border: "#F5C4B3", tag: "Prices" },
  regulator: { label: "Regulator", icon: "🏛️", model: "Llama-3.1-405B", color: "#3C3489", bg: "#EEEDFE", border: "#AFA9EC", tag: "Policy" },
};

const PHASES = ["Idle", "Farmer + Energy", "Logistics + Market", "Conflict Detection", "Regulator", "Complete"];

// ── Small reusable components ──────────────────────────────────────────────────

function Tag({ color, bg, border, children }) {
  return (
    <span style={{
      fontSize: 10, fontWeight: 600, letterSpacing: "0.05em",
      color, background: bg, border: `1px solid ${border || color + "44"}`,
      borderRadius: 4, padding: "2px 7px", display: "inline-block",
      textTransform: "uppercase",
    }}>{children}</span>
  );
}

function RiskBar({ value, color }) {
  const pct = Math.round((value || 0) * 100);
  const barColor = pct >= 70 ? "#e53e3e" : pct >= 40 ? "#dd6b20" : "#38a169";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <div style={{ flex: 1, height: 4, background: "#e2e8f0", borderRadius: 2, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: barColor, borderRadius: 2, transition: "width 0.8s ease" }} />
      </div>
      <span style={{ fontSize: 11, fontWeight: 600, color: barColor, minWidth: 28 }}>{pct}%</span>
    </div>
  );
}

function Spinner() {
  return (
    <span style={{
      display: "inline-block", width: 10, height: 10,
      border: "2px solid #ccc", borderTopColor: "#3C3489",
      borderRadius: "50%", animation: "spin 0.8s linear infinite",
    }} />
  );
}

// ── Agent card ─────────────────────────────────────────────────────────────────
function AgentCard({ name, data, status, onClick }) {
  const cfg = AGENTS[name];
  const isActive = status === "running";
  const isDone   = status === "done";

  return (
    <div
      onClick={() => data && onClick(name)}
      style={{
        border: `1.5px solid ${isDone ? cfg.border : isActive ? cfg.color + "88" : "#e2e8f0"}`,
        borderRadius: 12,
        background: isDone ? cfg.bg : isActive ? cfg.bg + "88" : "#fafafa",
        padding: "12px 14px",
        cursor: data ? "pointer" : "default",
        opacity: status === "waiting" ? 0.45 : 1,
        transition: "all 0.35s ease",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Running pulse border */}
      {isActive && (
        <div style={{
          position: "absolute", inset: 0,
          border: `2px solid ${cfg.color}`,
          borderRadius: 12,
          animation: "pulseBorder 1.4s ease-in-out infinite",
          pointerEvents: "none",
        }} />
      )}

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <span style={{ fontSize: 18 }}>{cfg.icon}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 13, color: cfg.color }}>{cfg.label}</div>
          <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 1 }}>{cfg.model}</div>
        </div>
        {isActive && <Spinner />}
        {isDone && <span style={{ fontSize: 14 }}>✅</span>}
      </div>

      <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginBottom: isDone && data ? 8 : 0 }}>
        <Tag color={cfg.color} bg={cfg.bg} border={cfg.border}>{cfg.tag}</Tag>
        {status === "running" && <Tag color="#633806" bg="#FAEEDA">analyzing…</Tag>}
        {status === "done"    && <Tag color="#0F6E56" bg="#E1F5EE">published</Tag>}
      </div>

      {isDone && data && (
        <div style={{ marginTop: 4 }}>
          {name === "farmer" && (
            <>
              <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>Climate risk</div>
              <RiskBar value={data.climate_risk_score} />
              {data.deficit_pct > 0 && (
                <div style={{ fontSize: 11, marginTop: 6 }}>
                  <span style={{ color: data.deficit_pct > 30 ? "#e53e3e" : "#dd6b20", fontWeight: 600 }}>
                    ⚠ Deficit {data.deficit_pct}%
                  </span>
                  {data.deficit_regions?.length > 0 && (
                    <span style={{ color: "#64748b" }}> — {data.deficit_regions.slice(0,2).join(", ")}</span>
                  )}
                </div>
              )}
            </>
          )}
          {name === "logistics" && (
            <>
              <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>Logistics risk</div>
              <RiskBar value={data.logistics_risk_score} />
              <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>
                Loss estimate: <b style={{ color: "#2d3748" }}>{data.loss_estimate_pct}%</b>
                {data.route_plan?.length > 0 && <> · <b>{data.route_plan.length}</b> routes planned</>}
              </div>
            </>
          )}
          {name === "energy" && (
            <>
              <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>Energy risk</div>
              <RiskBar value={data.energy_risk_score} />
              <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>
                ${data.energy_price_usd_kwh}/kWh · Grid {data.grid_load_pct}% ·{" "}
                <b style={{ color: data.shortage_alert === "critical" ? "#e53e3e" : data.shortage_alert === "warning" ? "#dd6b20" : "#38a169" }}>
                  {data.shortage_alert}
                </b>
              </div>
            </>
          )}
          {name === "market" && (
            <>
              <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>Market risk</div>
              <RiskBar value={data.market_risk_score} />
              <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>
                Demand: <b>{data.demand_signal}</b> · Stock: <b style={{ color: data.stock_level_days < 14 ? "#e53e3e" : "#2d3748" }}>{data.stock_level_days}d</b>
                {data.speculation_detected && <span style={{ color: "#e53e3e" }}> · ⚠ speculation</span>}
              </div>
            </>
          )}
          {name === "regulator" && (
            <>
              <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>Confidence</div>
              <RiskBar value={1 - (data.confidence_score || 0)} color="#3C3489" />
              {data.escalate_to_human && (
                <div style={{ fontSize: 11, color: "#e53e3e", marginTop: 4, fontWeight: 600 }}>
                  🚨 Human escalation required
                </div>
              )}
            </>
          )}
          <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 6, textAlign: "right" }}>
            click to inspect JSON →
          </div>
        </div>
      )}
    </div>
  );
}

// ── Conflict panel ─────────────────────────────────────────────────────────────
function ConflictPanel({ conflicts }) {
  if (!conflicts?.length) return null;
  return (
    <div style={{
      background: "#fffbeb", border: "1.5px solid #f59e0b",
      borderRadius: 10, padding: "12px 14px",
    }}>
      <div style={{ fontSize: 12, fontWeight: 700, color: "#92400e", marginBottom: 8 }}>
        ⚠️ Conflicts detected by coordinator
      </div>
      {conflicts.map((c, i) => (
        <div key={i} style={{
          fontSize: 12, color: "#78350f", padding: "4px 0",
          borderTop: i > 0 ? "1px solid #fde68a" : "none",
        }}>
          • {c}
        </div>
      ))}
    </div>
  );
}

// ── Final decision ─────────────────────────────────────────────────────────────
function FinalDecision({ event }) {
  const [showAudit, setShowAudit] = useState(false);
  if (!event) return null;
  const escalated = event.escalate_to_human;

  return (
    <div style={{
      background: escalated ? "#fff7ed" : "#f0fdf4",
      border: `1.5px solid ${escalated ? "#f59e0b" : "#86efac"}`,
      borderRadius: 12, padding: "16px 18px",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
        <span style={{ fontSize: 20 }}>{escalated ? "🚨" : "✅"}</span>
        <div style={{ fontWeight: 700, fontSize: 14, color: escalated ? "#92400e" : "#14532d" }}>
          {escalated ? "Human decision required" : "Final policy decision"}
        </div>
        <div style={{ marginLeft: "auto" }}>
          <Tag color="#3C3489" bg="#EEEDFE">
            Confidence {Math.round((event.confidence_score || 0) * 100)}%
          </Tag>
        </div>
      </div>

      <div style={{ fontSize: 13, color: "#1e293b", lineHeight: 1.7, marginBottom: 10 }}>
        {event.final_decision}
      </div>

      {escalated && event.escalation_reason && (
        <div style={{
          background: "#fef3c7", borderLeft: "3px solid #f59e0b",
          padding: "8px 12px", borderRadius: "0 6px 6px 0",
          fontSize: 12, color: "#92400e", marginBottom: 10,
        }}>
          <b>Escalation reason:</b> {event.escalation_reason}
        </div>
      )}

      <button
        onClick={() => setShowAudit(a => !a)}
        style={{
          fontSize: 11, color: "#3C3489", background: "none", border: "none",
          cursor: "pointer", padding: 0, textDecoration: "underline",
        }}
      >
        {showAudit ? "Hide" : "Show"} audit trail ({event.audit_trail?.audit_trail?.length || 0} entries)
      </button>

      {showAudit && event.audit_trail && (
        <pre style={{
          marginTop: 8, fontSize: 10, color: "#475569",
          background: "#f8fafc", borderRadius: 6, padding: 10,
          overflow: "auto", maxHeight: 200,
          border: "1px solid #e2e8f0",
        }}>
          {JSON.stringify(event.audit_trail, null, 2)}
        </pre>
      )}
    </div>
  );
}

// ── Band Room live feed ────────────────────────────────────────────────────────
function BandFeed({ events }) {
  const bottomRef = useRef(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  const color = (ev) => {
    if (ev.event === "error")              return "#fc8181";
    if (ev.event === "pipeline_complete")  return "#68d391";
    if (ev.event === "band_room_conflicts" && ev.count > 0) return "#f6ad55";
    if (ev.event === "phase")              return "#a78bfa";
    if (ev.event === "agent_done")         return AGENTS[ev.agent]?.color || "#94a3b8";
    return "#64748b";
  };

  const text = (ev) => {
    if (ev.event === "pipeline_start")    return `▶ Started: "${ev.scenario?.slice(0, 55)}${ev.scenario?.length > 55 ? "…" : ""}"`;
    if (ev.event === "phase")             return `── Phase ${ev.phase}: ${ev.label}`;
    if (ev.event === "agent_done")        return `${AGENTS[ev.agent]?.icon} ${AGENTS[ev.agent]?.label} published to Band Room`;
    if (ev.event === "band_room_conflicts") return ev.count === 0 ? "✓ No conflicts" : `⚠ ${ev.count} conflict(s) detected`;
    if (ev.event === "pipeline_complete") return `🎯 Decision ready | confidence ${Math.round((ev.confidence_score || 0) * 100)}%${ev.escalate_to_human ? " | 🚨 ESCALATED" : ""}`;
    if (ev.event === "error")             return `✗ Error: ${ev.message}`;
    return ev.event;
  };

  return (
    <div style={{
      background: "#0f0f1a", borderRadius: 12,
      padding: "12px 14px", height: 220, overflowY: "auto",
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    }}>
      <div style={{ fontSize: 10, color: "#7F77DD", marginBottom: 8, letterSpacing: "0.1em" }}>
        BAND ROOM · LIVE FEED
      </div>
      {events.length === 0 && (
        <div style={{ fontSize: 11, color: "#374151" }}>Waiting for pipeline start…</div>
      )}
      {events.map((ev, i) => (
        <div key={i} style={{ fontSize: 11.5, color: color(ev), padding: "1.5px 0" }}>
          {text(ev)}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

// ── JSON inspector modal ───────────────────────────────────────────────────────
function Inspector({ name, data, onClose }) {
  if (!name || !data) return null;
  const cfg = AGENTS[name];
  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed", inset: 0, background: "#0008",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 1000, padding: 16,
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          background: "#fff", borderRadius: 14, width: "100%", maxWidth: 560,
          maxHeight: "80vh", overflow: "hidden", display: "flex", flexDirection: "column",
          border: `2px solid ${cfg.border}`,
        }}
      >
        <div style={{
          display: "flex", alignItems: "center", gap: 8,
          padding: "14px 16px", borderBottom: `1px solid ${cfg.border}`,
          background: cfg.bg,
        }}>
          <span style={{ fontSize: 18 }}>{cfg.icon}</span>
          <div style={{ fontWeight: 700, color: cfg.color }}>{cfg.label} Agent Payload</div>
          <button onClick={onClose} style={{
            marginLeft: "auto", background: "none", border: "none",
            fontSize: 18, cursor: "pointer", color: "#64748b", lineHeight: 1,
          }}>×</button>
        </div>
        <pre style={{
          flex: 1, overflowY: "auto", margin: 0,
          padding: "12px 14px", fontSize: 11.5,
          color: "#1e293b", lineHeight: 1.6,
          background: "#fafafa",
        }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    </div>
  );
}

// ── Phase progress bar ─────────────────────────────────────────────────────────
function PhaseBar({ phase }) {
  if (phase === 0) return null;
  return (
    <div style={{ display: "flex", gap: 0, borderRadius: 8, overflow: "hidden", border: "1px solid #e2e8f0", marginBottom: 14 }}>
      {PHASES.slice(1).map((label, i) => {
        const phaseNum = i + 1;
        const done = phaseNum < phase;
        const active = phaseNum === phase;
        return (
          <div key={i} style={{
            flex: 1, padding: "5px 4px", textAlign: "center",
            background: done ? "#3C3489" : active ? "#7F77DD" : "#f1f5f9",
            fontSize: 9, fontWeight: 600, letterSpacing: "0.03em",
            color: done || active ? "#fff" : "#94a3b8",
            borderRight: i < 4 ? "1px solid #e2e8f0" : "none",
            transition: "all 0.3s",
            textTransform: "uppercase",
          }}>
            {label}
          </div>
        );
      })}
    </div>
  );
}

// ── EXAMPLE SCENARIOS ──────────────────────────────────────────────────────────
const SCENARIOS = [
  "Drought in Central Asia reduced wheat harvest by 25%. Energy prices up 40%. Assess regional food and energy security.",
  "Suez Canal blocked — grain shipments to Middle East disrupted. Local reserves critically low. Recommend policy actions.",
  "Speculative trading spike pushed wheat prices to 3-year high. Small farmers cannot afford inputs. Analyse market intervention options.",
  "Ukraine conflict escalation cuts corn exports by 35%. Energy grid attacks reduce cold chain capacity. Model cascading food security risks.",
];

// ── Main dashboard ─────────────────────────────────────────────────────────────
export default function Dashboard() {
  const [scenario, setScenario]       = useState(SCENARIOS[0]);
  const [running, setRunning]         = useState(false);
  const [events, setEvents]           = useState([]);
  const [agentData, setAgentData]     = useState({});
  const [agentStatus, setAgentStatus] = useState({ farmer:"waiting", logistics:"waiting", energy:"waiting", market:"waiting", regulator:"waiting" });
  const [phase, setPhase]             = useState(0);
  const [finalEvent, setFinalEvent]   = useState(null);
  const [conflicts, setConflicts]     = useState([]);
  const [inspector, setInspector]     = useState(null);  // { name, data }
  const wsRef = useRef(null);

  const reset = () => {
    setEvents([]); setAgentData({});
    setAgentStatus({ farmer:"waiting", logistics:"waiting", energy:"waiting", market:"waiting", regulator:"waiting" });
    setPhase(0); setFinalEvent(null); setConflicts([]);
  };

  const handleEvent = useCallback((ev) => {
    setEvents(prev => [...prev, ev]);

    if (ev.event === "phase") {
      setPhase(ev.phase);
      if (ev.phase === 1) setAgentStatus(s => ({ ...s, farmer: "running", energy: "running" }));
      if (ev.phase === 2) setAgentStatus(s => ({ ...s, logistics: "running", market: "running" }));
      if (ev.phase === 4) setAgentStatus(s => ({ ...s, regulator: "running" }));
    }
    if (ev.event === "agent_done") {
      setAgentData(prev => ({ ...prev, [ev.agent]: ev.data }));
      setAgentStatus(prev => ({ ...prev, [ev.agent]: "done" }));
    }
    if (ev.event === "band_room_conflicts") setConflicts(ev.conflicts || []);
    if (ev.event === "pipeline_complete")   { setFinalEvent(ev); setPhase(5); setRunning(false); }
    if (ev.event === "error")               setRunning(false);
  }, []);

  const run = async () => {
    reset(); setRunning(true);
    try {
      const ws = new WebSocket("ws://localhost:8000/ws");
      wsRef.current = ws;
      ws.onopen    = () => ws.send(JSON.stringify({ scenario }));
      ws.onmessage = (msg) => { try { handleEvent(JSON.parse(msg.data)); } catch {} };
      ws.onerror   = () => runViaRest();
      ws.onclose   = () => setRunning(false);
    } catch { runViaRest(); }
  };

  const runViaRest = async () => {
    try {
      const res  = await fetch("http://localhost:8000/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario }),
      });
      const data = await res.json();
      data.events?.forEach(handleEvent);
    } catch {
      handleEvent({ event: "error", message: "Backend unavailable. Run: uvicorn backend.main:app" });
      setRunning(false);
    }
  };

  return (
    <div style={{ fontFamily: "'Inter', system-ui, sans-serif", background: "#f1f0ff", minHeight: "100vh", padding: "18px 14px" }}>

      {/* Header */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
          <div style={{ fontSize: 21, fontWeight: 800, color: "#1e1b4b", letterSpacing: "-0.5px" }}>
            🌾 FoodEnergyMAS
          </div>
          <div style={{ fontSize: 11, color: "#7F77DD", fontWeight: 500 }}>
            Band · Featherless AI · ChromaDB
          </div>
        </div>
        <div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>
          5 agents · parallel analysis · human-in-the-loop escalation
        </div>
      </div>

      {/* Phase bar */}
      <PhaseBar phase={phase} />

      {/* Scenario */}
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 10, fontWeight: 700, color: "#94a3b8", letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 5 }}>
          Scenario
        </div>
        <textarea
          value={scenario}
          onChange={e => setScenario(e.target.value)}
          disabled={running}
          rows={3}
          style={{
            width: "100%", fontFamily: "inherit", fontSize: 13, lineHeight: 1.5,
            border: "1.5px solid #c7d2fe", borderRadius: 8, padding: "10px 12px",
            background: running ? "#f8f7ff" : "#fff", resize: "none",
            outline: "none", boxSizing: "border-box", color: "#1e1b4b",
          }}
        />
        {/* Quick scenario pills */}
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 6 }}>
          {SCENARIOS.map((s, i) => (
            <button key={i} onClick={() => !running && setScenario(s)} style={{
              fontSize: 10, padding: "3px 9px", borderRadius: 20,
              border: "1px solid #c7d2fe", background: scenario === s ? "#3C3489" : "#fff",
              color: scenario === s ? "#fff" : "#3C3489", cursor: running ? "default" : "pointer",
              fontWeight: 500,
            }}>
              Scenario {i + 1}
            </button>
          ))}
        </div>
      </div>

      {/* Run button */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button onClick={run} disabled={running} style={{
          flex: 1, padding: "11px 0", borderRadius: 9,
          background: running ? "#c7d2fe" : "linear-gradient(135deg, #3C3489, #7F77DD)",
          color: "#fff", border: "none", fontWeight: 700, fontSize: 14,
          cursor: running ? "not-allowed" : "pointer",
          boxShadow: running ? "none" : "0 2px 8px #3C348944",
          transition: "all 0.2s",
        }}>
          {running ? "⏳ Agents analysing…" : "▶ Run Pipeline"}
        </button>
        {running && (
          <button onClick={() => { wsRef.current?.close(); setRunning(false); }} style={{
            padding: "11px 14px", borderRadius: 9,
            background: "#fff", border: "1.5px solid #f87171",
            color: "#dc2626", fontWeight: 600, cursor: "pointer", fontSize: 13,
          }}>
            Stop
          </button>
        )}
      </div>

      {/* Agent grid */}
      <div style={{ fontSize: 10, fontWeight: 700, color: "#94a3b8", letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 8 }}>
        Agents
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 8 }}>
        {["farmer", "logistics", "energy", "market"].map(name => (
          <AgentCard
            key={name} name={name}
            data={agentData[name]} status={agentStatus[name]}
            onClick={(n) => setInspector({ name: n, data: agentData[n] })}
          />
        ))}
      </div>
      <AgentCard
        name="regulator"
        data={agentData["regulator"]} status={agentStatus["regulator"]}
        onClick={(n) => setInspector({ name: n, data: agentData[n] })}
      />

      {/* Conflicts */}
      {conflicts.length > 0 && (
        <div style={{ marginTop: 12 }}><ConflictPanel conflicts={conflicts} /></div>
      )}

      {/* Final decision */}
      {finalEvent && (
        <div style={{ marginTop: 12 }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: "#94a3b8", letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 8 }}>
            Final Decision
          </div>
          <FinalDecision event={finalEvent} />
        </div>
      )}

      {/* Band Room feed */}
      <div style={{ marginTop: 14 }}>
        <div style={{ fontSize: 10, fontWeight: 700, color: "#94a3b8", letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 8 }}>
          Band Room · Live
        </div>
        <BandFeed events={events} />
      </div>

      {/* Inspector modal */}
      {inspector && (
        <Inspector name={inspector.name} data={inspector.data} onClose={() => setInspector(null)} />
      )}

      <style>{`
        @keyframes spin        { to { transform: rotate(360deg); } }
        @keyframes pulseBorder { 0%,100%{ opacity:1; } 50%{ opacity:0.3; } }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar       { width: 4px; height: 4px; }
        ::-webkit-scrollbar-thumb { background: #AFA9EC; border-radius: 2px; }
        textarea:focus { border-color: #7F77DD !important; box-shadow: 0 0 0 3px #7F77DD22; }
      `}</style>
    </div>
  );
}