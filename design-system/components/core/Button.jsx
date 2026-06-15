export function Button({ variant = 'primary', size = 'md', disabled = false, onClick, children, style }) {
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
    ...style,
  };

  const variants = {
    primary: {
      background: 'var(--color-navy)',
      color: '#ffffff',
      borderColor: 'var(--color-navy)',
    },
    secondary: {
      background: 'transparent',
      color: 'var(--color-text-primary)',
      borderColor: 'var(--color-border)',
    },
    danger: {
      background: 'transparent',
      color: 'var(--color-error)',
      borderColor: 'var(--color-error)',
    },
    ghost: {
      background: 'transparent',
      color: 'var(--color-text-secondary)',
      borderColor: 'transparent',
    },
  };

  return React.createElement('button', {
    onClick: disabled ? undefined : onClick,
    disabled,
    style: { ...base, ...variants[variant] },
  }, children);
}
