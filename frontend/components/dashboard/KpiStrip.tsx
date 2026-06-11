import { motion } from "motion/react";
import { useEffect, useState } from "react";
import type { EngineResult } from "@/lib/aquaguard-engine";
import type { Station } from "@/data/stations";

function CountUp({ value, suffix = "", decimals = 0 }: { value: number; suffix?: string; decimals?: number }) {
  const [n, setN] = useState(0);
  useEffect(() => {
    const start = performance.now();
    const from = n;
    const to = value;
    const dur = 700;
    let raf = 0;
    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      setN(from + (to - from) * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);
  return (
    <span className="tabular-nums">
      {n.toFixed(decimals)}
      {suffix}
    </span>
  );
}

const riskTint: Record<string, string> = {
  low: "from-[oklch(0.78_0.18_155)] to-[oklch(0.65_0.18_180)]",
  moderate: "from-[oklch(0.85_0.16_120)] to-[oklch(0.78_0.18_155)]",
  high: "from-[oklch(0.82_0.18_75)] to-[oklch(0.78_0.18_45)]",
  critical: "from-[oklch(0.68_0.24_25)] to-[oklch(0.55_0.22_15)]",
};

export function KpiStrip({ result, station }: { result: EngineResult | null; station?: Station }) {
  const tiles = [
    {
      label: "Predicted Risk",
      value: result ? Math.round(result.predictedRisk.score * 100) : 0,
      suffix: "%",
      sub: result?.predictedRisk.level.toUpperCase() ?? "—",
      tint: riskTint[result?.predictedRisk.level ?? "low"],
    },
    {
      label: "IFC PS4 Compliance",
      value: result ? Math.min(200, Math.round(result.compliance.ratio * 100)) : 0,
      suffix: "%",
      sub: result?.compliance.compliant ? "COMPLIANT" : "NON-COMPLIANT",
      tint: result?.compliance.compliant
        ? "from-[oklch(0.82_0.16_200)] to-[oklch(0.78_0.18_155)]"
        : "from-[oklch(0.68_0.24_25)] to-[oklch(0.82_0.18_75)]",
    },
    {
      label: "ESG Score",
      value: result?.esgScore ?? 0,
      suffix: "/100",
      sub: (result?.esgScore ?? 0) >= 70 ? "GOOD" : (result?.esgScore ?? 0) >= 50 ? "AT RISK" : "POOR",
      tint: "from-[oklch(0.82_0.16_200)] to-[oklch(0.78_0.18_280)]",
    },
    {
      label: "Active Alerts",
      value: result?.alerts.length ?? 0,
      suffix: "",
      sub: (result?.alerts.length ?? 0) > 0 ? "ACTION REQUIRED" : "ALL CLEAR",
      tint: (result?.alerts.length ?? 0) > 0
        ? "from-[oklch(0.82_0.18_75)] to-[oklch(0.68_0.24_25)]"
        : "from-[oklch(0.78_0.18_155)] to-[oklch(0.82_0.16_200)]",
    },
  ];

  if (station) {
    tiles.push({
      label: "Eco Threshold",
      value: station.ecoThreshold,
      suffix: " m³/s",
      sub: (result?.compliance.compliant ?? true) ? "COMPLIANT" : "NON-COMPLIANT",
      tint: (result?.compliance.compliant ?? true)
        ? "from-[oklch(0.78_0.18_155)] to-[oklch(0.82_0.16_200)]"
        : "from-[oklch(0.82_0.18_75)] to-[oklch(0.68_0.24_25)]",
    });
  }

  return (
    <div className="grid grid-cols-2 gap-3 px-3 md:grid-cols-5">
      {tiles.map((t, i) => (
        <motion.div
          key={t.label}
          initial={{ y: 24, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 + i * 0.08, ease: "easeOut" }}
          className="glass relative overflow-hidden rounded-2xl p-4"
        >
          <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${t.tint}`} />
          <p className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">{t.label}</p>
          <p className="mt-1 flex items-baseline gap-1 text-3xl font-bold text-foreground">
            <CountUp value={t.value} suffix={t.suffix} />
          </p>
          <p className={`mt-1 text-[11px] font-semibold tracking-wider bg-gradient-to-r ${t.tint} bg-clip-text text-transparent`}>
            {t.sub}
          </p>
        </motion.div>
      ))}
    </div>
  );
}