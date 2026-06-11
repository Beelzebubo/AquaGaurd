import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Topbar } from "@/components/dashboard/Topbar";
import { KpiStrip } from "@/components/dashboard/KpiStrip";
import { ParamControls, type Params } from "@/components/dashboard/ParamControls";
import { ChartsPanel } from "@/components/dashboard/ChartsPanel";
import { AlertsFeed } from "@/components/dashboard/AlertsFeed";
import { AiSummaryFab } from "@/components/dashboard/AiSummaryFab";
import { NepalRiversMap } from "@/components/map/NepalRiversMap";
import { HistoricalData } from "@/components/dashboard/HistoricalData";
import { GaugeChart } from "@/components/ui/GaugeChart";
import { stations } from "@/data/stations";
import { runEngine, type EngineResult } from "@/lib/aquaguard-engine";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "AquaGuard Nepal — Hydropower Compliance Monitor" },
      { name: "description", content: "AI-powered IFC PS4 compliance, disaster prediction and ESG monitoring for Nepal's hydropower plants, with live river-system map and Gemini voice summary." },
      { property: "og:title", content: "AquaGuard Nepal — Hydropower Compliance Monitor" },
      { property: "og:description", content: "AI-powered IFC PS4 compliance, disaster prediction and ESG monitoring for Nepal's hydropower plants." },
    ],
  }),
  component: Index,
});

function defaultParams(ecoThreshold: number): Params {
  return {
    temperature: 22,
    rainfall: 18,
    humidity: 72,
    riverFlow: Math.max(ecoThreshold * 1.4, 60),
    rollingFlow: Math.max(ecoThreshold * 1.3, 55),
  };
}

function generateSummary(
  stationName: string,
  river: string,
  riverFlow: number,
  ecoThreshold: number,
  rainfall: number,
  humidity: number,
  temperature: number,
  eng: EngineResult,
): string {
  const status = eng.compliance.compliant
    ? "currently meeting IFC PS4 ecological-flow requirements"
    : `falling below IFC PS4 ecological flow by ${eng.compliance.deficit.toFixed(1)} m³/s`;
  const risk = eng.predictedRisk.level;
  return [
    `${stationName} on the ${river} river is ${status}.`,
    `River flow is ${riverFlow.toFixed(1)} m³/s against an ecological threshold of ${ecoThreshold} m³/s.`,
    `Forecasted disaster risk is ${risk} (${Math.round(eng.predictedRisk.score * 100)}%) with rainfall ${rainfall} mm and humidity ${humidity}%.`,
    eng.anomalyDetected
      ? "Anomaly detected in flow patterns — recommend immediate field verification."
      : "No anomalies detected; operational status nominal.",
    `Composite ESG score: ${eng.esgScore}/100.`,
  ].join(" ");
}

function Index() {
  const [selectedId, setSelectedId] = useState(stations[0].id);
  const station = useMemo(() => stations.find((s) => s.id === selectedId) ?? stations[0], [selectedId]);
  const [params, setParams] = useState<Params>(() => defaultParams(station.ecoThreshold));
  const [result, setResult] = useState<EngineResult | null>(() =>
    runEngine({ ...defaultParams(station.ecoThreshold), ecoThreshold: station.ecoThreshold }),
  );
  const [summary, setSummary] = useState<string>("");
  const [generatedAt, setGeneratedAt] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Recompute local engine instantly when params/ecoThreshold change.
  useEffect(() => {
    setResult(runEngine({ ...params, ecoThreshold: station.ecoThreshold }));
  }, [params, station.ecoThreshold]);

  const handleRun = useCallback(() => {
    const eng = runEngine({ ...params, ecoThreshold: station.ecoThreshold });
    setResult(eng);
    const g = generateSummary(station.name, station.river, params.riverFlow, station.ecoThreshold, params.rainfall, params.humidity, params.temperature, eng);
    setSummary(g);
    setGeneratedAt(new Date().toISOString());
  }, [params, station]);

  // Re-run analysis when station changes (resets params + regenerates summary).
  useEffect(() => {
    setParams(defaultParams(station.ecoThreshold));
    const eng = runEngine({ ...defaultParams(station.ecoThreshold), ecoThreshold: station.ecoThreshold });
    setResult(eng);
    const g = generateSummary(station.name, station.river, defaultParams(station.ecoThreshold).riverFlow, station.ecoThreshold, defaultParams(station.ecoThreshold).rainfall, defaultParams(station.ecoThreshold).humidity, defaultParams(station.ecoThreshold).temperature, eng);
    setSummary(g);
    setGeneratedAt(new Date().toISOString());
  }, [station.id]);

  return (
    <div className="min-h-screen grid-bg pb-8">
      <Topbar selectedId={selectedId} onSelect={setSelectedId} />
      <main className="mt-4 flex flex-col gap-3">
        <KpiStrip result={result} station={station} />
        <div className="grid grid-cols-2 gap-3 px-3 md:grid-cols-4">
          <div className="glass rounded-2xl p-3">
            <GaugeChart
              value={result ? Math.round(result.predictedRisk.score * 100) : 0}
              max={100}
              label="Flood Risk"
              color={!result ? "oklch(0.72 0.02 220)" : result.predictedRisk.score >= 0.7 ? "oklch(0.68 0.24 25)" : result.predictedRisk.score >= 0.4 ? "oklch(0.82 0.18 75)" : "oklch(0.78 0.18 155)"}
              size={100}
              strokeWidth={8}
            />
          </div>
          <div className="glass rounded-2xl p-3">
            <GaugeChart
              value={result ? Math.round(result.compliance.ratio * 100) : 0}
              max={100}
              label="IFC PS4 Compliance"
              color={result?.compliance.compliant ? "oklch(0.78 0.18 155)" : "oklch(0.68 0.24 25)"}
              size={100}
              strokeWidth={8}
            />
          </div>
          <div className="glass rounded-2xl p-3">
            <GaugeChart
              value={result?.esgScore ?? 0}
              max={100}
              label="ESG Score"
              color={(result?.esgScore ?? 0) >= 70 ? "oklch(0.82 0.16 200)" : (result?.esgScore ?? 0) >= 50 ? "oklch(0.82 0.18 75)" : "oklch(0.68 0.24 25)"}
              size={100}
              strokeWidth={8}
            />
          </div>
          <div className="glass flex flex-col items-center justify-center gap-1 rounded-2xl p-3">
            <span className="text-[28px] font-bold tabular-nums text-foreground" style={{ fontFamily: "'Space Grotesk', system-ui, sans-serif" }}>
              {station.ecoThreshold}
            </span>
            <span className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Eco Threshold (m³/s)</span>
            <span className={`mt-1 text-[10px] font-semibold uppercase tracking-wider ${(result?.compliance.compliant ?? true) ? "text-[oklch(0.78_0.18_155)]" : "text-[oklch(0.68_0.24_25)]"}`}>
              {(result?.compliance.compliant ?? true) ? "Compliant" : "Non-compliant"}
            </span>
          </div>
        </div>
        <div className="grid grid-cols-1 gap-3 px-3 lg:grid-cols-[1.4fr_1fr]">
          <div className="glass h-[460px] overflow-hidden rounded-2xl p-2">
            <NepalRiversMap
              selectedId={selectedId}
              onSelect={(s) => setSelectedId(s.id)}
            />
          </div>
          <ChartsPanel result={result} ecoThreshold={station.ecoThreshold} stationName={station.name} />
        </div>
        <div className="grid grid-cols-1 gap-3 px-3 lg:grid-cols-[1.4fr_1fr]">
          <ParamControls station={station} params={params} onChange={setParams} onRun={handleRun} busy={busy} />
          <AlertsFeed alerts={result?.alerts ?? []} />
        </div>
        <div className="px-3">
          <HistoricalData stationId={selectedId} />
        </div>
      </main>
      <AiSummaryFab summary={summary} busy={busy} generatedAt={generatedAt} />
    </div>
  );
}
