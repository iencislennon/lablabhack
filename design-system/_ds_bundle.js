/* @ds-bundle: {"format":3,"namespace":"CrisisNetDesignSystem_e35a87","components":[{"name":"AgentCard","sourcePath":"components/core/AgentCard.jsx"},{"name":"Badge","sourcePath":"components/core/Badge.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"}],"sourceHashes":{"components/core/AgentCard.jsx":"18cacb6a36e5","components/core/Badge.jsx":"b0d0405c3d5f","components/core/Button.jsx":"7bf421d0b909"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.CrisisNetDesignSystem_e35a87 = window.CrisisNetDesignSystem_e35a87 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/AgentCard.jsx
try { (() => {
const AGENT_META = {
  farmer: {
    label: 'Farmer',
    color: 'var(--color-farmer-text)',
    bg: 'var(--color-farmer-bg)',
    border: 'var(--color-farmer-border)',
    icon: 'ti-wheat'
  },
  logistics: {
    label: 'Logistics',
    color: 'var(--color-logistics-text)',
    bg: 'var(--color-logistics-bg)',
    border: 'var(--color-logistics-border)',
    icon: 'ti-truck'
  },
  energy: {
    label: 'Energy',
    color: 'var(--color-energy-text)',
    bg: 'var(--color-energy-bg)',
    border: 'var(--color-energy-border)',
    icon: 'ti-bolt'
  },
  market: {
    label: 'Market',
    color: 'var(--color-market-text)',
    bg: 'var(--color-market-bg)',
    border: 'var(--color-market-border)',
    icon: 'ti-trending-up'
  },
  regulator: {
    label: 'Regulator',
    color: 'var(--color-regulator-text)',
    bg: 'var(--color-regulator-bg)',
    border: 'var(--color-regulator-border)',
    icon: 'ti-building-bank'
  }
};
const RISK_COLOR = {
  low: 'var(--color-risk-low)',
  medium: 'var(--color-risk-medium)',
  high: 'var(--color-risk-high)',
  critical: 'var(--color-risk-high)'
};
function AgentCard({
  agent,
  status = 'waiting',
  model,
  metrics = [],
  riskScore,
  riskLevel = 'low',
  onClick,
  fullWidth,
  style
}) {
  const meta = AGENT_META[agent] || AGENT_META.farmer;
  const isRunning = status === 'analyzing';
  const isDone = status === 'done';
  const statusStyles = {
    waiting: {
      bg: '#f1f5f9',
      color: '#64748b',
      label: 'waiting'
    },
    analyzing: {
      bg: '#fef3c7',
      color: '#92400e',
      label: 'analyzing'
    },
    done: {
      bg: '#f0fdf4',
      color: '#15803d',
      label: 'done'
    }
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
      ...style
    }
  }, /* Header row */
  React.createElement('div', {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      marginBottom: '10px'
    }
  }, React.createElement('div', {
    style: {
      width: 'var(--agent-icon-size)',
      height: 'var(--agent-icon-size)',
      borderRadius: '50%',
      background: meta.bg,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0
    }
  }, React.createElement('i', {
    className: `ti ${meta.icon}`,
    style: {
      fontSize: '13px',
      color: meta.color
    }
  })), React.createElement('div', {
    style: {
      flex: 1,
      minWidth: 0
    }
  }, React.createElement('div', {
    style: {
      fontSize: '13px',
      fontWeight: 500,
      color: meta.color,
      fontFamily: 'var(--font-sans)'
    }
  }, meta.label), model && React.createElement('div', {
    style: {
      fontSize: '10px',
      color: 'var(--color-text-muted)',
      fontFamily: 'var(--font-sans)',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, model)), React.createElement('span', {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '4px',
      padding: '2px 8px',
      borderRadius: '4px',
      fontSize: '10px',
      fontWeight: 500,
      fontFamily: 'var(--font-sans)',
      background: ss.bg,
      color: ss.color,
      flexShrink: 0
    }
  }, isRunning && React.createElement('span', {
    style: {
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      border: '1.5px solid currentColor',
      borderTopColor: 'transparent',
      display: 'inline-block',
      animation: 'badge-spin 0.7s linear infinite'
    }
  }), ss.label)), /* Metrics */
  isDone && metrics.length > 0 && React.createElement('div', {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '4px',
      marginBottom: '10px',
      animation: 'fade-in 0.3s ease'
    }
  }, metrics.map((m, i) => React.createElement('div', {
    key: i,
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px'
    }
  }, React.createElement('i', {
    className: `ti ${m.icon || 'ti-point'}`,
    style: {
      fontSize: '11px',
      color: 'var(--color-text-muted)',
      width: '14px'
    }
  }), React.createElement('span', {
    style: {
      fontSize: '11px',
      color: 'var(--color-text-secondary)',
      fontFamily: 'var(--font-sans)',
      flex: 1
    }
  }, m.label), React.createElement('span', {
    style: {
      fontSize: '11px',
      fontWeight: 500,
      color: 'var(--color-text-primary)',
      fontFamily: 'var(--font-sans)'
    }
  }, m.value)))), /* Risk bar */
  React.createElement('div', {
    style: {
      height: 'var(--risk-bar-height)',
      background: 'var(--color-border-subtle)',
      borderRadius: '2px',
      overflow: 'hidden'
    }
  }, React.createElement('div', {
    style: {
      height: '100%',
      width: isDone ? `${Math.round((riskScore || 0) * 100)}%` : '0%',
      background: RISK_COLOR[riskLevel] || RISK_COLOR.low,
      transition: 'width 0.6s ease',
      borderRadius: '2px'
    }
  })));
}
Object.assign(__ds_scope, { AgentCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/AgentCard.jsx", error: String((e && e.message) || e) }); }

// components/core/Badge.jsx
try { (() => {
const AGENT_META = {
  farmer: {
    label: 'Farmer',
    color: 'var(--color-farmer-text)',
    bg: 'var(--color-farmer-bg)',
    border: 'var(--color-farmer-border)'
  },
  logistics: {
    label: 'Logistics',
    color: 'var(--color-logistics-text)',
    bg: 'var(--color-logistics-bg)',
    border: 'var(--color-logistics-border)'
  },
  energy: {
    label: 'Energy',
    color: 'var(--color-energy-text)',
    bg: 'var(--color-energy-bg)',
    border: 'var(--color-energy-border)'
  },
  market: {
    label: 'Market',
    color: 'var(--color-market-text)',
    bg: 'var(--color-market-bg)',
    border: 'var(--color-market-border)'
  },
  regulator: {
    label: 'Regulator',
    color: 'var(--color-regulator-text)',
    bg: 'var(--color-regulator-bg)',
    border: 'var(--color-regulator-border)'
  }
};
const STATUS_STYLES = {
  waiting: {
    bg: '#f1f5f9',
    color: '#64748b',
    label: 'waiting'
  },
  analyzing: {
    bg: '#fef3c7',
    color: '#92400e',
    label: 'analyzing'
  },
  done: {
    bg: 'var(--color-success-bg)',
    color: 'var(--color-success-text)',
    label: 'done'
  }
};
function Badge({
  variant = 'default',
  agent,
  status,
  children,
  style
}) {
  if (status) {
    const s = STATUS_STYLES[status] || STATUS_STYLES.waiting;
    return React.createElement('span', {
      style: {
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '10px',
        fontWeight: 500,
        fontFamily: 'var(--font-sans)',
        background: s.bg,
        color: s.color,
        ...style
      }
    }, status === 'analyzing' && React.createElement('span', {
      style: {
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        border: '1.5px solid currentColor',
        borderTopColor: 'transparent',
        display: 'inline-block',
        animation: 'badge-spin 0.7s linear infinite'
      }
    }), s.label);
  }
  if (agent && AGENT_META[agent]) {
    const a = AGENT_META[agent];
    return React.createElement('span', {
      style: {
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '10px',
        fontWeight: 500,
        fontFamily: 'var(--font-sans)',
        background: a.bg,
        color: a.color,
        border: `1px solid ${a.border}`,
        ...style
      }
    }, a.label);
  }
  const VARIANT_MAP = {
    default: {
      bg: '#f1f5f9',
      color: '#475569'
    },
    success: {
      bg: 'var(--color-success-bg)',
      color: 'var(--color-success-text)'
    },
    warning: {
      bg: 'var(--color-escalation-bg)',
      color: 'var(--color-escalation-text)'
    },
    error: {
      bg: 'var(--color-risk-high-bg)',
      color: 'var(--color-risk-high)'
    },
    purple: {
      bg: '#ede9fe',
      color: '#5b21b6'
    }
  };
  const v = VARIANT_MAP[variant] || VARIANT_MAP.default;
  return React.createElement('span', {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      padding: '2px 8px',
      borderRadius: '4px',
      fontSize: '10px',
      fontWeight: 500,
      fontFamily: 'var(--font-sans)',
      background: v.bg,
      color: v.color,
      ...style
    }
  }, children);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Badge.jsx", error: String((e && e.message) || e) }); }

// components/core/Button.jsx
try { (() => {
function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
  children,
  style
}) {
  const base = {
    fontFamily: 'var(--font-sans)',
    fontWeight: 'var(--font-weight-medium)',
    fontSize: size === 'sm' ? '11px' : '13px',
    lineHeight: 1,
    border: '1px solid transparent',
    borderRadius: 'var(--radius-md)',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    padding: size === 'sm' ? '5px 10px' : '7px 14px',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    transition: 'background 0.1s, border-color 0.1s',
    whiteSpace: 'nowrap',
    ...style
  };
  const variants = {
    primary: {
      background: 'var(--color-navy)',
      color: '#ffffff',
      borderColor: 'var(--color-navy)'
    },
    secondary: {
      background: 'transparent',
      color: 'var(--color-text-primary)',
      borderColor: 'var(--color-border)'
    },
    danger: {
      background: 'transparent',
      color: 'var(--color-error)',
      borderColor: 'var(--color-error)'
    },
    ghost: {
      background: 'transparent',
      color: 'var(--color-text-secondary)',
      borderColor: 'transparent'
    }
  };
  return React.createElement('button', {
    onClick: disabled ? undefined : onClick,
    disabled,
    style: {
      ...base,
      ...variants[variant]
    }
  }, children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

__ds_ns.AgentCard = __ds_scope.AgentCard;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Button = __ds_scope.Button;

})();
