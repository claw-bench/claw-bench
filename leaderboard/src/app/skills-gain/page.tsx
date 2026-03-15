import fs from "node:fs";
import path from "node:path";
import SkillsGainContent from "./SkillsGainContent";

interface SkillsGainEntry {
  framework: string;
  vanilla: number;
  curated: number;
  native: number;
  absoluteGain: number;
  normalizedGain: number;
  nativeEfficacy: number;
}

function loadSkillsGain(): SkillsGainEntry[] {
  const filePath = path.join(process.cwd(), "..", "data", "skills-gain", "skills-gain.json");

  try {
    if (fs.existsSync(filePath)) {
      const raw = fs.readFileSync(filePath, "utf-8");
      const data = JSON.parse(raw);
      if (Array.isArray(data) && data.length > 0 && "framework" in data[0]) {
        return data.map((d: Record<string, number | string>) => {
          const vanilla = (d.vanilla as number) || 0;
          const curated = (d.curated as number) || 0;
          const native_ = (d.native as number) || 0;
          const absGain = curated - vanilla;
          const ceiling = 100 - vanilla;
          return {
            framework: d.framework as string,
            vanilla,
            curated,
            native: native_,
            absoluteGain: d.absoluteGain != null ? (d.absoluteGain as number) : absGain,
            normalizedGain: d.normalizedGain != null ? (d.normalizedGain as number) : (ceiling > 0 ? absGain / ceiling : 0),
            nativeEfficacy: d.nativeEfficacy != null ? (d.nativeEfficacy as number) : native_ / Math.max(curated, 1),
          };
        });
      }
    }
  } catch {
    // Fall through
  }

  return [];
}

export default function SkillsGainPage() {
  const frameworks = loadSkillsGain();
  return <SkillsGainContent frameworks={frameworks} />;
}
