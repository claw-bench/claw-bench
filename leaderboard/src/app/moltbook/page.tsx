import fs from "node:fs";
import path from "node:path";
import MoltbookContent from "./MoltbookContent";

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
}

interface MoltBookData {
  clawId: string;
  submitter?: { github_user?: string; display_name?: string };
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
  moltbook?: MoltBookData | null;
}

/* ------------------------------------------------------------------ */
/*  Data                                                               */
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
            r.framework && r.model && typeof r.overall === "number"
        );
        if (valid.length > 0) return valid as BenchResult[];
      }
    }
  } catch {
    /* fall through */
  }

  return [];
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function MoltBookPage() {
  const results = loadResults();

  const byFramework: Record<string, BenchResult[]> = {};
  for (const r of results) {
    const fw = r.framework;
    if (!byFramework[fw]) byFramework[fw] = [];
    byFramework[fw].push(r);
  }

  return <MoltbookContent byFramework={byFramework} />;
}
