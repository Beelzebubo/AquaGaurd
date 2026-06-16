import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { stations } from "@/data/stations";
import { useServerFn } from "@tanstack/react-start";
import { runAquaGuardAnalysis } from "@/lib/aquaguard.functions";
import { runEngine } from "@/lib/aquaguard-engine";
import { Footer } from "@/components/layout/Footer";

export const Route = createFileRoute("/compliance")({
  head: () => ({
    meta: [
      { title: "Compliance Report — AquaGuard" },
      {
        name: "description",
        content: "IFC PS4 compliance report for Nepal hydropower stations.",
      },
    ],
  }),
  component: CompliancePage,
});

function CompliancePage() {
  const [selectedId, setSelectedId] = useState(stations[0].id);
  const station = stations.find((s) => s.id === selectedId) ?? stations[0];
  const run = useServerFn(runAquaGuardAnalysis);
  const [reports, setReports] = useState<
    Record<string, { status: string; score: number }>
  >({});

  const runAll = async () => {
    for (const s of stations) {
      const params = {
        temperature: 22,
        rainfall: 18,
        humidity: 72,
        riverFlow: Math.max(s.ecoThreshold * 1.4, 60),
        rollingFlow: Math.max(s.ecoThreshold * 1.3, 55),
        ecoThreshold: s.ecoThreshold,
      };
      const eng = runEngine(params);
      setReports((prev) => ({
        ...prev,
        [s.id]: {
          status: eng.compliance.compliant ? "Compliant" : "Non-Compliant",
          score: Math.round(eng.compliance.ratio * 100),
        },
      }));
    }
  };

  return (
    <div className="mx-auto min-h-screen max-w-5xl px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[var(--text)]">
          IFC PS4 Compliance Report
        </h1>
        <p className="mt-1 text-sm text-[var(--text-dim)]">
          Ecological flow compliance across all monitored stations
        </p>
        <button onClick={runAll} className="btn-primary mt-4">
          Run All Stations
        </button>
      </div>

      <div className="space-y-3">
        {stations.map((s) => {
          const r = reports[s.id];
          return (
            <div
              key={s.id}
              className="panel flex items-center justify-between p-4"
            >
              <div>
                <h3 className="text-sm font-semibold text-[var(--text)]">
                  {s.name}
                </h3>
                <p className="text-xs text-[var(--text-muted)]">
                  {s.river} · {s.capacityMw} MW · Eco threshold:{" "}
                  {s.ecoThreshold} m³/s
                </p>
              </div>
              {r ? (
                <div className="text-right">
                  <span
                    className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${
                      r.status === "Compliant"
                        ? "bg-[var(--success-muted)] text-[var(--success)]"
                        : "bg-[var(--danger-muted)] text-[var(--danger)]"
                    }`}
                  >
                    {r.status}
                  </span>
                  <p className="mt-1 font-mono text-xs text-[var(--text-dim)]">
                    Score: {r.score}%
                  </p>
                </div>
              ) : (
                <span className="text-xs text-[var(--text-muted)]">
                  Not analyzed
                </span>
              )}
            </div>
          );
        })}
      </div>
      <Footer />
    </div>
  );
}
