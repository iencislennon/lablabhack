const AGENT_META = {
  farmer:    { label: 'Farmer',    color: 'var(--color-farmer-text)',    bg: 'var(--color-farmer-bg)',    border: 'var(--color-farmer-border)',   icon: 'ti-wheat' },
  logistics: { label: 'Logistics', color: 'var(--color-logistics-text)', bg: 'var(--color-logistics-bg)', border: 'var(--color-logistics-border)', icon: 'ti-truck' },
  energy:    { label: 'Energy',    color: 'var(--color-energy-text)',    bg: 'var(--color-energy-bg)',    border: 'var(--color-energy-border)',   icon: 'ti-bolt' },
  market:    { label: 'Market',    color: 'var(--color-market-text)',    bg: 'var(--color-market-bg)',    border: 'var(--color-market-border)',   icon: 'ti-trending-up' },
  regulator: { label: 'Regulator', color: 'var(--color-regulator-text)', bg: 'var(--color-regulator-bg)', border: 'var(--color-regulator-border)', icon: 'ti-building-bank' },
};

const RISK_COLOR = { low: 'var(--color-risk-low)', medium: 'var(--color-risk-medium)', high: 'var(--color-risk-high)', critical: 'var(--color-risk-high)' };

export function AgentCard({ agent, status = 'waiting', model, metrics = [], riskScore, riskLevel = 'low', onClick, fullWidth, style }) {
  const meta = AGENT_META[agent] || AGENT_META.farmer;
  const isRunning = status === 'analyzing';
  const isDone = status === 'done';

  const statusStyles = {
    waiting:   { bg: '#f1f5f9', color: '#64748b', label: 'waiting' },
    analyzing: { bg: '#fef3c7', color: '#92400e', label: 'analyzing' },
    done:      { bg: '#f0fdf4', color: '#15803d', label: 'done' },
  };
  const ss = statusStyles[status] || statusStyles.waiting;

  return React.createElement('div', {
    onClick,
    style: {
      background: '#ffffff',
      border: `1px solid ${isRunning ? meta.border : isDone ? meta.border : 'var(--color-border)'}`,
      borderRadius: 'var(--radius-lg)',
      padding: 'var(--pad-card)',
      opacity: status === 'waiting' ? 0.45 : 1,
      transition: 'opacity 0.3s, border-color 0.2s',
      cursor: isDone ? 'pointer' : 'default',
      gridColumn: fullWidth ? '1 / -1' : undefined,
      animation: isRunning ? 'agent-pulse 2s ease-in-out infinite' : undefined,
      ...style,
    },
  },
    /* Header row */
    React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' } },
      React.createElement('div', {
        style: {
          width: 'var(--agent-icon-size)', height: 'var(--agent-icon-size)',
          borderRadius: '50%', background: meta.bg,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0,
        }
      },
        React.createElement('i', { className: `ti ${meta.icon}`, style: { fontSize: '13px', color: meta.color } })
      ),
      React.createElement('div', { style: { flex: 1, minWidth: 0 } },
        React.createElement('div', { style: { fontSize: '13px', fontWeight: 500, color: meta.color, fontFamily: 'var(--font-sans)' } }, meta.label),
        model && React.createElement('div', { style: { fontSize: '10px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-sans)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' } }, model),
      ),
      React.createElement('span', {
        style: {
          display: 'inline-flex', alignItems: 'center', gap: '4px',
          padding: '2px 8px', borderRadius: '4px', fontSize: '10px',
          fontWeight: 500, fontFamily: 'var(--font-sans)',
          background: ss.bg, color: ss.color, flexShrink: 0,
        }
      },
        isRunning && React.createElement('span', {
          style: {
            width: '8px', height: '8px', borderRadius: '50%',
            border: '1.5px solid currentColor', borderTopColor: 'transparent',
            display: 'inline-block', animation: 'badge-spin 0.7s linear infinite',
          }
        }),
        ss.label
      )
    ),

    /* Metrics */
    isDone && metrics.length > 0 && React.createElement('div', {
      style: { display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '10px', animation: 'fade-in 0.3s ease' }
    },
      metrics.map((m, i) =>
        React.createElement('div', { key: i, style: { display: 'flex', alignItems: 'center', gap: '8px' } },
          React.createElement('i', { className: `ti ${m.icon || 'ti-point'}`, style: { fontSize: '11px', color: 'var(--color-text-muted)', width: '14px' } }),
          React.createElement('span', { style: { fontSize: '11px', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-sans)', flex: 1 } }, m.label),
          React.createElement('span', { style: { fontSize: '11px', fontWeight: 500, color: 'var(--color-text-primary)', fontFamily: 'var(--font-sans)' } }, m.value),
        )
      )
    ),

    /* Risk bar */
    React.createElement('div', {
      style: { height: 'var(--risk-bar-height)', background: 'var(--color-border-subtle)', borderRadius: '2px', overflow: 'hidden' }
    },
      React.createElement('div', {
        style: {
          height: '100%',
          width: isDone ? `${Math.round((riskScore || 0) * 100)}%` : '0%',
          background: RISK_COLOR[riskLevel] || RISK_COLOR.low,
          transition: 'width 0.6s ease',
          borderRadius: '2px',
        }
      })
    )
  );
}
