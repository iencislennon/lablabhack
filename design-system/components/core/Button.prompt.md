Use `Button` for any discrete action in the dashboard — pipeline controls, panel closes, report downloads.

```jsx
<Button variant="primary" onClick={handleRun}>Run Pipeline</Button>
<Button variant="danger" onClick={handleStop}>Stop</Button>
<Button variant="secondary" size="sm">Download Report</Button>
<Button variant="ghost" size="sm" disabled>Waiting…</Button>
```

Variants: `primary` (navy fill), `secondary` (outline), `danger` (red outline), `ghost` (no border).
Sizes: `md` (default, 13px), `sm` (11px, 5px vertical padding).
Border-radius is capped at 6px per brand rules. No drop-shadows, no gradients.
