import fs from "node:fs";
import path from "node:path";
import CapabilitiesContent from "./CapabilitiesContent";

interface BenchResult {
  framework: string;
  model: string;
  overall: number;
  taskCompletion: number;
  efficiency: number;
  security: number;
  skills: number;
  ux: number;
}

function loadBestPerFramework(): Record<string, BenchResult> {
  const resultsDir = path.join(process.cwd(), "..", "data", "results");
  const best: Record<string, BenchResult> = {};

  try {
    if (fs.existsSync(resultsDir)) {
      const files = fs.readdirSync(resultsDir).filter((f) => f.endsWith(".json") && f !== "skills-gain.json");
      for (const file of files) {
        const raw = fs.readFileSync(path.join(resultsDir, file), "utf-8");
        const parsed = JSON.parse(raw) as BenchResult;
        if (!parsed.framework || typeof parsed.overall !== "number") continue;
        if (!best[parsed.framework] || parsed.overall > best[parsed.framework].overall) {
          best[parsed.framework] = parsed;
        }
      }
    }
  } catch {
    // Fall through
  }

  return best;
}

function loadCapabilitiesConfig(): { capabilities: string[]; taskCounts: Record<string, number> } {
  const filePath = path.join(process.cwd(), "..", "data", "config", "capabilities.json");
  try {
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, "utf-8"));
    }
  } catch {}
  return { capabilities: [], taskCounts: {} };
}

export default function CapabilitiesPage() {
  const bestPerFw = loadBestPerFramework();
  const { capabilities, taskCounts } = loadCapabilitiesConfig();
  return <CapabilitiesContent bestPerFw={bestPerFw} capabilities={capabilities} taskCounts={taskCounts} />;
}
