import fs from "node:fs";
import path from "node:path";
import ProfilesContent from "./ProfilesContent";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface AgentProfileData {
  profileId: string;
  displayName: string;
  model: string;
  framework: string;
  skillsMode: string;
  skills: string[];
  mcpServers: string[];
  memoryModules: string[];
  modelTier: string | null;
  tags: Record<string, string>;
}

interface ProgressiveData {
  baseline_pass_rate: number;
  current_pass_rate: number;
  absolute_gain: number;
  normalized_gain: number;
  gain_by_domain?: Record<
    string,
    { baseline: number; current: number; gain: number }
  >;
}

interface BenchResult {
  framework: string;
  model: string;
  overall: number;
  taskCompletion: number;
  efficiency: number;
  security: number;
  skills: number;
  ux: number;
  testTier?: string | null;
  agentProfile?: AgentProfileData | null;
  progressive?: ProgressiveData | null;
}

/* ------------------------------------------------------------------ */
/*  Data loading                                                       */
/* ------------------------------------------------------------------ */

function loadResults(): BenchResult[] {
  const resultsDir = path.join(process.cwd(), "..", "data", "results");

  try {
    if (fs.existsSync(resultsDir)) {
      const files = fs
        .readdirSync(resultsDir)
        .filter((f) => f.endsWith(".json"));

      if (files.length > 0) {
        const all = files.flatMap((file) => {
          const raw = fs.readFileSync(path.join(resultsDir, file), "utf-8");
          const parsed = JSON.parse(raw);
          return Array.isArray(parsed) ? parsed : [parsed];
        });
        const valid = all.filter(
          (r: Record<string, unknown>) =>
            r.framework &&
            r.model &&
            typeof r.overall === "number" &&
            typeof r.taskCompletion === "number"
        );
        if (valid.length > 0) return valid as BenchResult[];
      }
    }
  } catch {
    // Fall through
  }

  return [];
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function groupBy<T>(items: T[], keyFn: (item: T) => string): Record<string, T[]> {
  const groups: Record<string, T[]> = {};
  for (const item of items) {
    const key = keyFn(item);
    if (!groups[key]) groups[key] = [];
    groups[key].push(item);
  }
  return groups;
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function ProfilesPage() {
  const results = loadResults();
  const byModel = groupBy(results, (r) => r.model);
  const byFramework = groupBy(results, (r) => r.framework);

  return <ProfilesContent byModel={byModel} byFramework={byFramework} />;
}
