import { motion } from "motion/react";
import { useEffect, useMemo, useState } from "react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useServerFn } from "@tanstack/react-start";
import { getHistoricalData, type DischargeRecord } from "@/lib/historical-data.functions";
import { stations } from "@/data/stations";

function rollingMean(data: number[], window: number): (number | null)[] {
  return data.map((_, i) => {
    const start = Math.max(0, i - window + 1);
    const slice = data.slice(start, i + 1);
    return slice.length > 0 ? slice.reduce((a, b) => a + b, 0) / slice.length : null;
  });
}

function monthName(m: number): string {
  return ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][m - 1] ?? "";
}

export function HistoricalData({ stationId }: { stationId: string }) {
  const fetch = useServerFn(getHistoricalData);
  const station = useMemo(() => stations.find((s) => s.id === stationId) ?? stations[0], [stationId]);

  const [allRecords, setAllRecords] = useState<DischargeRecord[]>([]);
  const [minYear, setMinYear] = useState(1979);
  const [maxYear, setMaxYear] = useState(2025);
  const [error, setError] = useState<string | null>(null);
  const [yearRange, setYearRange] = useState<[number, number]>([2015, 2025]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch({ data: { stationId } })
      .then((res) => {
        const r = res as { records: DischargeRecord[]; minYear: number; maxYear: number };
        setAllRecords(r.records);
        setMinYear(r.minYear);
        setMaxYear(r.maxYear);
        setYearRange([Math.max(r.minYear, 2015), r.maxYear]);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load data"))
      .finally(() => setLoading(false));
  }, [fetch, stationId]);

  const filtered = useMemo(() => {
    return allRecords.filter((r) => {
      const y = new Date(r.datetime).getFullYear();
      return !isNaN(y) && y >= yearRange[0] && y <= yearRange[1];
    });
  }, [allRecords, yearRange]);

  const chartData = useMemo(() => {
    if (filtered.length < 2) return [];
    const values = filtered.map((r) => r.discharge);
    const rolling = rollingMean(values, 30);
    const sampled: { date: string; flow: number; rolling: number | null }[] = [];
    const step = Math.max(1, Math.floor(filtered.length / 500));
    for (let i = 0; i < filtered.length; i += step) {
      sampled.push({
        date: filtered[i].datetime,
        flow: filtered[i].discharge,
        rolling: rolling[i],
      });
    }
    return sampled;
  }, [filtered]);

  const monthlyData = useMemo(() => {
    const groups: Record<number, number[]> = {};
    for (const r of filtered) {
      const d = new Date(r.datetime);
      const m = d.getMonth() + 1;
      if (!isNaN(m)) {
        if (!groups[m]) groups[m] = [];
        groups[m].push(r.discharge);
      }
    }
    return Array.from({ length: 12 }, (_, i) => {
      const m = i + 1;
      const vals = groups[m] ?? [];
      if (vals.length === 0) return { month: monthName(m), mean: 0, min: 0, max: 0, count: 0 };
      const sorted = [...vals].sort((a, b) => a - b);
      return {
        month: monthName(m),
        mean: Math.round(vals.reduce((a, b) => a + b, 0) / vals.length),
        min: Math.round(sorted[0]),
        max: Math.round(sorted[sorted.length - 1]),
        count: vals.length,
      };
    });
  }, [filtered]);

  const stats = useMemo(() => {
    if (filtered.length === 0) return null;
    const vals = filtered.map((r) => r.discharge);
    const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
    const sorted = [...vals].sort((a, b) => a - b);
    const std = Math.sqrt(vals.reduce((s, v) => s + (v - mean) ** 2, 0) / vals.length);
    const peakMonth = monthlyData.reduce((max, m) => (m.mean > max.mean ? m : max), monthlyData[0]);
    const lowMonth = monthlyData.reduce((min, m) => (m.mean < min.mean ? m : min), monthlyData[0]);
    const trend =
      vals.length > 60
        ? vals.slice(-30).reduce((a, b) => a + b, 0) / 30 > vals.slice(0, 30).reduce((a, b) => a + b, 0) / 30
          ? "increasing"
          : "decreasing"
        : "stable";
    return { mean, std, min: sorted[0], max: sorted[sorted.length - 1], peakMonth, lowMonth, trend };
  }, [filtered, monthlyData]);

  if (loading) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass rounded-2xl p-4">
        <p className="text-sm text-muted-foreground">Loading historical data...</p>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass rounded-2xl p-4">
        <p className="text-sm text-muted-foreground">Historical data unavailable: {error}</p>
      </motion.div>
    );
  }

  if (filtered.length === 0) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass rounded-2xl p-4">
        <p className="text-sm text-muted-foreground">No historical data for the selected range.</p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ y: 24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="glass rounded-2xl p-4"
    >
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">Historical data</p>
          <h3 className="text-base font-semibold text-foreground">{station.name} · {station.river} Discharge</h3>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-[11px] text-muted-foreground">
            <span>
              {yearRange[0]}–{yearRange[1]}
            </span>
            <input
              type="range"
              min={minYear}
              max={maxYear}
              value={yearRange[0]}
              onChange={(e) => setYearRange([Math.min(Number(e.target.value), yearRange[1]), yearRange[1]])}
              className="w-24 accent-[var(--hydro-cyan)]"
              aria-label="Start year"
            />
            <input
              type="range"
              min={minYear}
              max={maxYear}
              value={yearRange[1]}
              onChange={(e) => setYearRange([yearRange[0], Math.max(Number(e.target.value), yearRange[0])])}
              className="w-24 accent-[var(--hydro-cyan)]"
              aria-label="End year"
            />
          </label>
        </div>
      </div>

      <div className="h-52 w-full">
        <ResponsiveContainer>
          <AreaChart data={chartData} margin={{ top: 6, right: 8, left: -16, bottom: 0 }}>
            <defs>
              <linearGradient id="histFlow" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="oklch(0.82 0.16 200)" stopOpacity={0.3} />
                <stop offset="100%" stopColor="oklch(0.82 0.16 200)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="oklch(0.4 0.04 230 / 0.25)" strokeDasharray="3 3" />
            <XAxis dataKey="date" stroke="oklch(0.72 0.02 220)" fontSize={10} tickFormatter={(v) => v?.slice(0, 7) ?? ""} interval="preserveStartEnd" />
            <YAxis stroke="oklch(0.72 0.02 220)" fontSize={10} />
            <Tooltip
              cursor={false}
              contentStyle={{
                background: "oklch(0.16 0.03 235 / 0.9)",
                border: "1px solid oklch(0.4 0.04 230 / 0.5)",
                borderRadius: 12,
                color: "oklch(0.96 0.01 220)",
                fontSize: 12,
              }}
              labelFormatter={(v) => `Date: ${v}`}
              formatter={(val) => [`${Number(val).toFixed(1)} m³/s`]}
            />
            <Area type="monotone" dataKey="flow" stroke="oklch(0.82 0.16 200)" strokeWidth={1.5} fill="url(#histFlow)" dot={false} />
            <Area type="monotone" dataKey="rolling" stroke="oklch(0.78 0.18 155)" strokeWidth={2} strokeDasharray="4 3" fill="none" dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3">
        <p className="mb-2 text-[11px] uppercase tracking-[0.2em] text-muted-foreground">Monthly average discharge</p>
        <div className="h-36 w-full">
          <ResponsiveContainer>
            <BarChart data={monthlyData} margin={{ top: 6, right: 8, left: -16, bottom: 0 }}>
              <CartesianGrid stroke="oklch(0.4 0.04 230 / 0.25)" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="month" stroke="oklch(0.72 0.02 220)" fontSize={10} />
              <YAxis stroke="oklch(0.72 0.02 220)" fontSize={10} />
              <Tooltip
                cursor={{ fill: "oklch(0.3 0.04 230 / 0.3)" }}
                contentStyle={{
                  background: "oklch(0.16 0.03 235 / 0.9)",
                  border: "1px solid oklch(0.4 0.04 230 / 0.5)",
                  borderRadius: 12,
                  color: "oklch(0.96 0.01 220)",
                  fontSize: 12,
                }}
                formatter={(val, name) => [`${Number(val).toFixed(0)} m³/s`, name === "mean" ? "Mean" : name === "min" ? "Min" : "Max"]}
              />
              <Bar dataKey="mean" fill="oklch(0.82 0.16 200 / 0.7)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {stats && (
        <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] md:grid-cols-4">
          <div className="rounded-xl bg-background/40 p-2.5">
            <span className="text-muted-foreground">Mean flow</span>
            <p className="font-semibold text-foreground">{stats.mean.toFixed(0)} m³/s</p>
          </div>
          <div className="rounded-xl bg-background/40 p-2.5">
            <span className="text-muted-foreground">Range</span>
            <p className="font-semibold text-foreground">
              {stats.min.toFixed(0)}–{stats.max.toFixed(0)} m³/s
            </p>
          </div>
          <div className="rounded-xl bg-background/40 p-2.5">
            <span className="text-muted-foreground">Peak month</span>
            <p className="font-semibold text-foreground">
              {stats.peakMonth.month} ({stats.peakMonth.mean} m³/s)
            </p>
          </div>
          <div className="rounded-xl bg-background/40 p-2.5">
            <span className="text-muted-foreground">Trend</span>
            <p className="font-semibold capitalize text-foreground">{stats.trend}</p>
          </div>
        </div>
      )}
    </motion.div>
  );
}
