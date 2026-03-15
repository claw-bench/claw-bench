import fs from "node:fs";
import path from "node:path";
import DomainsContent from "./DomainsContent";

interface Domain {
  id: string;
  name: string;
  tasks: number;
  l1: number;
  l2: number;
  l3: number;
  l4: number;
}

function loadDomains(): Domain[] {
  const filePath = path.join(process.cwd(), "..", "data", "config", "domains.json");
  try {
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, "utf-8"));
    }
  } catch {}
  return [];
}

export default function DomainsPage() {
  const domains = loadDomains();

  const totals = {
    tasks: domains.reduce((s, d) => s + d.tasks, 0),
    l1: domains.reduce((s, d) => s + d.l1, 0),
    l2: domains.reduce((s, d) => s + d.l2, 0),
    l3: domains.reduce((s, d) => s + d.l3, 0),
    l4: domains.reduce((s, d) => s + d.l4, 0),
  };

  return <DomainsContent domains={domains} totals={totals} />;
}
