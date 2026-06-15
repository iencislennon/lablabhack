/**
 * Agent status card for pipeline views. Shows icon, name, model, lifecycle badge, metrics, and risk bar.
 * Click when `status="done"` to open the JSON inspector panel.
 *
 * @example
 * <AgentCard
 *   agent="farmer"
 *   status="done"
 *   model="Mixtral-8x7B"
 *   metrics={[{ icon: 'ti-alert-triangle', label: 'Deficit', value: '34.2%' }]}
 *   riskScore={0.78}
 *   riskLevel="high"
 *   onClick={() => openPanel('farmer')}
 * />
 */
export interface AgentCardProps {
  agent: 'farmer' | 'logistics' | 'energy' | 'market' | 'regulator';
  status?: 'waiting' | 'analyzing' | 'done';
  /** Short model name shown below agent name */
  model?: string;
  /** Key metrics shown when status is done */
  metrics?: Array<{ icon?: string; label: string; value: string }>;
  /** Risk score 0–1 for the fill bar */
  riskScore?: number;
  /** Determines bar color */
  riskLevel?: 'low' | 'medium' | 'high' | 'critical';
  /** Callback fired when card is clicked (only meaningful when done) */
  onClick?: () => void;
  /** Span full grid width (for Regulator) */
  fullWidth?: boolean;
  style?: React.CSSProperties;
}
