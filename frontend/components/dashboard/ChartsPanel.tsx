import { motion } from "motion/react";
import { Area, AreaChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { EngineResult } from "@/lib/aquaguard-engine";

export function ChartsPanel({ result, ecoThreshold }: { result: EngineResult | null; ecoThreshold: number }) {
  const data = result?.forecast ?? [];
  return (
    <motion.div
      initial={{ x: 24, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="glass flex h-full flex-col gap-3 rounded-2xl p-4"
    >
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">24-hour forecast</p>
        <h3 className="text-base font-semibold text-foreground">River flow vs ecological threshold</h3>
      </div>
      <div className="h-44 w-full">
        <ResponsiveContainer>
          <AreaChart data={data} margin={{ top: 6, right: 8, left: -16, bottom: 0 }}>
            <defs>
              <linearGradient id="flowG" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="oklch(0.82 0.16 200)" stopOpacity={0.65} />
                <stop offset="100%" stopColor="oklch(0.82 0.16 200)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="oklch(0.4 0.04 230 / 0.25)" strokeDasharray="3 3" />
            <XAxis dataKey="hour" stroke="oklch(0.72 0.02 220)" fontSize={10} tickFormatter={(v) => `${v}h`} />
            <YAxis stroke="oklch(0.72 0.02 220)" fontSize={10} />
            <Tooltip
              contentStyle={{
                background: "oklch(0.16 0.03 235 / 0.9)",
                border: "1px solid oklch(0.4 0.04 230 / 0.5)",
                borderRadius: 12,
                color: "oklch(0.96 0.01 220)",
                fontSize: 12,
              }}
            />
            <Area type="monotone" dataKey="flow" stroke="oklch(0.82 0.16 200)" strokeWidth={2} fill="url(#flowG)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">Disaster risk trend</p>
      </div>
      <div className="h-32 w-full">
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 6, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid stroke="oklch(0.4 0.04 230 / 0.25)" strokeDasharray="3 3" />
            <XAxis dataKey="hour" stroke="oklch(0.72 0.02 220)" fontSize={10} tickFormatter={(v) => `${v}h`} />
            <YAxis stroke="oklch(0.72 0.02 220)" fontSize={10} domain={[0, 100]} />
            <Tooltip
              contentStyle={{
                background: "oklch(0.16 0.03 235 / 0.9)",
                border: "1px solid oklch(0.4 0.04 230 / 0.5)",
                borderRadius: 12,
                color: "oklch(0.96 0.01 220)",
                fontSize: 12,
              }}
            />
            <Line type="monotone" dataKey="risk" stroke="oklch(0.82 0.18 75)" strokeWidth={2.5} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="text-[11px] text-muted-foreground">Ecological flow threshold: {ecoThreshold} m³/s</p>
    </motion.div>
  );
}