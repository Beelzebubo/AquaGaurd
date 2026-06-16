import { createFileRoute, Link } from "@tanstack/react-router";
import { stations } from "@/data/stations";
import { Footer } from "@/components/layout/Footer";

export const Route = createFileRoute("/stations")({
  head: () => ({
    meta: [
      { title: "Stations — AquaGuard" },
      {
        name: "description",
        content: "Overview of all monitored hydropower stations in Nepal.",
      },
    ],
  }),
  component: StationsPage,
});

function StationsPage() {
  return (
    <div className="mx-auto min-h-screen max-w-5xl px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[var(--text)]">
          Monitoring Stations
        </h1>
        <p className="mt-1 text-sm text-[var(--text-dim)]">
          {stations.length} hydropower stations across Nepal
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {stations.map((s) => (
          <Link
            key={s.id}
            to="/"
            className="panel block p-4 transition-colors hover:border-[var(--accent-dim)]"
          >
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-[var(--text)]">
                {s.name}
              </h3>
              <span className="rounded bg-[var(--accent-muted)] px-2 py-0.5 font-mono text-[10px] text-[var(--accent)]">
                {s.capacityMw} MW
              </span>
            </div>
            <p className="text-xs text-[var(--text-dim)]">{s.river} river</p>
            <div className="mt-3 grid grid-cols-2 gap-2 border-t border-[var(--border)] pt-3">
              <div>
                <p className="font-mono text-[10px] text-[var(--text-muted)]">
                  Eco Threshold
                </p>
                <p className="font-mono text-sm tabular-nums text-[var(--text)]">
                  {s.ecoThreshold}
                  <span className="text-xs text-[var(--text-dim)]"> m³/s</span>
                </p>
              </div>
              <div>
                <p className="font-mono text-[10px] text-[var(--text-muted)]">
                  Coordinates
                </p>
                <p className="font-mono text-xs tabular-nums text-[var(--text)]">
                  {s.lat.toFixed(2)}, {s.lng.toFixed(2)}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>
      <Footer />
    </div>
  );
}
