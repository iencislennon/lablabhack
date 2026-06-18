"""
report.py — Generate structured Markdown + PDF reports.

On Render (ephemeral filesystem), reports are stored in memory (_report_store).
On local dev, reports are also saved to disk in reports/.
PDF is generated on-demand from the in-memory markdown.
"""

import json
import re
import os
import io
from datetime import datetime
from pathlib import Path
from backend.schemas import BandRoomState

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

# In-memory store: session_id -> {"md": str, "json": dict}
# Survives within the same process lifetime (same Render instance)
_report_store: dict = {}


def _risk_label(score: float) -> str:
    if score >= 0.7:  return "HIGH"
    if score >= 0.4:  return "MEDIUM"
    return "LOW"


def _alert_emoji(alert: str) -> str:
    return {"none": "OK", "warning": "WARNING", "critical": "CRITICAL"}.get(alert, alert)


def _build_markdown(state: BandRoomState, scenario: str, audit: dict) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    r = state.regulator
    f = state.farmer
    l = state.logistics
    e = state.energy
    m = state.market
    lines = []

    lines += [
        "# CrisisNet — Security Assessment Report", "",
        f"**Session:** `{state.session_id}`  ",
        f"**Generated:** {now}  ",
        f"**Scenario:** {scenario}", "", "---", "",
    ]

    lines += ["## Executive Summary", ""]
    if r:
        lines += [
            f"> {r.policy_recommendation}", "",
            "| Confidence | Escalation | Import needed | Reserves release |",
            "|---|---|---|---|",
            f"| **{int(r.confidence_score * 100)}%** | {'YES' if r.escalate_to_human else 'No'} | {'YES' if r.import_trigger else 'No'} | {'YES' if r.emergency_reserves_release else 'No'} |",
            "",
        ]
        if r.escalate_to_human and r.escalation_reason:
            lines += [f"> **Human decision required:** {r.escalation_reason}", ""]

    lines += ["---", "", "## Agent Findings", ""]

    if f:
        lines += [
            f"### Farmer Agent — {_risk_label(f.climate_risk_score)}", "",
            f"- **Climate risk score:** {f.climate_risk_score:.2f}",
            f"- **Max regional deficit:** {f.deficit_pct}%",
        ]
        if f.deficit_regions:
            lines.append(f"- **Deficit regions:** {', '.join(f.deficit_regions)}")
        if f.risk_flags:
            lines.append(f"- **Risk flags:** {', '.join(f.risk_flags)}")
        if f.crop_forecast:
            lines += ["", "**Crop Forecast:**", "", "| Crop | Region | Expected (t) | vs Last Year |", "|---|---|---|---|"]
            for c in f.crop_forecast[:5]:
                trend = f"+{c.vs_last_year_pct:.1f}%" if c.vs_last_year_pct >= 0 else f"{c.vs_last_year_pct:.1f}%"
                lines.append(f"| {c.crop_type} | {c.region} | {c.expected_yield_tons:,.0f} | {trend} |")
        lines.append("")

    if l:
        lines += [
            f"### Logistics Agent — {_risk_label(l.logistics_risk_score)}", "",
            f"- **Supply chain loss estimate:** {l.loss_estimate_pct}%",
            f"- **Available storage:** {l.storage_capacity_available_tons:,.0f} tonnes",
        ]
        if l.bottlenecks:
            lines.append(f"- **Bottlenecks:** {', '.join(l.bottlenecks)}")
        if l.route_plan:
            lines += ["", "**Route Plan:**", "", "| From | To | Mode | Capacity (t) | Days | Cost/t |", "|---|---|---|---|---|---|"]
            for rt in l.route_plan[:5]:
                lines.append(f"| {rt.from_region} | {rt.to_region} | {rt.transport_mode} | {rt.capacity_tons:,.0f} | {rt.estimated_days} | ${rt.cost_per_ton_usd} |")
        lines.append("")

    if e:
        lines += [
            f"### Energy Agent — {_risk_label(e.energy_risk_score)}", "",
            f"- **Price:** ${e.energy_price_usd_kwh}/kWh ({e.energy_price_trend})",
            f"- **Grid load:** {e.grid_load_pct}%",
            f"- **Shortage alert:** {_alert_emoji(e.shortage_alert)}",
            f"- **Renewable share:** {e.renewable_share_pct}%",
            f"- **Impact:** {e.impact_on_food_production}", "",
        ]

    if m:
        lines += [
            f"### Market Agent — {_risk_label(m.market_risk_score)}", "",
            f"- **Demand signal:** {m.demand_signal} ({m.demand_trend})",
            f"- **Stock level:** {m.stock_level_days} days {'CRITICAL' if m.stock_level_days < 14 else ''}",
            f"- **Inflation risk:** {m.inflation_risk}",
            f"- **Speculation detected:** {'Yes' if m.speculation_detected else 'No'}",
        ]
        if m.price_recommendations:
            lines += ["", "**Price Recommendations:**", "", "| Commodity | Current | Recommended | Rationale |", "|---|---|---|---|"]
            for p in m.price_recommendations[:5]:
                lines.append(f"| {p.commodity} | ${p.current_price_usd} | ${p.recommended_price_usd} | {p.rationale[:60]} |")
        lines.append("")

    lines += ["---", ""]

    if r:
        lines += ["## Policy Decision", "", f"**Recommendation:** {r.policy_recommendation}", ""]
        if r.subsidy_plan:
            lines += ["**Subsidy Plan:**", "", "| Target | Amount (USD M) | Duration | Rationale |", "|---|---|---|---|"]
            for s in r.subsidy_plan:
                lines.append(f"| {s.target} | ${s.amount_usd_million}M | {s.duration_months} months | {s.rationale[:60]} |")
            lines.append("")
        if r.import_trigger and r.import_details:
            lines += [f"**Emergency Import:** {r.import_details}", ""]
        if r.price_controls:
            lines += ["**Price Controls:** Activated", ""]

    lines += ["---", ""]

    if state.conflicts:
        lines += ["## Conflicts Detected", ""]
        for c in state.conflicts:
            lines.append(f"- {c}")
        lines += ["", "---", ""]

    lines += [
        "## Audit Trail", "",
        f"- **Actions logged:** {len(audit.get('audit_trail', []))}",
        f"- **Debate rounds:** {state.debate_rounds}", "",
        "| # | Agent | Action | Details |", "|---|---|---|---|",
    ]
    for i, entry in enumerate(audit.get("audit_trail", []), 1):
        lines.append(f"| {i} | {entry.get('agent','')} | {entry.get('action','')} | {str(entry.get('details',''))[:60]} |")

    lines += ["", "---", "", f"*CrisisNet · Session `{state.session_id}` · {now}*"]
    return "\n".join(lines)


def _md_to_pdf_bytes(md_text: str) -> bytes:
    """Convert markdown string to PDF bytes using weasyprint."""
    from weasyprint import HTML

    html_body = md_text
    html_body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
    html_body = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html_body, flags=re.MULTILINE)
    html_body = html_body.replace('\n---\n', '\n<hr/>\n')

    def convert_table(m):
        tlines = [ln.strip() for ln in m.group(0).strip().split('\n') if ln.strip()]
        rows = [ln for ln in tlines if not re.match(r'^\|[-| :]+\|$', ln)]
        html = '<table>'
        for i, row in enumerate(rows):
            cells = [c.strip() for c in row.strip('|').split('|')]
            tag = 'th' if i == 0 else 'td'
            html += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>'
        html += '</table>'
        return html

    html_body = re.sub(r'(\|.+\|\n)+', convert_table, html_body)
    html_body = re.sub(r'^- (.+)$', r'<li>\1</li>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'(<li>.*</li>\n?)+', lambda m: f'<ul>{m.group(0)}</ul>', html_body)

    lines_out = []
    for line in html_body.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            lines_out.append(f'<p>{stripped}</p>')
        else:
            lines_out.append(line)
    html_body = '\n'.join(lines_out)

    full_html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><style>
  @page {{ size: A4; margin: 2cm 2.2cm; }}
  body {{ font-family: Arial, sans-serif; font-size: 11pt; color: #1e293b; line-height: 1.6; }}
  h1 {{ font-size: 18pt; font-weight: 500; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6pt; margin-top: 0; }}
  h2 {{ font-size: 13pt; font-weight: 500; color: #0f172a; margin-top: 18pt; border-bottom: 1px solid #f1f5f9; padding-bottom: 4pt; }}
  h3 {{ font-size: 11pt; font-weight: 500; color: #334155; margin-top: 12pt; }}
  p  {{ margin: 5pt 0; }}
  blockquote {{ background: #f8fafc; border-left: 3px solid #3C3489; padding: 8pt 12pt; margin: 8pt 0; font-style: italic; color: #334155; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 8pt 0; }}
  th {{ background: #0f1623; color: #fff; padding: 5pt 8pt; text-align: left; font-weight: 500; }}
  td {{ padding: 4pt 8pt; border-bottom: 1px solid #f1f5f9; }}
  tr:nth-child(even) td {{ background: #f8fafc; }}
  ul {{ padding-left: 16pt; margin: 5pt 0; }}
  li {{ margin: 2pt 0; }}
  hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 12pt 0; }}
  strong {{ font-weight: 500; }}
</style></head><body>{html_body}</body></html>"""

    return HTML(string=full_html).write_pdf()


def generate_report(state: BandRoomState, scenario: str, audit: dict) -> str:
    """
    Build markdown, store in memory + optionally save to disk.
    Returns session_id (used as key for later PDF generation).
    """
    sid = state.session_id[:8]
    md  = _build_markdown(state, scenario, audit)

    # Store in memory (works on Render ephemeral fs)
    _report_store[sid] = {
        "md":   md,
        "json": {
            "session_id": state.session_id,
            "scenario":   scenario,
            "generated_at": datetime.utcnow().isoformat(),
            "farmer":    state.farmer.model_dump()    if state.farmer    else None,
            "logistics": state.logistics.model_dump() if state.logistics else None,
            "energy":    state.energy.model_dump()    if state.energy    else None,
            "market":    state.market.model_dump()    if state.market    else None,
            "regulator": state.regulator.model_dump() if state.regulator else None,
            "conflicts": state.conflicts,
            "audit":     audit,
        }
    }

    # Also try to save to disk (works locally, no-op if fs is read-only)
    try:
        REPORTS_DIR.mkdir(exist_ok=True)
        (REPORTS_DIR / f"report_{sid}.md").write_text(md, encoding="utf-8")
    except Exception:
        pass

    return sid


def get_report_md(session_id: str) -> str | None:
    """Return markdown text for a session, from memory or disk."""
    sid = session_id[:8]
    if sid in _report_store:
        return _report_store[sid]["md"]
    path = REPORTS_DIR / f"report_{sid}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def get_report_json(session_id: str) -> dict | None:
    """Return JSON data for a session, from memory or disk."""
    sid = session_id[:8]
    if sid in _report_store:
        return _report_store[sid]["json"]
    path = REPORTS_DIR / f"report_{sid}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def generate_pdf_bytes(session_id: str) -> bytes | None:
    """
    Generate PDF bytes on-demand from in-memory markdown.
    Returns bytes (not a file path) so nothing needs to be written to disk.
    """
    try:
        from weasyprint import HTML
    except ImportError:
        return None

    md = get_report_md(session_id)
    if not md:
        return None

    return _md_to_pdf_bytes(md)


# Keep old generate_pdf for local compatibility
def generate_pdf(session_id: str) -> str | None:
    """Legacy: write PDF to disk and return path. Use generate_pdf_bytes for Render."""
    try:
        from weasyprint import HTML
    except ImportError:
        return None
    sid = session_id[:8]
    md  = get_report_md(session_id)
    if not md:
        return None
    REPORTS_DIR.mkdir(exist_ok=True)
    pdf_path = REPORTS_DIR / f"report_{sid}.pdf"
    _md_to_pdf_bytes(md)  # validate
    HTML(string=_build_html_from_md(md)).write_pdf(str(pdf_path))
    return str(pdf_path)


def _build_html_from_md(md_text: str) -> str:
    """Helper — same as in _md_to_pdf_bytes but returns HTML string."""
    html_body = md_text
    html_body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
    html_body = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html_body, flags=re.MULTILINE)
    html_body = html_body.replace('\n---\n', '\n<hr/>\n')
    return f"<html><body>{html_body}</body></html>"