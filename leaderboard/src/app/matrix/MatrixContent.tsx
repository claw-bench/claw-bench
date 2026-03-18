"use client";

import { useEffect, useState } from "react";
import { useI18n } from "../i18n";

interface MatrixContentProps {
  frameworks: string[];
  modelTiers: { name: string; models: string[] }[];
  scores: Record<string, Record<string, number | null>>;
}

function cellColor(score: number | null): string {
  if (score === null) return "var(--bg-secondary)";
  if (score >= 85) return "var(--success)";
  if (score >= 75) return "var(--warning)";
  return "var(--danger)";
}

function cellOpacity(score: number | null): number {
  if (score === null) return 0.3;
  return 0.4 + ((score - 60) / 40) * 0.6;
}

export default function MatrixContent({ frameworks, modelTiers, scores }: MatrixContentProps) {
  const { t } = useI18n();

  const [liveMatrix, setLiveMatrix] = useState<MatrixContentProps | null>(null);
  useEffect(() => {
    Promise.all([
      fetch("/api/leaderboard").then((r) => (r.ok ? r.json() : null)),
      fetch("/api/config/models").then((r) => (r.ok ? r.json() : null)).catch(() => null),
    ]).then(([lb, modelsConfig]) => {
      if (lb && Array.isArray(lb) && lb.length > 0) {
        const fwSet = new Set<string>();
        const modelSet = new Set<string>();
        const scoreMap: Record<string, Record<string, number | null>> = {};
        for (const entry of lb) {
          fwSet.add(entry.framework);
          modelSet.add(entry.model);
          if (!scoreMap[entry.framework]) scoreMap[entry.framework] = {};
          const existing = scoreMap[entry.framework][entry.model];
          if (existing === undefined || existing === null || entry.overall > existing) {
            scoreMap[entry.framework][entry.model] = entry.overall;
          }
        }
        let tiers: { name: string; models: string[] }[];
        if (modelsConfig && Array.isArray(modelsConfig)) {
          tiers = modelsConfig;
        } else {
          tiers = [{ name: "All Models", models: Array.from(modelSet).sort() }];
        }
        setLiveMatrix({
          frameworks: Array.from(fwSet).sort(),
          modelTiers: tiers,
          scores: scoreMap,
        });
      }
    }).catch(() => {});
  }, []);
  const activeFrameworks = liveMatrix?.frameworks || frameworks;
  const activeModelTiers = liveMatrix?.modelTiers || modelTiers;
  const activeScores = liveMatrix?.scores || scores;

  const allModelColumns = activeModelTiers.flatMap((tier) => tier.models);

  return (
    <>
      <header className="page-header">
        <h1>{t("matrix.title")}</h1>
        <p>{t("matrix.subtitle")}</p>
      </header>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th
                  rowSpan={2}
                  style={{ position: "sticky", left: 0, background: "var(--bg-card)", zIndex: 2, verticalAlign: "bottom" }}
                >
                  {t("matrix.frameworkModel")}
                </th>
                {activeModelTiers.map((tier) => (
                  <th
                    key={tier.name}
                    colSpan={tier.models.length}
                    style={{
                      textAlign: "center",
                      fontSize: "0.75rem",
                      fontWeight: 700,
                      borderBottom: "2px solid var(--border)",
                    }}
                  >
                    {tier.name}
                  </th>
                ))}
              </tr>
              <tr>
                {allModelColumns.map((model) => (
                  <th key={model} style={{ textAlign: "center", fontSize: "0.65rem", fontWeight: 500 }}>
                    {model}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {activeFrameworks.map((fw) => (
                <tr key={fw}>
                  <td
                    style={{
                      fontWeight: 600,
                      position: "sticky",
                      left: 0,
                      background: "var(--bg-card)",
                      zIndex: 1,
                    }}
                  >
                    {fw}
                  </td>
                  {allModelColumns.map((model) => {
                    const score = activeScores[fw]?.[model] ?? null;
                    return (
                      <td
                        key={model}
                        style={{
                          textAlign: "center",
                          fontFamily: "var(--font-mono)",
                          fontSize: "0.85rem",
                          fontWeight: 600,
                          color: score !== null ? "#fff" : "var(--text-secondary)",
                          background: cellColor(score),
                          opacity: cellOpacity(score),
                        }}
                      >
                        {score !== null ? score.toFixed(2) : "--"}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div
        style={{
          display: "flex",
          gap: "1rem",
          marginTop: "1rem",
          fontSize: "0.75rem",
          color: "var(--text-secondary)",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <span>{t("matrix.legend")}</span>
        <span style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
          <span
            style={{
              display: "inline-block",
              width: "12px",
              height: "12px",
              borderRadius: "2px",
              background: "var(--success)",
            }}
          />
          {t("matrix.score85")}
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
          <span
            style={{
              display: "inline-block",
              width: "12px",
              height: "12px",
              borderRadius: "2px",
              background: "var(--warning)",
            }}
          />
          {t("matrix.score75")}
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
          <span
            style={{
              display: "inline-block",
              width: "12px",
              height: "12px",
              borderRadius: "2px",
              background: "var(--danger)",
            }}
          />
          {t("matrix.scoreBelow75")}
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
          <span
            style={{
              display: "inline-block",
              width: "12px",
              height: "12px",
              borderRadius: "2px",
              background: "var(--bg-secondary)",
              border: "1px solid var(--border)",
            }}
          />
          {t("matrix.notTested")}
        </span>
      </div>
    </>
  );
}
