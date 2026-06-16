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

async function geminiSummary(
  input: AnalysisInput,
  eng: ReturnType<typeof runEngine>,
): Promise<string> {
  const apiKey = process.env.LOVABLE_API_KEY;
  if (!apiKey) return fallbackSummary(input, eng);

  const prompt = `Station: ${input.stationName} (${input.river} river)
River Flow: ${input.riverFlow.toFixed(1)} m³/s
Ecological Threshold: ${input.ecoThreshold} m³/s
Rainfall (24h): ${input.rainfall} mm
Humidity: ${input.humidity}%
Temperature: ${input.temperature}°C
Compliance Ratio: ${eng.compliance.ratio.toFixed(2)}
Compliance Status: ${eng.compliance.compliant ? "COMPLIANT" : "NON-COMPLIANT"}
Predicted Risk: ${eng.predictedRisk.level} (${Math.round(eng.predictedRisk.score * 100)}%)
Anomaly Detected: ${eng.anomalyDetected ? "YES" : "NO"}
ESG Score: ${eng.esgScore}/100
Active Alerts: ${eng.alerts.length ? eng.alerts.join(" | ") : "none"}

Generate a concise IFC PS4 compliance summary (4-6 sentences) for a hydropower ESG monitoring dashboard.
Mention: ecological flow conditions, environmental risk, operational status, compliance interpretation, and a single concrete next action. Keep it professional, plain prose, no markdown headings.`;

  try {
    const aiUrl =
      import.meta.env.VITE_LOVABLE_API_URL ||
      "https://ai.gateway.lovable.dev/v1/chat/completions";
    const res = await fetch(aiUrl, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "google/gemini-3-flash-preview",
          messages: [
            {
              role: "system",
              content:
                "You are AquaGuard, an IFC PS4 compliance analyst for Nepali hydropower plants.",
            },
            { role: "user", content: prompt },
          ],
        }),
      },
    );
    if (!res.ok) {
      console.error(
        "Lovable AI error",
        res.status,
        await res.text().catch(() => ""),
      );
      return fallbackSummary(input, eng);
    }
    const j = (await res.json()) as {
      choices?: { message?: { content?: string } }[];
    };
    const txt = j.choices?.[0]?.message?.content?.trim();
    return txt || fallbackSummary(input, eng);
  } catch (e) {
    console.error("Gemini summary failed:", e);
    return fallbackSummary(input, eng);
  }
}

export const runAquaGuardAnalysis = createServerFn({ method: "POST" })
  .inputValidator((data: unknown) => InputSchema.parse(data))
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
    const summary = await geminiSummary(data, engine);
    return { engine, summary, generatedAt: new Date().toISOString() };
  });
