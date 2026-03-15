import fs from "node:fs";
import path from "node:path";
import CompareContent from "./CompareContent";

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

function loadBestPerFramework(): Record<string, Record<string, number>> {
  const resultsDir = path.join(process.cwd(), "..", "data", "results");
  const data: Record<string, Record<string, number>> = {};

  try {
    if (fs.existsSync(resultsDir)) {
      const files = fs.readdirSync(resultsDir).filter((f) => f.endsWith(".json"));
      for (const file of files) {
        const raw = fs.readFileSync(path.join(resultsDir, file), "utf-8");
        const parsed = JSON.parse(raw) as Record<string, unknown>;
        if (!parsed.framework || !parsed.taskCompletion) continue;
        const fw = parsed.framework as string;
        const scores = {
          "Task Completion": parsed.taskCompletion as number,
          Efficiency: parsed.efficiency as number,
          Security: parsed.security as number,
          Skills: parsed.skills as number,
          UX: parsed.ux as number,
        };
        if (!data[fw] || (parsed.overall as number) > (data[fw]._overall ?? 0)) {
          data[fw] = { ...scores, _overall: parsed.overall as number };
        }
      }
    }
  } catch {
    // Fall through
  }

  for (const fw of Object.keys(data)) {
    delete data[fw]._overall;
  }
  return data;
}

export default function ComparePage() {
  const data = loadBestPerFramework();
  return <CompareContent data={data} />;
}
