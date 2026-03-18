"use client";

import { useI18n } from "../i18n";

interface SkillsGainEntry {
  framework: string;
  vanilla: number;
  curated: number;
  native: number;
  absoluteGain: number;
  normalizedGain: number;
  nativeEfficacy: number;
}

interface SkillsGainContentProps {
  frameworks: SkillsGainEntry[];
}

function safe(v: number | undefined): number {
  return typeof v === "number" && isFinite(v) ? v : 0;
}

function barWidth(value: number): string {
  return `${Math.min(100, value)}%`;
}

function scoreClass(score: number): string {
  if (score >= 85) return "score score-high";
  if (score >= 70) return "score score-mid";
  return "score score-low";
}

export default function SkillsGainContent({ frameworks }: SkillsGainContentProps) {
  const { t } = useI18n();

  return (
    <>
      <header className="page-header">
        <h1>{t("skillsGain.title")}</h1>
        <p>
          {t("skillsGain.skBenchDesc")}.{" "}
          {t("skillsGain.subtitle", { vanilla: t("skillsGain.vanilla"), curated: t("skillsGain.curated"), native: t("skillsGain.native") })}
        </p>
      </header>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1rem",
          marginBottom: "1.5rem",
        }}
      >
        {[
          {
            label: t("skillsGain.methodology"),
            value: t("skillsGain.skBench"),
            sub: t("skillsGain.skBenchDesc"),
          },
          {
            label: t("skillsGain.conditions"),
            value: "3",
            sub: t("skillsGain.conditionsVal"),
          },
          {
            label: t("skillsGain.bestNormGain"),
            value: frameworks.length > 0 ? `${Math.max(...frameworks.map((f) => safe(f.normalizedGain))).toFixed(2)}` : "-",
            sub: frameworks.length > 0 ? (frameworks.reduce((best, f) => safe(f.normalizedGain) > safe(best.normalizedGain) ? f : best)).framework : "-",
          },
          {
            label: t("skillsGain.bestNativeEff"),
            value: frameworks.length > 0 ? `+${Math.max(...frameworks.map((f) => safe(f.nativeEfficacy))).toFixed(2)}%` : "-",
            sub: frameworks.length > 0 ? (frameworks.reduce((best, f) => safe(f.nativeEfficacy) > safe(best.nativeEfficacy) ? f : best)).framework : "-",
          },
        ].map((stat) => (
          <div key={stat.label} className="card" style={{ textAlign: "center" }}>
            <div
              style={{
                fontSize: "0.75rem",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                color: "var(--text-secondary)",
                marginBottom: "0.25rem",
              }}
            >
              {stat.label}
            </div>
            <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{stat.value}</div>
            <div
              style={{
                fontSize: "0.8rem",
                color: "var(--text-secondary)",
                marginTop: "0.15rem",
              }}
            >
              {stat.sub}
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{t("common.framework")}</th>
                <th>{t("skillsGain.vanilla")}</th>
                <th>{t("skillsGain.curated")}</th>
                <th>{t("skillsGain.native")}</th>
                <th>{t("skillsGain.absGain")}</th>
                <th>{t("skillsGain.normGain")}</th>
                <th>{t("skillsGain.nativeEfficacy")}</th>
              </tr>
            </thead>
            <tbody>
              {frameworks.map((fw) => (
                <tr key={fw.framework}>
                  <td style={{ fontWeight: 600 }}>{fw.framework}</td>
                  <td>
                    <span className={scoreClass(fw.vanilla)}>{fw.vanilla.toFixed(2)}</span>
                  </td>
                  <td>
                    <span className={scoreClass(fw.curated)}>{fw.curated.toFixed(2)}</span>
                  </td>
                  <td>
                    <span className={scoreClass(fw.native)}>{fw.native.toFixed(2)}</span>
                  </td>
                  <td
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontWeight: 600,
                      color: "var(--success)",
                    }}
                  >
                    +{fw.absoluteGain.toFixed(2)}
                  </td>
                  <td style={{ fontFamily: "var(--font-mono)" }}>
                    {fw.normalizedGain.toFixed(2)}
                  </td>
                  <td
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontWeight: 600,
                      color: "var(--success)",
                    }}
                  >
                    +{fw.nativeEfficacy.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card" style={{ marginTop: "1.5rem" }}>
        <h3
          style={{
            fontSize: "0.95rem",
            fontWeight: 600,
            marginBottom: "1rem",
          }}
        >
          {t("skillsGain.scoreDist")}
        </h3>
        {frameworks.map((fw) => (
          <div key={fw.framework} style={{ marginBottom: "1rem" }}>
            <div
              style={{
                fontWeight: 600,
                fontSize: "0.85rem",
                marginBottom: "0.35rem",
              }}
            >
              {fw.framework}
            </div>
            {[
              { label: t("skillsGain.vanilla"), value: fw.vanilla, color: "#94a3b8" },
              { label: t("skillsGain.curated"), value: fw.curated, color: "var(--accent)" },
              { label: t("skillsGain.native"), value: fw.native, color: "var(--success)" },
            ].map((bar) => (
              <div
                key={bar.label}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  marginBottom: "0.2rem",
                  fontSize: "0.8rem",
                }}
              >
                <div style={{ width: "55px", color: "var(--text-secondary)" }}>
                  {bar.label}
                </div>
                <div
                  style={{
                    flex: 1,
                    height: "14px",
                    borderRadius: "4px",
                    background: "var(--bg-secondary)",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      height: "100%",
                      width: barWidth(bar.value),
                      borderRadius: "4px",
                      background: bar.color,
                    }}
                  />
                </div>
                <div
                  style={{
                    width: "45px",
                    textAlign: "right",
                    fontFamily: "var(--font-mono)",
                    fontWeight: 500,
                  }}
                >
                  {bar.value.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>

      <footer
        style={{
          marginTop: "3rem",
          paddingBottom: "2rem",
          textAlign: "center",
          fontSize: "0.8rem",
          color: "var(--text-secondary)",
        }}
      >
        {t("skillsGain.footer")}{" "}
        <code style={{ fontFamily: "var(--font-mono)" }}>
          claw-bench run --skills vanilla,curated,native
        </code>{" "}
        to generate real 3-condition comparisons.
      </footer>
    </>
  );
}
