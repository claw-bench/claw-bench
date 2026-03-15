import fs from "node:fs";
import path from "node:path";
import GettingStartedContent from "./GettingStartedContent";

function loadDomains() {
  const filePath = path.join(process.cwd(), "..", "data", "config", "domains.json");
  try {
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, "utf-8"));
    }
  } catch {}
  return [];
}

export default function GettingStartedPage() {
  const domains = loadDomains();
  return <GettingStartedContent domains={domains} />;
}
