export type Season = "winter" | "spring" | "monsoon" | "autumn";

export const SEASONS: { key: Season; label: string; months: string }[] = [
  { key: "winter", label: "Winter", months: "Dec–Feb" },
  { key: "spring", label: "Spring", months: "Mar–May" },
  { key: "monsoon", label: "Monsoon", months: "Jun–Sep" },
  { key: "autumn", label: "Autumn", months: "Oct–Nov" },
];

const DEFAULT_EFFICIENCY = 0.85;

export const STATION_HEADS: Record<string, number> = {
  "melamchi": 850,
  "upper-tamakoshi": 822,
  "kali-gandaki-a": 115,
  "marsyangdi": 78,
  "trishuli": 60,
  "kulekhani": 315,
  "chisapani": 100,
  "arun-iii": 260,
  "sapta-koshi": 40,
  "budhi-gandaki": 135,
};

type HistoricalSeasonal = {
  flow: number;
  rainfall: number;
  temperature: number;
};

export const HISTORICAL_STATIONS: Record<string, Record<Season, HistoricalSeasonal>> = {
  melamchi: {
    winter: { flow: 0.14, rainfall: 0.27, temperature: 2.2 },
    spring: { flow: 0.05, rainfall: 1.08, temperature: 9.7 },
    monsoon: { flow: 1.26, rainfall: 4.75, temperature: 14.4 },
    autumn: { flow: 0.52, rainfall: 0.62, temperature: 7.6 },
  },
  chisapani: {
    winter: { flow: 320.31, rainfall: 0.7, temperature: 16.5 },
    spring: { flow: 438.16, rainfall: 1.05, temperature: 28.4 },
    monsoon: { flow: 2835.36, rainfall: 7.13, temperature: 29.6 },
    autumn: { flow: 937.32, rainfall: 0.65, temperature: 22.4 },
  },
};

const SEASONAL_MULTIPLIERS: Record<Season, number> = {
  winter: 1.15,
  spring: 1.0,
  monsoon: 5.0,
  autumn: 2.0,
};

export function getStationFlow(
  stationId: string,
  ecoThreshold: number,
  season: Season,
): { flow: number; source: "historical" | "estimated" } {
  if (
    HISTORICAL_STATIONS[stationId] &&
    HISTORICAL_STATIONS[stationId][season]
  ) {
    return {
      flow: HISTORICAL_STATIONS[stationId][season].flow,
      source: "historical",
    };
  }
  return {
    flow: ecoThreshold * SEASONAL_MULTIPLIERS[season],
    source: "estimated",
  };
}

export function estimateHydropower(flow: number, head: number | null) {
  if (head === null || head <= 0) {
    return { powerKw: null, powerMw: null, note: "Head height required", classification: null as string | null };
  }
  const powerW = DEFAULT_EFFICIENCY * 1000 * 9.81 * flow * head;
  const powerMw = powerW / 1_000_000;
  const classification =
    powerMw >= 100 ? "Large" : powerMw >= 10 ? "Medium" : powerMw >= 1 ? "Small" : "Mini / Pico";
  const unit = powerMw >= 1 ? "MW" : "kW";
  const value = powerMw >= 1 ? powerMw : powerMw * 1000;
  const note = `${classification} hydropower potential (${value.toFixed(1)} ${unit})`;
  return { powerMw: Math.round(powerMw * 100) / 100, powerKw: Math.round(powerMw * 1000 * 100) / 100, note, classification };
}

const NASA_POWER_URL =
  import.meta.env.VITE_NASA_POWER_URL ??
  "https://power.larc.nasa.gov/api/temporal/daily/point";
const CACHE_TTL = 5 * 60 * 1000;

type LiveCache = { data: { rainfall: number; temperature: number; humidity: number }; at: number };
const liveCache = new Map<string, LiveCache>();

export async function fetchLiveWeatherForStation(
  lat: number,
  lng: number,
): Promise<{ rainfall: number; temperature: number; humidity: number }> {
  const key = `${lat.toFixed(2)}-${lng.toFixed(2)}`;
  const cached = liveCache.get(key);
  if (cached && Date.now() - cached.at < CACHE_TTL) return cached.data;

  const today = new Date();
  const end = new Date(today);
  end.setDate(end.getDate() - 1);
  const start = new Date(end);
  start.setDate(start.getDate() - 6);
  const fmt = (d: Date) =>
    d.getFullYear().toString() +
    String(d.getMonth() + 1).padStart(2, "0") +
    String(d.getDate()).padStart(2, "0");

  const params = new URLSearchParams({
    parameters: "PRECTOTCORR,T2M,RH2M",
    community: "RE",
    format: "JSON",
    latitude: lat.toString(),
    longitude: lng.toString(),
    start: fmt(start),
    end: fmt(end),
  });

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);
  const res = await fetch(`${NASA_POWER_URL}?${params}`, { signal: controller.signal });
  clearTimeout(timeoutId);
  if (!res.ok) throw new Error(`NASA POWER error: ${res.status}`);

  const data = await res.json();
  const props = data?.properties?.parameter ?? {};
  const precip: Record<string, number> = props.PRECTOTCORR ?? {};
  const temp: Record<string, number> = props.T2M ?? {};
  const humid: Record<string, number> = props.RH2M ?? {};

  const days = Object.keys(precip).sort();
  let validDay: string | null = null;
  for (let i = days.length - 1; i >= 0; i--) {
    const d = days[i];
    if (Number(precip[d]) !== -999 && Number(temp[d]) !== -999 && Number(humid[d]) !== -999) {
      validDay = d;
      break;
    }
  }
  if (!validDay) throw new Error("No valid data from NASA POWER for this location");

  const result = {
    rainfall: Number(precip[validDay]),
    temperature: Number(temp[validDay]),
    humidity: Number(humid[validDay]),
  };
  liveCache.set(key, { data: result, at: Date.now() });
  return result;
}

export function getSeasonalRainfallBaseline(stationId: string, season: Season): number | null {
  return HISTORICAL_STATIONS[stationId]?.[season]?.rainfall ?? null;
}
