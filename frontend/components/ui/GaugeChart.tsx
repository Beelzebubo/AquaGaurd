export function GaugeChart({
  value,
  max = 100,
  label,
  color,
  size = 140,
  strokeWidth = 10,
}: {
  value: number;
  max?: number;
  label: string;
  color: string;
  size?: number;
  strokeWidth?: number;
}) {
  const pct = Math.min(value / max, 1);
  const radius = (size - strokeWidth) / 2;
  const circ = 2 * Math.PI * radius;
  const offset = circ * (1 - pct);
  const cx = size / 2;
  const cy = size / 2;

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} className="drop-shadow-[0_0_12px_oklch(0.82_0.16_200/0.2)]">
        <circle cx={cx} cy={cy} r={radius} fill="none" stroke="oklch(0.3 0.04 230 / 0.5)" strokeWidth={strokeWidth} />
        <circle
          cx={cx}
          cy={cy}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${cx} ${cy})`}
          style={{ transition: "stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)" }}
        />
        <text x={cx} y={cy} textAnchor="middle" dominantBaseline="central" fill="oklch(0.96 0.01 220)" fontSize={24} fontWeight={700} fontFamily="'Space Grotesk', system-ui, sans-serif">
          {Math.round(value)}
        </text>
        <text x={cx} y={cy + 18} textAnchor="middle" dominantBaseline="central" fill="oklch(0.72 0.02 220)" fontSize={10} fontWeight={500}>
          /{max}
        </text>
      </svg>
      <span className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">{label}</span>
    </div>
  );
}
