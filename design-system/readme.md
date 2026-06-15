# CrisisNet Design System
### FoodEnergyMAS · Multi-Agent Food & Energy Security

---

## Overview

**CrisisNet** is the design identity for the **FoodEnergyMAS** multi-agent system — a UN/government-grade decision-support tool for food and energy security coordination. Five AI agents run in parallel across a shared "Band Room", detect conflicts, and issue policy decisions with human-in-the-loop escalation.

The design ethos is **Bloomberg Terminal meets UN OCHA situation room**: flat, data-dense, authoritative. No gradients. No drop-shadows. No startup ornamentation.

**Source repositories:**
- https://github.com/iencislennon/lablabhack — Primary codebase (frontend, backend, agent config)

Explore the repo to understand the full agent schema, WebSocket event contracts, and escalation thresholds before building new screens.

---

## CONTENT FUNDAMENTALS

**Tone:** Operational, terse, precise. This is crisis management software — copy should be as spare as a military briefing. No fluff.

**Casing:** Sentence case everywhere. Never ALL CAPS except for metric labels and terminal identifiers (e.g. `BAND ROOM`, `DEFICIT PCT`).

**Voice:** Third-person, impersonal. "Regulator decision" not "Your decision." "Confidence score" not "How confident we are."

**Numbers:** Always show units. `34.2%` not `34.2`. `$0.187/kWh` not `0.187`. `18.5 days` not `18.5`.

**Actions:** Imperative verbs — "Run Pipeline", "Download report", "View JSON", "Stop". Never passive ("Pipeline can be run").

**Status labels:** `waiting`, `analyzing`, `done` — lowercase, no decoration.

**Emoji:** Never used in the product UI. Only in the project README as informal shorthand.

**Error states:** Specific and actionable. "Logistics bottleneck at port_odessa" not "An error occurred."

---

## VISUAL FOUNDATIONS

### Colors
Two-tier system: **surface/structure** (navy sidebar + white main) and **semantic** (per-agent + status).

**Structure:**
- Sidebar: `#0f1623` (near-black navy)
- Main background: `#ffffff`
- Borders: `#e2e8f0` (standard), `#f1f5f9` (subtle)
- Text primary: `#0f1623` / secondary: `#475569` / muted: `#94a3b8`

**Agent identity (5-color system — immutable):**

| Agent     | Text     | Background | Border   |
|-----------|----------|------------|----------|
| Farmer    | #0F6E56  | #E1F5EE    | #6DCFB0  |
| Logistics | #085041  | #C8EDE0    | #4DB896  |
| Energy    | #633806  | #FAEEDA    | #FAC775  |
| Market    | #712B13  | #FAECE7    | #F5C4B3  |
| Regulator | #3C3489  | #EEEDFE    | #AFA9EC  |

**Status palette:**
- Risk HIGH: `#e53e3e` / MEDIUM: `#dd6b20` / LOW: `#38a169`
- Escalation: `#f59e0b` bg `#fffbeb`
- Success: `#22c55e` bg `#f0fdf4`
- Error: `#ef4444` bg `#fef2f2`
- Purple accent (phase stepper, progress bar): `#7c3aed`

### Typography
**Font:** Inter — loaded from Google Fonts. Two weights only: **400 (regular)** and **500 (medium)**. No bold (600+), no light (300−).

Font families: `'Inter', -apple-system, sans-serif` (UI) and `'JetBrains Mono'` (terminal, timestamps, JSON).

Size scale: 10px → 11px → 12px → 13px → 15px → 20px. The majority of UI lives at 11–13px.

### Backgrounds
White main content. Navy sidebar. No imagery, no textures, no patterns. Cards are white with a 1px `#e2e8f0` border, 8px radius (maximum allowed).

### Spacing
4px grid. Component padding follows the pad-* tokens (`--pad-card: 14px 16px`, `--pad-button: 7px 14px`).

### Borders & Radius
Maximum border-radius: **8px** (never exceed this). Standard: 6px (buttons, badges). Agent cards: 8px. Badges: 4px. No pill shapes, no circles for non-icon elements.

### Shadows
**None.** Depth is communicated via border color changes and opacity shifts.

### Animations
Only purposeful, subtle animations:
- **Agent border pulse** (`2s ease-in-out infinite`) on running cards — border color fades between `#e2e8f0` and agent border color
- **Badge spinner** (`0.7s linear infinite`) on "analyzing" status
- **Phase circle pulse** (`scale(1.1)`, `1.6s`) on active step
- **Fade-in** (`0.3s ease`) when metrics or panels appear
- **Progress bar sweep** when pipeline is running

No bounce, no spring, no slide entrances. No infinite decorative loops outside of active-state indicators.

### Hover / Press States
- Buttons: no transform, no shadow — background darkens slightly (handled by browser for `<button>`)
- Agent cards: border color darkens on hover when `status=done` (cursor pointer signal is sufficient)
- Links: underline on hover

### Cards
White background. `1px solid #e2e8f0` border. 8px radius. `14px 16px` padding. No shadow. Agent cards gain the agent's border color when running or done.

### Opacity
Idle/waiting agent cards render at 38–40% opacity — the primary affordance for "not yet active." Full opacity on transition to `analyzing` or `done`.

### Icons
Tabler Icons (outline style, v3.31). CDN: `https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.31.0/dist/tabler-icons.min.css`. Used as `<i class="ti ti-{name}">`.

**Core icon set:**
`ti-wheat` (Farmer), `ti-truck` (Logistics), `ti-bolt` (Energy), `ti-trending-up` (Market), `ti-building-bank` (Regulator), `ti-alert-triangle` (warning), `ti-check` (success), `ti-download` (export), `ti-x` (close), `ti-code` (JSON), `ti-refresh` (restart), `ti-leaf` (logo), `ti-ship` (import), `ti-tag` (price controls), `ti-gauge` (confidence), `ti-player-play` / `ti-player-stop` (pipeline controls).

---

## ICONOGRAPHY

Source: **Tabler Icons** (web font, outline style). No custom SVGs, no PNG icons, no emoji in product UI.

Load via CDN — no local copy needed. Usage pattern: `<i class="ti ti-{name}" style="font-size: 14px; color: ..." />`.

Icon sizes:
- 28px icon circle container → 13px icon inside (agent card header)
- 14px inline (metric rows, conflict panel)
- 12px compact (button label, badge, table actions)
- 16px medium (decision card header, panel close)

---

## FILE INDEX

```
CrisisNet Design System
├── styles.css                          Root stylesheet (import chain)
├── readme.md                           This file
├── SKILL.md                            Agent skill definition
│
├── tokens/
│   ├── colors.css                      All color custom properties
│   ├── typography.css                  Font stack + size/weight scale
│   └── spacing.css                     4px grid + radius + layout tokens
│
├── components/core/
│   ├── Button.jsx / .d.ts / .prompt.md  Primary action button (4 variants)
│   ├── Badge.jsx / .d.ts / .prompt.md   Status + agent + semantic labels
│   ├── AgentCard.jsx / .d.ts / .prompt.md  Agent lifecycle card
│   └── core.card.html                  Component showcase card (@dsCard)
│
├── guidelines/
│   ├── agent-colors.card.html          Agent color swatches
│   ├── status-colors.card.html         Risk / escalation / success
│   ├── surface-colors.card.html        Navy / white / text hierarchy
│   ├── type-scale.card.html            Inter type ramp
│   ├── mono-type.card.html             JetBrains Mono terminal specimens
│   └── spacing.card.html              4px grid + radius tokens
│
└── ui_kits/foodenergymas/
    └── index.html                      Full FoodEnergyMAS dashboard
                                        (React 18, inline styles, WebSocket
                                         with simulation fallback)
```

### Components

| Component  | Props summary |
|------------|---------------|
| `Button`   | `variant` (primary/secondary/danger/ghost), `size` (sm/md), `disabled` |
| `Badge`    | `status` (waiting/analyzing/done), `agent` (5 agents), `variant` (semantic) |
| `AgentCard`| `agent`, `status`, `model`, `metrics[]`, `riskScore`, `riskLevel`, `fullWidth` |

### UI Kit: FoodEnergyMAS Dashboard

Full-page React 18 app. Connects to `ws://localhost:8000/ws` and auto-falls back to an event simulation when the backend is unavailable. Covers all 13 WebSocket event types, both clean and escalated final-decision states, conflict panel, Band Room terminal, and JSON inspector slide-in panel.

Start the backend per the [lablabhack README](https://github.com/iencislennon/lablabhack) or simply open the file standalone and click **Run Pipeline** for the simulated demo.
