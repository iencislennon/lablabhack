/**
 * Primary action trigger for the FoodEnergyMAS dashboard.
 * Use `primary` for the main CTA (Run Pipeline), `danger` for Stop, `secondary` for alternatives.
 *
 * @example
 * <Button variant="primary" onClick={run}>Run Pipeline</Button>
 * <Button variant="danger" onClick={stop}>Stop</Button>
 * <Button variant="secondary" size="sm">Download Report</Button>
 *
 */
export interface ButtonProps {
  /** Visual style */
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  /** Size — default md */
  size?: 'sm' | 'md';
  disabled?: boolean;
  onClick?: () => void;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}
