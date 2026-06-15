/**
 * Compact label for pipeline status, agent identity, and risk signalling.
 * Use `status` prop for agent lifecycle states (waiting/analyzing/done),
 * `agent` prop for branded agent chips, or `variant` for semantic states.
 *
 * @example
 * <Badge status="analyzing" />
 * <Badge status="done" />
 * <Badge agent="farmer" />
 * <Badge variant="warning">Escalated</Badge>
 * <Badge variant="error">High risk</Badge>
 */
export interface BadgeProps {
  /** Semantic color variant */
  variant?: 'default' | 'success' | 'warning' | 'error' | 'purple';
  /** Render as a branded agent chip (overrides variant) */
  agent?: 'farmer' | 'logistics' | 'energy' | 'market' | 'regulator';
  /** Render pipeline status with spinner for "analyzing" (overrides agent + variant) */
  status?: 'waiting' | 'analyzing' | 'done';
  children?: React.ReactNode;
  style?: React.CSSProperties;
}
