import fs from "node:fs";
import path from "node:path";
import MatrixContent from "./MatrixContent";

interface MatrixEntry {
  framework: string;
  model: string;
  overall: number;
}

function loadMatrix(): {
  frameworks: string[];
  modelTiers: { name: string; models: string[] }[];
  scores: Record<string, Record<string, number | null>>;
} {
  const resultsDir = path.join(process.cwd(), "..", "data", "results");
  const entries: MatrixEntry[] = [];

  try {
    if (fs.existsSync(resultsDir)) {
      const files = fs.readdirSync(resultsDir).filter((f) => f.endsWith(".json") && f !== "skills-gain.json");
      for (const file of files) {
        const raw = fs.readFileSync(path.join(resultsDir, file), "utf-8");
        const parsed = JSON.parse(raw);
        if (parsed.framework && parsed.model && typeof parsed.overall === "number") {
          entries.push({
            framework: parsed.framework,
            model: parsed.model,
            overall: parsed.overall,
          });
        }
      }
    }
  } catch {
    // Fall through
  }

  if (entries.length > 0) {
    const fwSet = new Set<string>();
    const modelSet = new Set<string>();
    const scores: Record<string, Record<string, number | null>> = {};

    for (const e of entries) {
      fwSet.add(e.framework);
      modelSet.add(e.model);
      if (!scores[e.framework]) scores[e.framework] = {};
      scores[e.framework][e.model] = e.overall;
    }

    const frameworks = Array.from(fwSet).sort();
    const models = Array.from(modelSet).sort();

    for (const fw of frameworks) {
      for (const m of models) {
        if (scores[fw][m] === undefined) scores[fw][m] = null;
      }
    }

    const modelsConfigPath = path.join(process.cwd(), "..", "data", "config", "models.json");
    let tierMap: Record<string, string> = {};
    try {
      if (fs.existsSync(modelsConfigPath)) {
        tierMap = JSON.parse(fs.readFileSync(modelsConfigPath, "utf-8")).tiers || {};
      }
    } catch {}
    const tierOrder = ["Flagship", "Standard", "Economy", "Open Source"];
    const tierGroups: Record<string, string[]> = {};
    for (const t of tierOrder) tierGroups[t] = [];
    for (const m of models) {
      const tier = tierMap[m] || "Other";
      if (!tierGroups[tier]) tierGroups[tier] = [];
      tierGroups[tier].push(m);
    }

    const modelTiers = tierOrder
      .filter((t) => tierGroups[t].length > 0)
      .map((t) => ({ name: t, models: tierGroups[t] }));

    if (tierGroups["Other"]?.length > 0) {
      modelTiers.push({ name: "Other", models: tierGroups["Other"] });
    }

    return { frameworks, modelTiers, scores };
  }

  return { frameworks: [], modelTiers: [], scores: {} };
}

export default function MatrixPage() {
  const { frameworks, modelTiers, scores } = loadMatrix();
  return <MatrixContent frameworks={frameworks} modelTiers={modelTiers} scores={scores} />;
}
