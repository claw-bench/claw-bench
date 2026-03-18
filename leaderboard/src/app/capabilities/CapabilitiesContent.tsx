"use client";

import { useEffect, useState } from "react";
import { useI18n } from "../i18n";

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

interface CapabilitiesContentProps {
  bestPerFw: Record<string, BenchResult>;
  capabilities: string[];
  taskCounts: Record<string, number>;
}

const capKeys: Record<string, string> = {
  reasoning: "capabilities.reasoning",
  "tool-use": "capabilities.toolUse",
  memory: "capabilities.memory",
  multimodal: "capabilities.multimodal",
  collaboration: "capabilities.collaboration",
};

function capScore(r: BenchResult, cap: string): number {
  if (!r) return 0;
  switch (cap) {
    case "reasoning":
      return r.taskCompletion * 0.7 + r.overall * 0.3;
    case "tool-use":
      return r.efficiency * 0.6 + r.taskCompletion * 0.4;
    case "memory":
      return r.skills * 0.5 + r.overall * 0.5;
    case "multimodal":
      return r.ux * 0.6 + r.overall * 0.4;
    case "collaboration":
      return (r.taskCompletion + r.efficiency + r.security + r.skills + r.ux) / 5;
    default:
      return r.overall;
  }
}

function scoreClass(score: number): string {
  if (score >= 85) return "score score-high";
  if (score >= 70) return "score score-mid";
  return "score score-low";
}

export default function CapabilitiesContent({ bestPerFw, capabilities, taskCounts }: CapabilitiesContentProps) {
  const { t } = useI18n();

  const [liveBestPerFw, setLiveBestPerFw] = useState<Record<string, BenchResult> | null>(null);
  useEffect(() => {
    fetch("/api/leaderboard")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d && Array.isArray(d) && d.length > 0) {
          const grouped: Record<string, BenchResult> = {};
          for (const entry of d) {
            if (!grouped[entry.framework] || entry.overall > grouped[entry.framework].overall) {
              grouped[entry.framework] = entry;
            }
          }
          setLiveBestPerFw(grouped);
        }
      })
      .catch(() => {});
  }, []);
  const activeBestPerFw = liveBestPerFw || bestPerFw;

  const allFrameworks = Object.keys(activeBestPerFw).sort(
    (a, b) => activeBestPerFw[b].overall - activeBestPerFw[a].overall
  );

  function bestFramework(cap: string): string {
    let best = "";
    let bestS = 0;
    for (const fw of allFrameworks) {
      const s = capScore(activeBestPerFw[fw], cap);
      if (s > bestS) {
        bestS = s;
        best = fw;
      }
    }
    return best;
  }

  return (
    <>
      <header className="page-header">
        <h1>{t("capabilities.title")}</h1>
        <p>{t("capabilities.subtitle")}</p>
      </header>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "1rem",
          marginBottom: "1.5rem",
        }}
      >
        {capabilities.map((cap) => (
          <div key={cap} className="card" style={{ textAlign: "center" }}>
            <div
              style={{
                fontSize: "0.75rem",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                color: "var(--text-secondary)",
                marginBottom: "0.25rem",
              }}
            >
              {t(capKeys[cap])}
            </div>
            <div style={{ fontSize: "1.3rem", fontWeight: 700 }}>
              {taskCounts[cap]} {t("common.tasks")}
            </div>
            <div
              style={{
                fontSize: "0.8rem",
                color: "var(--text-secondary)",
                marginTop: "0.15rem",
              }}
            >
              {t("capabilities.best")} {bestFramework(cap)}
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
                {capabilities.map((cap) => (
                  <th key={cap} style={{ textAlign: "center" }}>
                    {t(capKeys[cap])}
                  </th>
                ))}
                <th style={{ textAlign: "center" }}>{t("capabilities.avg")}</th>
              </tr>
            </thead>
            <tbody>
              {allFrameworks.map((fw) => {
                const scores = capabilities.map((cap) => capScore(activeBestPerFw[fw], cap));
                const avg = scores.reduce((sum, s) => sum + s, 0) / scores.length;
                return (
                  <tr key={fw}>
                    <td style={{ fontWeight: 600 }}>{fw}</td>
                    {capabilities.map((cap, i) => (
                      <td key={cap} style={{ textAlign: "center" }}>
                        <span className={scoreClass(scores[i])}>
                          {scores[i].toFixed(2)}
                        </span>
                      </td>
                    ))}
                    <td style={{ textAlign: "center" }}>
                      <span
                        className={scoreClass(avg)}
                        style={{ fontWeight: 700 }}
                      >
                        {avg.toFixed(2)}
                      </span>
                    </td>
                  </tr>
                );
              })}
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
          {t("capabilities.capProfiles")}
        </h3>
        {allFrameworks.slice(0, 4).map((fw) => (
          <div key={fw} style={{ marginBottom: "1rem" }}>
            <div
              style={{ fontWeight: 600, fontSize: "0.85rem", marginBottom: "0.3rem" }}
            >
              {fw}
            </div>
            {capabilities.map((cap) => {
              const score = capScore(activeBestPerFw[fw], cap);
              return (
                <div
                  key={cap}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    marginBottom: "0.15rem",
                    fontSize: "0.8rem",
                  }}
                >
                  <div
                    style={{
                      width: "90px",
                      color: "var(--text-secondary)",
                      textOverflow: "ellipsis",
                      overflow: "hidden",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {t(capKeys[cap])}
                  </div>
                  <div
                    style={{
                      flex: 1,
                      height: "12px",
                      borderRadius: "4px",
                      background: "var(--bg-secondary)",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        height: "100%",
                        width: `${score}%`,
                        borderRadius: "4px",
                        background: "var(--accent)",
                      }}
                    />
                  </div>
                  <div
                    style={{
                      width: "40px",
                      textAlign: "right",
                      fontFamily: "var(--font-mono)",
                      fontWeight: 500,
                    }}
                  >
                    {score.toFixed(2)}
                  </div>
                </div>
              );
            })}
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
        {t("capabilities.footer")}
      </footer>
    </>
  );
}
