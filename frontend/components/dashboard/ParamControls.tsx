import { motion } from "motion/react";
import type { Station } from "@/data/stations";

export type Params = {
  temperature: number;
  rainfall: number;
  humidity: number;
  riverFlow: number;
  rollingFlow: number;
};

const fields: { key: keyof Params; label: string; min: number; max: number; step: number; suffix: string }[] = [
  { key: "temperature", label: "Temperature", min: -5, max: 45, step: 0.5, suffix: "°C" },
  { key: "rainfall", label: "Rainfall (24h)", min: 0, max: 300, step: 1, suffix: "mm" },
  { key: "humidity", label: "Humidity", min: 0, max: 100, step: 1, suffix: "%" },
  { key: "riverFlow", label: "River Flow", min: 0, max: 4000, step: 1, suffix: "m³/s" },
  { key: "rollingFlow", label: "7-day Rolling Flow", min: 1, max: 4000, step: 1, suffix: "m³/s" },
];

export function ParamControls({
  station,
  params,
  onChange,
  onRun,
  busy,
}: {
  station: Station;
  params: Params;
  onChange: (p: Params) => void;
  onRun: () => void;
  busy: boolean;
}) {
  return (
    <motion.div
      initial={{ y: 24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.25 }}
      className="glass rounded-2xl p-4"
    >
      <div className="mb-3 flex items-center justify-between">
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">Sensor inputs</p>
          <h2 className="text-lg font-semibold text-foreground">
            {station.name} <span className="text-muted-foreground">· {station.river}</span>
          </h2>
        </div>
        <button
          onClick={onRun}
          disabled={busy}
          className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-primary to-[oklch(0.7_0.18_215)] px-4 py-2 text-sm font-semibold text-primary-foreground shadow-[0_8px_24px_oklch(0.82_0.16_200/0.35)] transition-transform hover:scale-[1.03] active:scale-[0.97] disabled:opacity-60"
        >
          <span className="relative z-10">{busy ? "Analyzing…" : "Run Analysis"}</span>
          {busy && <span className="absolute inset-0 shimmer" aria-hidden />}
        </button>
      </div>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-5">
        {fields.map((f) => (
          <label key={f.key} className="rounded-xl bg-background/40 p-3">
            <span className="flex items-center justify-between text-[11px] uppercase tracking-wider text-muted-foreground">
              <span>{f.label}</span>
              <span className="font-mono text-foreground/90 tabular-nums">
                {params[f.key].toFixed(f.step < 1 ? 1 : 0)}
                {f.suffix}
              </span>
            </span>
            <input
              type="range"
              min={f.min}
              max={f.max}
              step={f.step}
              value={params[f.key]}
              onChange={(e) => onChange({ ...params, [f.key]: Number(e.target.value) })}
              className="mt-2 w-full accent-[var(--hydro-cyan)]"
            />
          </label>
        ))}
      </div>
      <p className="mt-3 text-[11px] text-muted-foreground">
        Ecological flow threshold for {station.name}: <span className="text-foreground">{station.ecoThreshold} m³/s</span>
      </p>
    </motion.div>
  );
}