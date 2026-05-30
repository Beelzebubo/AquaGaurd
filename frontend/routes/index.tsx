import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { Topbar } from "@/components/dashboard/Topbar";
import { KpiStrip } from "@/components/dashboard/KpiStrip";
import { ParamControls, type Params } from "@/components/dashboard/ParamControls";
import { ChartsPanel } from "@/components/dashboard/ChartsPanel";
import { AlertsFeed } from "@/components/dashboard/AlertsFeed";
import { AiSummaryFab } from "@/components/dashboard/AiSummaryFab";
import { NepalRiversMap } from "@/components/map/NepalRiversMap";
import { stations } from "@/data/stations";
import { runAquaGuardAnalysis } from "@/lib/aquaguard.functions";
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

  const run = useServerFn(runAquaGuardAnalysis);

  // Recompute local engine instantly when params/station change for snappy UI.
  useEffect(() => {
    setResult(runEngine({ ...params, ecoThreshold: station.ecoThreshold }));
  }, [params, station.ecoThreshold]);

  // Reset params when switching station.
  useEffect(() => {
    setParams(defaultParams(station.ecoThreshold));
  }, [station.id, station.ecoThreshold]);

  const handleRun = async () => {
    setBusy(true);
    try {
      const res = await run({
        data: {
          stationId: station.id,
          stationName: station.name,
          river: station.river,
          temperature: params.temperature,
          rainfall: params.rainfall,
          humidity: params.humidity,
          riverFlow: params.riverFlow,
          rollingFlow: params.rollingFlow,
          ecoThreshold: station.ecoThreshold,
        },
      });
      setResult(res.engine);
      setSummary(res.summary);
      setGeneratedAt(res.generatedAt);
    } catch (e) {
      console.error(e);
    } finally {
      setBusy(false);
    }
  };

  // Auto-run once on mount so the summary panel has content.
  useEffect(() => {
    handleRun();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen grid-bg pb-8">
      <Topbar selectedId={selectedId} onSelect={setSelectedId} />
      <main className="mt-4 flex flex-col gap-3">
        <KpiStrip result={result} />
        <div className="grid grid-cols-1 gap-3 px-3 lg:grid-cols-[1.4fr_1fr]">
          <div className="glass h-[460px] overflow-hidden rounded-2xl p-2">
            <NepalRiversMap
              selectedId={selectedId}
              onSelect={(s) => setSelectedId(s.id)}
            />
          </div>
          <ChartsPanel result={result} ecoThreshold={station.ecoThreshold} />
        </div>
        <div className="grid grid-cols-1 gap-3 px-3 lg:grid-cols-[1.4fr_1fr]">
          <ParamControls station={station} params={params} onChange={setParams} onRun={handleRun} busy={busy} />
          <AlertsFeed alerts={result?.alerts ?? []} />
        </div>
      </main>
      <AiSummaryFab summary={summary} busy={busy} generatedAt={generatedAt} />
    </div>
  );
}
