import fs from "node:fs";
import path from "node:path";
import ParetoContent from "./ParetoContent";

interface ParetoPoint {
  fw: string;
  model: string;
  tier: string;
  score: number;
  cost: string;
  costNum: number;
  optimal: boolean;
}

function loadModelsConfig(): { costs: Record<string, number>; tiers: Record<string, string> } {
  const filePath = path.join(process.cwd(), "..", "data", "config", "models.json");
  try {
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, "utf-8"));
    }
  } catch {}
  return { costs: {}, tiers: {} };
}

function computePareto(points: ParetoPoint[]): Set<string> {
  const sorted = [...points].sort((a, b) => a.costNum - b.costNum || b.score - a.score);
  const frontier = new Set<string>();
  let bestScore = -Infinity;

  for (const p of sorted) {
    if (p.score > bestScore) {
      frontier.add(`${p.fw}:${p.model}`);
      bestScore = p.score;
    }
  }
  return frontier;
}

function loadParetoData(): ParetoPoint[] {
  const resultsDir = path.join(process.cwd(), "..", "data", "results");
  const { costs, tiers } = loadModelsConfig();

  try {
    if (fs.existsSync(resultsDir)) {
      const files = fs.readdirSync(resultsDir).filter((f) => f.endsWith(".json") && f !== "skills-gain.json");
      const points: ParetoPoint[] = [];

      for (const file of files) {
        const raw = fs.readFileSync(path.join(resultsDir, file), "utf-8");
        const parsed = JSON.parse(raw);
        if (!parsed.framework || !parsed.model || typeof parsed.overall !== "number") continue;

        const model = parsed.model as string;
        const costNum = costs[model] ?? 0.10;
        points.push({
          fw: parsed.framework,
          model,
          tier: tiers[model] || "Other",
          score: parsed.overall,
          cost: `$${costNum.toFixed(2)}`,
          costNum,
          optimal: false,
        });
      }

      if (points.length > 0) {
        const frontier = computePareto(points);
        for (const p of points) {
          p.optimal = frontier.has(`${p.fw}:${p.model}`);
        }
        points.sort((a, b) => b.score - a.score);
        return points;
      }
    }
  } catch {
    // Fall through
  }

  return [];
}

export default function ParetoPage() {
  const dataPoints = loadParetoData();
  return <ParetoContent dataPoints={dataPoints} />;
}
