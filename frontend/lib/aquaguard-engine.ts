// Pure deterministic engine that mirrors the AquaGuard FastAPI backend
// (app/services/*). Safe to import from anywhere (no env, no network).

export type EngineInput = {
  temperature: number; // °C
  rainfall: number; // mm/24h
  humidity: number; // %
  riverFlow: number; // m3/s
  rollingFlow: number; // m3/s 7-day rolling avg
  ecoThreshold: number; // m3/s minimum ecological flow
};

export type EngineResult = {
  predictedRisk: { level: "low" | "moderate" | "high" | "critical"; score: number };
  compliance: { compliant: boolean; ratio: number; deficit: number };
  alerts: string[];
  anomalyDetected: boolean;
  esgScore: number;
  forecast: { hour: number; flow: number; risk: number }[];
};

const clamp = (n: number, min: number, max: number) => Math.max(min, Math.min(max, n));

export function predictRisk(input: EngineInput): EngineResult["predictedRisk"] {
  // Heuristic from FloodPredictionModel feature weights (rainfall dominant).
  const rainfallW = clamp(input.rainfall / 200, 0, 1) * 0.55;
  const humidityW = clamp((input.humidity - 50) / 50, 0, 1) * 0.15;
  const tempW = clamp((35 - input.temperature) / 35, 0, 1) * 0.05;
  const flowW = clamp(input.riverFlow / Math.max(input.ecoThreshold * 6, 1), 0, 1) * 0.25;
  const score = clamp(rainfallW + humidityW + tempW + flowW, 0, 1);
  const level = score >= 0.8 ? "critical" : score >= 0.55 ? "high" : score >= 0.3 ? "moderate" : "low";
  return { level, score };
}

export function evaluateCompliance(currentFlow: number, ecoThreshold: number) {
  const ratio = ecoThreshold > 0 ? currentFlow / ecoThreshold : 1;
  const compliant = currentFlow >= ecoThreshold;
  return { compliant, ratio, deficit: Math.max(ecoThreshold - currentFlow, 0) };
}

export function detectAnomaly(rainfall: number, riverFlow: number, rollingFlow: number) {
  // FastAPI app/services/anomaly_detection: spike in flow vs rolling avg OR heavy rain w/ low flow.
  const spike = rollingFlow > 0 ? riverFlow / rollingFlow : 1;
  if (spike > 2.0) return { anomaly: true, message: `Flow spike detected (${spike.toFixed(2)}× rolling average) — possible flash flood.` };
  if (rainfall > 120 && riverFlow < rollingFlow * 0.8)
    return { anomaly: true, message: "Heavy rainfall with suppressed flow — possible upstream obstruction." };
  if (spike < 0.4)
    return { anomaly: true, message: `Severe flow drop (${spike.toFixed(2)}× rolling average) — sediment intake risk.` };
  return { anomaly: false, message: "" };
}

export function calculateEsgScore(complianceRatio: number, anomalyDetected: boolean): number {
  const base = clamp(complianceRatio, 0, 1.5) * 60; // up to 90
  const compliancePts = complianceRatio >= 1 ? 25 : 25 * clamp(complianceRatio, 0, 1);
  const anomalyPenalty = anomalyDetected ? 18 : 0;
  return Math.round(clamp(base + compliancePts - anomalyPenalty, 0, 100));
}

export function forecastNext24h(input: EngineInput): EngineResult["forecast"] {
  const out: EngineResult["forecast"] = [];
  for (let h = 1; h <= 24; h++) {
    const decay = Math.exp(-h / 18);
    const noise = Math.sin(h * 1.3) * 0.04;
    const flow = input.riverFlow * (0.92 + decay * 0.2 + noise);
    const r = predictRisk({ ...input, riverFlow: flow, rainfall: input.rainfall * decay });
    out.push({ hour: h, flow: Math.round(flow * 10) / 10, risk: Math.round(r.score * 100) });
  }
  return out;
}

export function runEngine(input: EngineInput): EngineResult {
  const predictedRisk = predictRisk(input);
  const compliance = evaluateCompliance(input.riverFlow, input.ecoThreshold);
  const anomaly = detectAnomaly(input.rainfall, input.riverFlow, input.rollingFlow);
  const alerts: string[] = [];
  if (anomaly.anomaly) alerts.push(anomaly.message);
  if (!compliance.compliant)
    alerts.push(
      `IFC PS4 non-compliance: ecological flow deficit of ${compliance.deficit.toFixed(1)} m³/s.`,
    );
  if (predictedRisk.level === "critical")
    alerts.push("Critical disaster risk — initiate emergency spillway protocol.");
  else if (predictedRisk.level === "high")
    alerts.push("Elevated risk — pre-position response crews and monitor every 15 minutes.");
  const esgScore = calculateEsgScore(compliance.ratio, anomaly.anomaly);
  const forecast = forecastNext24h(input);
  return {
    predictedRisk,
    compliance,
    alerts,
    anomalyDetected: anomaly.anomaly,
    esgScore,
    forecast,
  };
}