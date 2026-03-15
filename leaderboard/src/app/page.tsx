import fs from "node:fs";
import path from "node:path";
import LeaderboardTable, { type BenchResultData } from "./LeaderboardTable";
import { HomeHeader, HomeFooter } from "./HomeHeader";

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
  gain_by_domain?: Record<string, { baseline: number; current: number; gain: number }>;
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

  // Try to load real results from data/results/*.json
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
        // Filter to entries that have all required BenchResult fields
        const valid = all.filter(
          (r: Record<string, unknown>) =>
            r.framework && r.model && typeof r.overall === "number" && typeof r.taskCompletion === "number"
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

/** Dedup results by profileId — keep the entry with the highest overall score. */
function dedupByProfile(results: BenchResult[]): BenchResult[] {
  const best = new Map<string, BenchResult>();
  for (const r of results) {
    const key = r.agentProfile?.profileId ?? `${r.framework}:${r.model}`;
    const existing = best.get(key);
    if (!existing || r.overall > existing.overall) {
      best.set(key, r);
    }
  }
  return Array.from(best.values());
}

export default function LeaderboardPage() {
  const results = loadResults();

  // Dedup by profile and sort by overall descending
  const sorted = dedupByProfile(results).sort((a, b) => b.overall - a.overall);

  return (
    <>
      <HomeHeader />
      <LeaderboardTable data={sorted as BenchResultData[]} />
      <HomeFooter />
    </>
  );
}
