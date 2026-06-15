const AGENT_META = {
  farmer:    { label: 'Farmer',    color: 'var(--color-farmer-text)',    bg: 'var(--color-farmer-bg)',    border: 'var(--color-farmer-border)' },
  logistics: { label: 'Logistics', color: 'var(--color-logistics-text)', bg: 'var(--color-logistics-bg)', border: 'var(--color-logistics-border)' },
  energy:    { label: 'Energy',    color: 'var(--color-energy-text)',    bg: 'var(--color-energy-bg)',    border: 'var(--color-energy-border)' },
  market:    { label: 'Market',    color: 'var(--color-market-text)',    bg: 'var(--color-market-bg)',    border: 'var(--color-market-border)' },
  regulator: { label: 'Regulator', color: 'var(--color-regulator-text)', bg: 'var(--color-regulator-bg)', border: 'var(--color-regulator-border)' },
};

const STATUS_STYLES = {
  waiting:   { bg: '#f1f5f9', color: '#64748b', label: 'waiting' },
  analyzing: { bg: '#fef3c7', color: '#92400e', label: 'analyzing' },
  done:      { bg: 'var(--color-success-bg)', color: 'var(--color-success-text)', label: 'done' },
};

export function Badge({ variant = 'default', agent, status, children, style }) {
  if (status) {
    const s = STATUS_STYLES[status] || STATUS_STYLES.waiting;
    return React.createElement('span', {
      style: {
        display: 'inline-flex', alignItems: 'center', gap: '4px',
        padding: '2px 8px', borderRadius: '4px', fontSize: '10px',
        fontWeight: 500, fontFamily: 'var(--font-sans)',
        background: s.bg, color: s.color,
        ...style,
      },
    },
      status === 'analyzing' && React.createElement('span', {
        style: {
          width: '8px', height: '8px', borderRadius: '50%',
          border: '1.5px solid currentColor',
          borderTopColor: 'transparent',
          display: 'inline-block',
          animation: 'badge-spin 0.7s linear infinite',
        }
      }),
      s.label
    );
  }

  if (agent && AGENT_META[agent]) {
    const a = AGENT_META[agent];
    return React.createElement('span', {
      style: {
        display: 'inline-flex', alignItems: 'center',
        padding: '2px 8px', borderRadius: '4px', fontSize: '10px',
        fontWeight: 500, fontFamily: 'var(--font-sans)',
        background: a.bg, color: a.color, border: `1px solid ${a.border}`,
        ...style,
      },
    }, a.label);
  }

  const VARIANT_MAP = {
    default:  { bg: '#f1f5f9', color: '#475569' },
    success:  { bg: 'var(--color-success-bg)',    color: 'var(--color-success-text)' },
    warning:  { bg: 'var(--color-escalation-bg)', color: 'var(--color-escalation-text)' },
    error:    { bg: 'var(--color-risk-high-bg)',   color: 'var(--color-risk-high)' },
    purple:   { bg: '#ede9fe', color: '#5b21b6' },
  };

  const v = VARIANT_MAP[variant] || VARIANT_MAP.default;
  return React.createElement('span', {
    style: {
      display: 'inline-flex', alignItems: 'center',
      padding: '2px 8px', borderRadius: '4px', fontSize: '10px',
      fontWeight: 500, fontFamily: 'var(--font-sans)',
      background: v.bg, color: v.color,
      ...style,
    },
  }, children);
}
