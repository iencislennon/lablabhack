Status and identity labels across the pipeline — agent names, lifecycle states, risk signals.

```jsx
// Agent lifecycle (in card headers)
<Badge status="waiting" />
<Badge status="analyzing" />   // shows spinner
<Badge status="done" />

// Branded agent chips (sidebar, log, summaries)
<Badge agent="farmer" />
<Badge agent="regulator" />

// Semantic variants
<Badge variant="warning">Escalated</Badge>
<Badge variant="error">High risk</Badge>
<Badge variant="success">Policy approved</Badge>
<Badge variant="purple">Phase 3</Badge>
```

Border-radius is 4px. Text is always 10px / weight 500. The `analyzing` status renders an 8px spinning ring.
