import { useEffect, useState } from "react";
import { stations } from "@/data/stations";
import { fetchLiveWeather, type LiveWeather } from "@/lib/weather";

export function WeatherWidget({
  selectedId,
  onFetch,
}: {
  selectedId: string;
  onFetch?: (w: LiveWeather) => void;
}) {
  const station = stations.find((s) => s.id === selectedId) ?? stations[0];
  const [weather, setWeather] = useState<LiveWeather | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const w = await fetchLiveWeather(station.lat, station.lng);
      setWeather(w);
      onFetch?.(w);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch weather");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId]);

  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-3">
      <div className="mb-2 flex items-center justify-between">
        <p className="section-label">Live Weather (NASA POWER)</p>
        {loading && (
          <span className="shimmer inline-block h-2 w-2 rounded-full" />
        )}
      </div>

      {error ? (
        <p className="text-xs text-[var(--danger)]">{error}</p>
      ) : weather ? (
        <div className="grid grid-cols-3 gap-2">
          <div>
            <p className="font-mono text-xs text-[var(--text-dim)]">Temp</p>
            <p className="font-mono text-sm font-semibold tabular-nums text-[var(--text)]">
              {weather.temperature.toFixed(1)}°C
            </p>
          </div>
          <div>
            <p className="font-mono text-xs text-[var(--text-dim)]">Rain</p>
            <p className="font-mono text-sm font-semibold tabular-nums text-[var(--text)]">
              {weather.rainfall.toFixed(1)} mm
            </p>
          </div>
          <div>
            <p className="font-mono text-xs text-[var(--text-dim)]">Humidity</p>
            <p className="font-mono text-sm font-semibold tabular-nums text-[var(--text)]">
              {weather.humidity.toFixed(0)}%
            </p>
          </div>
        </div>
      ) : (
        <p className="text-xs text-[var(--text-muted)]">
          Click refresh to load
        </p>
      )}

      <button
        onClick={load}
        disabled={loading}
        className="mt-2 w-full rounded-md border border-[var(--border)] bg-[var(--bg-muted)] px-2 py-1 text-[11px] font-medium text-[var(--text-dim)] transition-colors hover:border-[var(--accent-dim)] hover:text-[var(--accent)] disabled:opacity-50"
      >
        {loading ? "Loading..." : "Refresh Weather"}
      </button>
    </div>
  );
}
