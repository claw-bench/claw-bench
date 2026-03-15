import fs from "node:fs";
import path from "node:path";
import AgentHistoryContent from "./AgentHistoryContent";

export function generateStaticParams() {
  const moltbookDir = path.join(process.cwd(), "..", "data", "moltbook");
  try {
    if (fs.existsSync(moltbookDir)) {
      const files = fs.readdirSync(moltbookDir).filter((f) => f.endsWith(".json"));
      if (files.length > 0) {
        return files.map((f) => ({ clawId: f.replace(".json", "") }));
      }
    }
  } catch {}
  return [{ clawId: "_placeholder" }];
}

interface HistoryEntry {
  date: string;
  tier: string;
  overall: number;
  passRate: number;
}

function loadAgentHistory(clawId: string): {
  displayName: string;
  framework: string;
  model: string;
  submitter: string;
  history: HistoryEntry[];
} {
  const moltbookDir = path.join(process.cwd(), "..", "data", "moltbook");
  const filePath = path.join(moltbookDir, `${clawId}.json`);
  try {
    if (fs.existsSync(filePath)) {
      const data = JSON.parse(fs.readFileSync(filePath, "utf-8"));
      return {
        displayName: data.displayName || clawId,
        framework: data.framework || "Unknown",
        model: data.model || "Unknown",
        submitter: data.submitter || "-",
        history: (data.runs || []).map((r: Record<string, unknown>) => ({
          date: r.date || "",
          tier: r.tier || "",
          overall: r.overall || 0,
          passRate: r.passRate || 0,
        })),
      };
    }
  } catch {}
  return { displayName: clawId, framework: "Unknown", model: "Unknown", submitter: "-", history: [] };
}

export default async function AgentHistoryPage({
  params,
}: {
  params: Promise<{ clawId: string }>;
}) {
  const { clawId } = await params;
  const data = loadAgentHistory(clawId);

  return (
    <AgentHistoryContent
      clawId={clawId}
      displayName={data.displayName}
      framework={data.framework}
      model={data.model}
      submitter={data.submitter}
      history={data.history}
    />
  );
}
