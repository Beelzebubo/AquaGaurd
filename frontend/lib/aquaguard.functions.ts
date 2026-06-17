import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import { runEngine, type EngineInput } from "./aquaguard-engine";

const InputSchema = z.object({
  stationId: z.string().min(1).max(80),
  stationName: z.string().min(1).max(120),
  river: z.string().min(1).max(80),
  temperature: z.number().min(-20).max(60),
  rainfall: z.number().min(0).max(500),
  humidity: z.number().min(0).max(100),
  riverFlow: z.number().min(0).max(20000),
  rollingFlow: z.number().min(0.01).max(20000),
  ecoThreshold: z.number().min(0.1).max(5000),
});

export type AnalysisInput = z.infer<typeof InputSchema>;

function fallbackSummary(
  input: AnalysisInput,
  eng: ReturnType<typeof runEngine>,
): string {
  const status = eng.compliance.compliant
    ? "currently meeting IFC PS4 ecological-flow requirements"
    : `falling below IFC PS4 ecological flow by ${eng.compliance.deficit.toFixed(1)} m³/s`;
  const risk = eng.predictedRisk.level;
  return [
    `${input.stationName} on the ${input.river} river is ${status}.`,
    `River flow is ${input.riverFlow.toFixed(1)} m³/s against an ecological threshold of ${input.ecoThreshold} m³/s.`,
    `Forecasted disaster risk is ${risk} (${Math.round(eng.predictedRisk.score * 100)}%) with rainfall ${input.rainfall} mm and humidity ${input.humidity}%.`,
    eng.anomalyDetected
      ? "Anomaly detected in flow patterns — recommend immediate field verification."
      : "No anomalies detected; operational status nominal.",
    `Composite ESG score: ${eng.esgScore}/100.`,
  ].join(" ");
}

async function backendSummary(
  input: AnalysisInput,
  eng: ReturnType<typeof runEngine>,
): Promise<string> {
  const apiUrl = import.meta.env.VITE_APP_URL;
  if (!apiUrl) return fallbackSummary(input, eng);

  try {
    const res = await fetch(`${apiUrl}/analytics`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        station_id: input.stationId,
        rainfall: input.rainfall,
        humidity: input.humidity,
        temperature: input.temperature,
        river_flow: input.riverFlow,
        compliance_score: Math.round(eng.compliance.ratio * 100),
        anomaly_detected: eng.anomalyDetected,
      }),
    });
    if (!res.ok) {
      console.error(
        "Backend analytics error",
        res.status,
        await res.text().catch(() => ""),
      );
      return fallbackSummary(input, eng);
    }
    const j = (await res.json()) as {
      ai_summary?: { summary?: string };
    };
    const txt = j.ai_summary?.summary?.trim();
    return txt || fallbackSummary(input, eng);
  } catch (e) {
    console.error("Backend summary failed:", e);
    return fallbackSummary(input, eng);
  }
}

export const runAquaGuardAnalysis = createServerFn({ method: "POST" })
  .validator((data: unknown) => InputSchema.parse(data))
  .handler(async ({ data }) => {
    const engineInput: EngineInput = {
      temperature: data.temperature,
      rainfall: data.rainfall,
      humidity: data.humidity,
      riverFlow: data.riverFlow,
      rollingFlow: data.rollingFlow,
      ecoThreshold: data.ecoThreshold,
    };
    const engine = runEngine(engineInput);
    const summary = await backendSummary(data, engine);
    return { engine, summary, generatedAt: new Date().toISOString() };
  });
