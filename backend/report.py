"""
report.py — Generate a structured Markdown + JSON report from a pipeline run.

Called automatically after each pipeline completion.
Output: reports/report_<session_id>.md
"""

import json
import os
from datetime import datetime
from pathlib import Path

from backend.schemas import BandRoomState


REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def _risk_label(score: float) -> str:
    if score >= 0.7:  return "🔴 HIGH"
    if score >= 0.4:  return "🟡 MEDIUM"
    return "🟢 LOW"


def _alert_emoji(alert: str) -> str:
    return {"none": "✅", "warning": "⚠️", "critical": "🚨"}.get(alert, "❓")


def generate_report(state: BandRoomState, scenario: str, audit: dict) -> str:
    """
    Generate a full Markdown report from the completed BandRoomState.
    Returns the file path of the saved report.
    """
    REPORTS_DIR.mkdir(exist_ok=True)

    now   = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sid   = state.session_id[:8]
    fname = REPORTS_DIR / f"report_{sid}.md"

    r = state.regulator
    f = state.farmer
    l = state.logistics
    e = state.energy
    m = state.market

    lines = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines += [
        "# 🌾⚡ FoodEnergyMAS — Security Assessment Report",
        "",
        f"**Session:** `{state.session_id}`  ",
        f"**Generated:** {now}  ",
        f"**Scenario:** {scenario}",
        "",
        "---",
        "",
    ]

    # ── Executive summary ─────────────────────────────────────────────────────
    lines += ["## Executive Summary", ""]
    if r:
        lines += [
            f"> {r.policy_recommendation}",
            "",
            f"| Confidence | Escalation | Import needed | Reserves release |",
            f"|---|---|---|---|",
            f"| **{int(r.confidence_score * 100)}%** | {'🚨 YES' if r.escalate_to_human else '✅ No'} | {'YES' if r.import_trigger else 'No'} | {'YES' if r.emergency_reserves_release else 'No'} |",
            "",
        ]
        if r.escalate_to_human and r.escalation_reason:
            lines += [
                f"> ⚠️ **Human decision required:** {r.escalation_reason}",
                "",
            ]

    lines += ["---", ""]

    # ── Agent findings ────────────────────────────────────────────────────────
    lines += ["## Agent Findings", ""]

    # Farmer
    if f:
        lines += [
            f"### 🌾 Farmer Agent — {_risk_label(f.climate_risk_score)}",
            "",
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

    # Logistics
    if l:
        lines += [
            f"### 🚛 Logistics Agent — {_risk_label(l.logistics_risk_score)}",
            "",
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

    # Energy
    if e:
        lines += [
            f"### ⚡ Energy Agent — {_risk_label(e.energy_risk_score)}",
            "",
            f"- **Price:** ${e.energy_price_usd_kwh}/kWh ({e.energy_price_trend})",
            f"- **Grid load:** {e.grid_load_pct}%",
            f"- **Shortage alert:** {_alert_emoji(e.shortage_alert)} {e.shortage_alert.upper()}",
            f"- **Renewable share:** {e.renewable_share_pct}%",
            f"- **Impact on food production:** {e.impact_on_food_production}",
            "",
        ]

    # Market
    if m:
        lines += [
            f"### 📈 Market Agent — {_risk_label(m.market_risk_score)}",
            "",
            f"- **Demand signal:** {m.demand_signal} ({m.demand_trend})",
            f"- **Stock level:** {m.stock_level_days} days {'⚠️ CRITICAL' if m.stock_level_days < 14 else ''}",
            f"- **Inflation risk:** {m.inflation_risk}",
            f"- **Speculation detected:** {'⚠️ Yes' if m.speculation_detected else 'No'}",
        ]
        if m.price_recommendations:
            lines += ["", "**Price Recommendations:**", "", "| Commodity | Current | Recommended | Rationale |", "|---|---|---|---|"]
            for p in m.price_recommendations[:5]:
                lines.append(f"| {p.commodity} | ${p.current_price_usd} | ${p.recommended_price_usd} | {p.rationale[:60]}… |")
        lines.append("")

    lines += ["---", ""]

    # ── Policy decision ────────────────────────────────────────────────────────
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

        if r.conflicts_detected:
            lines += ["**Conflicts resolved:**", ""]
            for c in r.conflicts_detected:
                lines.append(f"- {c}")
            lines.append("")

    lines += ["---", ""]

    # ── Conflicts ──────────────────────────────────────────────────────────────
    if state.conflicts:
        lines += ["## Coordinator Conflicts Detected", ""]
        for c in state.conflicts:
            lines.append(f"- ⚠️ {c}")
        lines.append("")
        lines += ["---", ""]

    # ── Audit trail ───────────────────────────────────────────────────────────
    lines += [
        "## Audit Trail",
        "",
        f"- **Debate rounds:** {state.debate_rounds}",
        f"- **Total actions logged:** {len(audit.get('audit_trail', []))}",
        f"- **Final decision ready:** {state.final_decision_ready}",
        "",
        "| # | Agent | Action | Details |",
        "|---|---|---|---|",
    ]
    for i, entry in enumerate(audit.get("audit_trail", []), 1):
        lines.append(f"| {i} | {entry.get('agent','')} | {entry.get('action','')} | {str(entry.get('details',''))[:60]} |")

    lines += [
        "",
        "---",
        "",
        f"*Report generated by FoodEnergyMAS · Session `{state.session_id}` · {now}*",
    ]

    content = "\n".join(lines)
    fname.write_text(content, encoding="utf-8")

    # Also save raw JSON
    json_path = REPORTS_DIR / f"report_{sid}.json"
    json_path.write_text(json.dumps({
        "session_id": state.session_id,
        "scenario": scenario,
        "generated_at": now,
        "farmer":    state.farmer.model_dump()    if state.farmer    else None,
        "logistics": state.logistics.model_dump() if state.logistics else None,
        "energy":    state.energy.model_dump()    if state.energy    else None,
        "market":    state.market.model_dump()    if state.market    else None,
        "regulator": state.regulator.model_dump() if state.regulator else None,
        "conflicts": state.conflicts,
        "audit":     audit,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return str(fname)


def generate_pdf(session_id: str) -> str | None:
    """
    Convert the Markdown report to PDF using weasyprint.
    Returns PDF file path, or None if weasyprint is not installed.
    """
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        return None

    sid      = session_id[:8]
    md_path  = REPORTS_DIR / f"report_{sid}.md"
    pdf_path = REPORTS_DIR / f"report_{sid}.pdf"

    if not md_path.exists():
        return None

    md_text = md_path.read_text(encoding="utf-8")

    # Convert Markdown to HTML manually (no extra deps)
    import re
    html_body = md_text

    # Headers
    html_body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', html_body, flags=re.MULTILINE)

    # Bold
    html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)

    # Blockquote
    html_body = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html_body, flags=re.MULTILINE)

    # Horizontal rule
    html_body = html_body.replace('\n---\n', '\n<hr/>\n')

    # Tables — convert markdown table rows to HTML
    def convert_table(m):
        lines = [l.strip() for l in m.group(0).strip().split('\n') if l.strip()]
        rows = [l for l in lines if not re.match(r'^\|[-| :]+\|$', l)]
        html = '<table>'
        for i, row in enumerate(rows):
            cells = [c.strip() for c in row.strip('|').split('|')]
            tag = 'th' if i == 0 else 'td'
            html += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>'
        html += '</table>'
        return html

    html_body = re.sub(r'(\|.+\|\n)+', convert_table, html_body)

    # List items
    html_body = re.sub(r'^- (.+)$', r'<li>\1</li>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'(<li>.*</li>\n?)+', lambda m: f'<ul>{m.group(0)}</ul>', html_body)

    # Paragraphs — wrap plain lines
    lines_out = []
    for line in html_body.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            lines_out.append(f'<p>{stripped}</p>')
        else:
            lines_out.append(line)
    html_body = '\n'.join(lines_out)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page {{ size: A4; margin: 2cm 2.2cm; }}
  body {{ font-family: 'Inter', -apple-system, Arial, sans-serif; font-size: 11pt; color: #1e293b; line-height: 1.6; }}
  h1 {{ font-size: 18pt; font-weight: 500; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6pt; margin-top: 0; }}
  h2 {{ font-size: 13pt; font-weight: 500; color: #0f172a; margin-top: 18pt; border-bottom: 1px solid #f1f5f9; padding-bottom: 4pt; }}
  h3 {{ font-size: 11pt; font-weight: 500; color: #334155; margin-top: 12pt; }}
  p  {{ margin: 5pt 0; }}
  blockquote {{ background: #f8fafc; border-left: 3px solid #3C3489; padding: 8pt 12pt; margin: 8pt 0; border-radius: 2pt; font-style: italic; color: #334155; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 8pt 0; }}
  th {{ background: #0f1623; color: #fff; padding: 5pt 8pt; text-align: left; font-weight: 500; }}
  td {{ padding: 4pt 8pt; border-bottom: 1px solid #f1f5f9; }}
  tr:nth-child(even) td {{ background: #f8fafc; }}
  ul {{ padding-left: 16pt; margin: 5pt 0; }}
  li {{ margin: 2pt 0; }}
  hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 12pt 0; }}
  strong {{ font-weight: 500; }}
  .footer {{ font-size: 8pt; color: #94a3b8; margin-top: 24pt; border-top: 1px solid #f1f5f9; padding-top: 6pt; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    HTML(string=full_html).write_pdf(str(pdf_path))
    return str(pdf_path)