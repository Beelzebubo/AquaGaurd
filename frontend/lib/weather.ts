const NASA_POWER_URL =
  import.meta.env.VITE_NASA_POWER_URL ??
  "https://power.larc.nasa.gov/api/temporal/daily/point";
const CACHE_TTL = 5 * 60 * 1000;

type CacheEntry = {
  data: LiveWeather;
  at: number;
};
const cache = new Map<string, CacheEntry>();

export type LiveWeather = {
  temperature: number;
  rainfall: number;
  humidity: number;
  date: string;
  loading: boolean;
  error?: string;
};

const NULL_SENTINEL = -999;

function findLatestValidDay(
  precip: Record<string, number>,
  temp: Record<string, number>,
  humid: Record<string, number>,
): string | null {
  const days = Object.keys(precip).sort();
  for (let i = days.length - 1; i >= 0; i--) {
    const d = days[i];
    const p = Number(precip[d]);
    const t = Number(temp[d]);
    const h = Number(humid[d]);
    if (p !== NULL_SENTINEL && t !== NULL_SENTINEL && h !== NULL_SENTINEL) {
      return d;
    }
  }
  return null;
}

export async function fetchLiveWeather(
  lat: number,
  lng: number,
): Promise<LiveWeather> {
  const key = `${lat.toFixed(2)}-${lng.toFixed(2)}`;
  const cached = cache.get(key);
  if (cached && Date.now() - cached.at < CACHE_TTL) {
    return cached.data;
  }

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
  const res = await fetch(`${NASA_POWER_URL}?${params}`, {
    signal: controller.signal,
  });
  clearTimeout(timeoutId);
  if (!res.ok) {
    throw new Error(`NASA POWER error: ${res.status}`);
  }

  const data = await res.json();
  const props = data?.properties?.parameter ?? {};
  const precip = props.PRECTOTCORR ?? {};
  const temp = props.T2M ?? {};
  const humid = props.RH2M ?? {};

  const validDay = findLatestValidDay(precip, temp, humid);
  if (!validDay) {
    throw new Error("No valid data from NASA POWER for this location");
  }

  const result: LiveWeather = {
    temperature: Number(temp[validDay]),
    rainfall: Number(precip[validDay]),
    humidity: Number(humid[validDay]),
    date: validDay,
    loading: false,
  };

  cache.set(key, { data: result, at: Date.now() });
  return result;
}
