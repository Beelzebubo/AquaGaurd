import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

export type DischargeRecord = {
  datetime: string;
  discharge: number;
};

function parseCsvLine(line: string): DischargeRecord | null {
  const trimmed = line.trim();
  if (!trimmed) return null;
  const commaIdx = trimmed.indexOf(",");
  if (commaIdx === -1) return null;
  const dt = trimmed.slice(0, commaIdx).trim();
  const val = trimmed.slice(commaIdx + 1).trim();
  const num = Number(val);
  if (!dt || isNaN(num) || num <= 0) return null;
  return { datetime: dt, discharge: num };
}

function parseMelamchiLine(line: string): DischargeRecord | null {
  const trimmed = line.trim();
  if (!trimmed) return null;
  const commaIdx = trimmed.indexOf(",");
  if (commaIdx === -1) return null;
  const dt = trimmed.slice(0, commaIdx).trim().replace(" 00:00:00", "");
  const val = trimmed.slice(commaIdx + 1).trim();
  const num = Number(val);
  if (!dt || isNaN(num) || num <= 0) return null;
  return { datetime: dt, discharge: num };
}

function generateSyntheticData(
  baseRecords: DischargeRecord[],
  ecoThreshold: number,
  baseEcoThreshold: number,
  targetId: string,
): DischargeRecord[] {
  if (baseRecords.length === 0) return [];
  const ratio = ecoThreshold / baseEcoThreshold;
  const seed = targetId.split("").reduce((a, c) => a + c.charCodeAt(0), 0);

  return baseRecords.map((r, i) => {
    const noise = 1 + (Math.sin(i * 0.1 + seed) * 0.15 + Math.cos(i * 0.07 + seed * 0.5) * 0.1);
    return {
      datetime: r.datetime,
      discharge: Math.round(r.discharge * ratio * noise * 10) / 10,
    };
  });
}

const STATION_ECO_MAP: Record<string, number> = {
  chisapani: 280,
  "upper-tamakoshi": 35,
  melamchi: 12,
  kulekhani: 8,
  "kali-gandaki-a": 95,
  marsyangdi: 45,
  trishuli: 38,
  "arun-iii": 120,
  "sapta-koshi": 320,
  "budhi-gandaki": 110,
};

export const getHistoricalData = createServerFn({ method: "GET" })
  .validator((d: unknown) =>
    z
      .object({
        stationId: z.string().min(1).max(80),
        yearStart: z.number().optional(),
        yearEnd: z.number().optional(),
      })
      .parse(d),
  )
  .handler(async ({ data }) => {
    const { readFileSync, existsSync } = await import("node:fs");
    const { resolve } = await import("node:path");
    const baseEcoThreshold = STATION_ECO_MAP["chisapani"] ?? 280;
    const ecoThreshold = STATION_ECO_MAP[data.stationId];

    function readCsvFile(filePath: string, parser: (line: string) => DischargeRecord | null): DischargeRecord[] {
      if (!existsSync(filePath)) return [];
      const content = readFileSync(filePath, "utf-8");
      const lines = content.split("\n");
      const records: DischargeRecord[] = [];
      for (let i = 1; i < lines.length; i++) {
        const r = parser(lines[i]);
        if (r) records.push(r);
      }
      return records;
    }

    let records: DischargeRecord[] = [];

    if (data.stationId === "chisapani") {
      const csvPath = resolve(process.cwd(), "chisapani_yearly_csv", "chisapani_master_cleaned.csv");
      records = readCsvFile(csvPath, parseCsvLine);
    } else if (data.stationId === "melamchi") {
      const csvPath = resolve(process.cwd(), "Datasets", "melamchi_waterflow.csv");
      records = readCsvFile(csvPath, parseMelamchiLine);
    } else {
      const chisapaniPath = resolve(process.cwd(), "chisapani_yearly_csv", "chisapani_master_cleaned.csv");
      const baseRecords = readCsvFile(chisapaniPath, parseCsvLine);
      records = generateSyntheticData(baseRecords, ecoThreshold ?? 100, baseEcoThreshold, data.stationId);
    }

    const years = records.map((r) => new Date(r.datetime).getFullYear()).filter((y) => !isNaN(y));
    const minYear = years.length > 0 ? Math.min(...years) : 0;
    const maxYear = years.length > 0 ? Math.max(...years) : 0;

    let filtered = records;
    if (data?.yearStart || data?.yearEnd) {
      const ys = data?.yearStart ?? minYear;
      const ye = data?.yearEnd ?? maxYear;
      filtered = records.filter((r) => {
        const y = new Date(r.datetime).getFullYear();
        return !isNaN(y) && y >= ys && y <= ye;
      });
    }

    return { records: filtered, minYear, maxYear, stationId: data.stationId };
  });
