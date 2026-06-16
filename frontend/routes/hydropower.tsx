import { createFileRoute } from "@tanstack/react-router";
import { motion } from "motion/react";
import { useMemo, useState } from "react";
import { stations } from "@/data/stations";
import {
  SEASONS,
  STATION_HEADS,
  estimateHydropower,
  getStationFlow,
  fetchLiveWeatherForStation,
  getSeasonalRainfallBaseline,
  type Season,
} from "@/data/hydropower";
import { Footer } from "@/components/layout/Footer";

export const Route = createFileRoute("/hydropower")({
  head: () => ({
    meta: [
      { title: "Hydropower Potential — AquaGuard" },
      {
        name: "description",
        content:
          "Seasonal hydropower potential estimation for all Nepal monitoring stations, based on historical river discharge data and NASA POWER live weather.",
      },
    ],
  }),
  component: HydropowerPage,
});

const FLOW_SOURCE_BADGE: Record<string, { label: string; className: string }> =
  {
    historical: {
      label: "Historical avg",
      className:
        "bg-[oklch(0.78_0.18_155/0.2)] text-[oklch(0.78_0.18_155)]",
    },
    estimated: {
      label: "Estimated",
      className: "bg-[oklch(0.82_0.18_75/0.2)] text-[oklch(0.82_0.18_75)]",
    },
  };

const CLASSIFICATION_COLORS: Record<
  string,
  { border: string; text: string; bg: string }
> = {
  Large: {
    border: "border-[oklch(0.82_0.16_200/0.4)]",
    text: "text-[oklch(0.82_0.16_200)]",
    bg: "bg-[oklch(0.82_0.16_200/0.15)]",
  },
  Medium: {
    border: "border-[oklch(0.78_0.18_155/0.4)]",
    text: "text-[oklch(0.78_0.18_155)]",
    bg: "bg-[oklch(0.78_0.18_155/0.15)]",
  },
  Small: {
    border: "border-[oklch(0.82_0.18_75/0.4)]",
    text: "text-[oklch(0.82_0.18_75)]",
    bg: "bg-[oklch(0.82_0.18_75/0.15)]",
  },
};

function getClassificationColor(
  classification: string | null,
): (typeof CLASSIFICATION_COLORS)[keyof typeof CLASSIFICATION_COLORS] {
  if (!classification) {
    return {
      border: "border-muted",
      text: "text-muted-foreground",
      bg: "bg-muted/40",
    };
  }
  const exact = CLASSIFICATION_COLORS[classification];
  if (exact) return exact;
  return {
    border: "border-[oklch(0.7_0.08_210/0.4)]",
    text: "text-muted-foreground",
    bg: "bg-muted/40",
  };
}

function HydropowerPage() {
  const [season, setSeason] = useState<Season>("monsoon");
  const [liveData, setLiveData] = useState<
    Record<string, { rainfall: number; temperature: number; humidity: number }>
  >({});
  const [weatherLoading, setWeatherLoading] = useState(false);

  const stationData = useMemo(
    () =>
      stations.map((s) => {
        const head = STATION_HEADS[s.id] ?? null;
        const { flow, source } = getStationFlow(s.id, s.ecoThreshold, season);
        const hydro = estimateHydropower(flow, head);
        const utilPct =
          hydro.powerMw !== null && s.capacityMw > 0
            ? (hydro.powerMw / s.capacityMw) * 100
            : null;
        const live = liveData[s.id] ?? null;
        const baselineRainfall = source === "historical"
          ? getSeasonalRainfallBaseline(s.id, season)
          : null;
        const rainDiff =
          live && baselineRainfall !== null
            ? ((live.rainfall - baselineRainfall) / baselineRainfall) * 100
            : null;
        return { station: s, head, flow, source, hydro, utilPct, live, rainDiff, baselineRainfall };
      }),
    [season, liveData],
  );

  const totals = useMemo(() => {
    const totalEstimated = stationData.reduce(
      (sum, d) => sum + (d.hydro.powerMw ?? 0),
      0,
    );
    const totalCapacity = stations.reduce(
      (sum, s) => sum + s.capacityMw,
      0,
    );
    return { totalEstimated, totalCapacity };
  }, [stationData]);

  const handleLiveWeather = async () => {
    setWeatherLoading(true);
    const results: Record<
      string,
      { rainfall: number; temperature: number; humidity: number }
    > = {};
    await Promise.allSettled(
      stations.map(async (s) => {
        try {
          const w = await fetchLiveWeatherForStation(s.lat, s.lng);
          results[s.id] = w;
        } catch {
          // skip failures
        }
      }),
    );
    setLiveData((prev) => ({ ...prev, ...results }));
    setWeatherLoading(false);
  };

  return (
    <div className="min-h-screen grid-bg pb-8">
      <main className="mx-auto max-w-7xl px-4 pt-6">
        <motion.div
          initial={{ y: -16, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="glass rounded-2xl p-6"
        >
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground text-glow">
                Hydropower Potential
              </h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Estimated electrical output across all monitored stations ·{" "}
                {season.charAt(0).toUpperCase() + season.slice(1)} season
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex rounded-xl border border-[oklch(0.4_0.04_230/0.4)] bg-background/60 p-1">
                {SEASONS.map((s) => (
                  <button
                    key={s.key}
                    onClick={() => setSeason(s.key)}
                    className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                      season === s.key
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
              <button
                onClick={handleLiveWeather}
                disabled={weatherLoading}
                className="relative overflow-hidden rounded-xl border border-[oklch(0.4_0.04_230/0.4)] bg-background/60 px-3 py-2 text-xs font-semibold text-foreground transition-all hover:bg-background/80 active:scale-[0.97] disabled:opacity-50"
              >
                {weatherLoading ? (
                  <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                ) : (
                  "Live Weather"
                )}
              </button>
            </div>
          </div>

          {Object.keys(liveData).length > 0 && (
            <p className="mt-3 text-[11px] text-muted-foreground">
              Live NASA POWER weather fetched for{" "}
              {Object.keys(liveData).length} stations
              {liveData[stations[0]?.id ?? ""] && (
                <span>
                  {" · "}e.g. {stations[0].name}:{" "}
                  {liveData[stations[0].id].rainfall.toFixed(1)}mm rain ·{" "}
                  {liveData[stations[0].id].temperature.toFixed(1)}°C ·{" "}
                  {liveData[stations[0].id].humidity.toFixed(0)}% RH
                </span>
              )}
            </p>
          )}
        </motion.div>

        <motion.div
          initial={{ y: 16, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3"
        >
          {stationData.map((d, i) => {
            const badge = FLOW_SOURCE_BADGE[d.source];
            const cc = getClassificationColor(d.hydro.classification);
            return (
              <motion.div
                key={d.station.id}
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.4, delay: 0.05 * i }}
                className="glass rounded-2xl p-5 transition-transform hover:scale-[1.02]"
              >
                <div className="mb-3 flex items-start justify-between">
                  <div>
                    <h3 className="text-base font-semibold text-foreground">
                      {d.station.name}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      {d.station.river} river
                    </p>
                  </div>
                  <span className={`rounded-full px-2.5 py-0.5 text-[10px] font-semibold ${cc.bg} ${cc.text}`}>
                    {d.hydro.classification ?? "N/A"}
                  </span>
                </div>

                <div className="mb-3 grid grid-cols-2 gap-2 rounded-xl bg-background/40 p-3">
                  <div>
                    <p className="font-mono text-[10px] text-muted-foreground">
                      Head height
                    </p>
                    <p className="font-mono text-sm tabular-nums text-foreground">
                      {d.head !== null ? `${d.head} m` : "—"}
                    </p>
                  </div>
                  <div>
                    <p className="font-mono text-[10px] text-muted-foreground">
                      Installed
                    </p>
                    <p className="font-mono text-sm tabular-nums text-foreground">
                      {d.station.capacityMw}{" "}
                      <span className="text-[10px] text-muted-foreground">
                        MW
                      </span>
                    </p>
                  </div>
                </div>

                <div className="mb-2">
                  <div className="flex items-center justify-between">
                    <p className="font-mono text-[10px] text-muted-foreground">
                      River flow ({season})
                    </p>
                    <span
                      className={`rounded px-1.5 py-0.5 text-[9px] font-medium ${badge.className}`}
                    >
                      {badge.label}
                    </span>
                  </div>
                  <p className="font-mono text-lg tabular-nums text-foreground">
                    {d.flow.toFixed(d.flow < 1 ? 3 : d.flow < 100 ? 1 : 0)}
                    <span className="ml-1 text-xs text-muted-foreground">
                      m³/s
                    </span>
                  </p>
                </div>

                <div className="mb-2">
                  <p className="font-mono text-[10px] text-muted-foreground">
                    Estimated power
                  </p>
                  <p className="font-mono text-2xl tabular-nums text-primary text-glow">
                    {d.hydro.powerMw !== null
                      ? d.hydro.powerMw >= 1
                        ? `${d.hydro.powerMw.toFixed(d.hydro.powerMw >= 100 ? 0 : 1)}`
                        : `${(d.hydro.powerMw * 1000).toFixed(0)}`
                      : "—"}
                    <span className="ml-1 text-sm text-muted-foreground">
                      {d.hydro.powerMw !== null
                        ? d.hydro.powerMw >= 1
                          ? "MW"
                          : "kW"
                        : ""}
                    </span>
                  </p>
                </div>

                {d.utilPct !== null && (
                  <div>
                    <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                      <span>Capacity utilization</span>
                      <span className="font-mono">
                        {d.utilPct.toFixed(1)}%
                      </span>
                    </div>
                    <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-background/60">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          d.utilPct > 100
                            ? "bg-[oklch(0.82_0.16_200)]"
                            : d.utilPct > 50
                              ? "bg-[oklch(0.78_0.18_155)]"
                              : "bg-[oklch(0.82_0.18_75)]"
                        }`}
                        style={{ width: `${Math.min(d.utilPct, 200)}%` }}
                      />
                    </div>
                  </div>
                )}

                {d.live && d.baselineRainfall !== null && (
                  <div className="mt-2 rounded-lg bg-background/30 px-2 py-1.5">
                    <p className="font-mono text-[10px] text-muted-foreground">
                      Live rainfall: {d.live.rainfall.toFixed(1)}mm
                      {d.rainDiff !== null && (
                        <span
                          className={
                            d.rainDiff > 0
                              ? "ml-1 text-[oklch(0.82_0.16_200)]"
                              : "ml-1 text-[oklch(0.82_0.18_75)]"
                          }
                        >
                          ({d.rainDiff > 0 ? "+" : ""}
                          {d.rainDiff.toFixed(0)}% vs seasonal avg)
                        </span>
                      )}
                    </p>
                  </div>
                )}
              </motion.div>
            );
          })}
        </motion.div>

        <motion.div
          initial={{ y: 16, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-4"
        >
          <div className="glass rounded-2xl p-5">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div className="text-center">
                <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  Total estimated power
                </p>
                <p className="mt-1 font-mono text-3xl tabular-nums text-primary text-glow">
                  {totals.totalEstimated >= 1000
                    ? `${(totals.totalEstimated / 1000).toFixed(1)}`
                    : totals.totalEstimated.toFixed(0)}
                  <span className="ml-1 text-base text-muted-foreground">
                    {totals.totalEstimated >= 1000 ? "GW" : "MW"}
                  </span>
                </p>
              </div>
              <div className="text-center">
                <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  Total installed capacity
                </p>
                <p className="mt-1 font-mono text-3xl tabular-nums text-foreground">
                  {totals.totalCapacity >= 1000
                    ? `${(totals.totalCapacity / 1000).toFixed(1)}`
                    : totals.totalCapacity}
                  <span className="ml-1 text-base text-muted-foreground">
                    GW
                  </span>
                </p>
              </div>
              <div className="text-center">
                <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  Utilization
                </p>
                <p className="mt-1 font-mono text-3xl tabular-nums text-foreground">
                  {totals.totalCapacity > 0
                    ? `${((totals.totalEstimated / totals.totalCapacity) * 100).toFixed(1)}`
                    : "—"}
                  <span className="ml-1 text-base text-muted-foreground">%</span>
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </main>
      <Footer />
    </div>
  );
}
