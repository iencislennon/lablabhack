Use `AgentCard` in any pipeline status view to surface agent lifecycle and key outputs.

```jsx
// Idle state
<AgentCard agent="energy" status="waiting" model="Llama-3.3-70B" />

// Running state — amber badge with spinner, border pulses
<AgentCard agent="farmer" status="analyzing" model="Mixtral-8x7B" />

// Done state — full metrics, coloured risk bar, click to inspect JSON
<AgentCard
  agent="market"
  status="done"
  model="Qwen2.5-72B"
  metrics={[
    { icon: 'ti-trending-up', label: 'Demand signal', value: 'High' },
    { icon: 'ti-calendar',    label: 'Stock days',    value: '18.5' },
    { icon: 'ti-alert-triangle', label: 'Inflation risk', value: 'High' },
  ]}
  riskScore={0.74}
  riskLevel="high"
  onClick={() => openPanel('market')}
/>
```

`fullWidth` spans the card across all grid columns — use for Regulator (the 5th agent).
Card opacity drops to 45% when waiting and animates to 100% on completion.
