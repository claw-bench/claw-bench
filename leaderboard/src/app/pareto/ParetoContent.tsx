"use client";

import { useEffect, useState } from "react";
import { useI18n } from "../i18n";

interface ParetoPoint {
  fw: string;
  model: string;
  tier: string;
  score: number;
  cost: string;
  costNum: number;
  optimal: boolean;
}

interface ParetoContentProps {
  dataPoints: ParetoPoint[];
}

const TIER_COLORS: Record<string, string> = {
  Flagship: "var(--accent)",
  Standard: "var(--warning)",
  Economy: "var(--success)",
  "Open Source": "#8b5cf6",
  Other: "var(--text-tertiary)",
};

function ScatterPlot({ points }: { points: ParetoPoint[] }) {
  if (points.length === 0) return null;

  const W = 600, H = 350, PAD = 50;
  const maxCost = Math.max(...points.map((p) => p.costNum)) * 1.15;
  const minScore = Math.min(...points.map((p) => p.score)) * 0.9;
  const maxScore = Math.max(...points.map((p) => p.score)) * 1.05;

  function x(cost: number) { return PAD + ((cost / maxCost) * (W - PAD * 2)); }
  function y(score: number) { return H - PAD - (((score - minScore) / (maxScore - minScore)) * (H - PAD * 2)); }

  const frontier = points.filter((p) => p.optimal).sort((a, b) => a.costNum - b.costNum);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", maxWidth: 700, display: "block", margin: "0 auto" }}>
      {[0.2, 0.4, 0.6, 0.8, 1.0].map((f) => {
        const yPos = H - PAD - f * (H - PAD * 2);
        const label = (minScore + f * (maxScore - minScore)).toFixed(0);
        return (
          <g key={f}>
            <line x1={PAD} y1={yPos} x2={W - PAD} y2={yPos} stroke="var(--border)" strokeWidth={0.5} />
            <text x={PAD - 8} y={yPos + 3} textAnchor="end" style={{ fontSize: "0.55rem", fill: "var(--text-tertiary)" }}>{label}</text>
          </g>
        );
      })}
      {[0.2, 0.4, 0.6, 0.8, 1.0].map((f) => {
        const xPos = PAD + f * (W - PAD * 2);
        const label = `$${(f * maxCost).toFixed(2)}`;
        return (
          <g key={f}>
            <line x1={xPos} y1={PAD} x2={xPos} y2={H - PAD} stroke="var(--border)" strokeWidth={0.5} />
            <text x={xPos} y={H - PAD + 15} textAnchor="middle" style={{ fontSize: "0.55rem", fill: "var(--text-tertiary)" }}>{label}</text>
          </g>
        );
      })}

      {frontier.length >= 2 && (
        <polyline
          points={frontier.map((p) => `${x(p.costNum)},${y(p.score)}`).join(" ")}
          fill="none" stroke="var(--accent)" strokeWidth={2} strokeDasharray="6,3" opacity={0.6}
        />
      )}

      {points.map((p, i) => (
        <g key={i}>
          <circle
            cx={x(p.costNum)} cy={y(p.score)} r={p.optimal ? 7 : 5}
            fill={TIER_COLORS[p.tier] || TIER_COLORS.Other}
            stroke={p.optimal ? "var(--text)" : "none"} strokeWidth={p.optimal ? 1.5 : 0}
            opacity={0.85}
          />
          <title>{`${p.fw} / ${p.model}\nScore: ${p.score}\nCost: ${p.cost}\nTier: ${p.tier}${p.optimal ? " ★ Pareto Optimal" : ""}`}</title>
        </g>
      ))}

      <text x={W / 2} y={H - 5} textAnchor="middle" style={{ fontSize: "0.6rem", fill: "var(--text-secondary)" }}>
        Cost per task (USD)
      </text>
      <text x={12} y={H / 2} textAnchor="middle" transform={`rotate(-90, 12, ${H / 2})`} style={{ fontSize: "0.6rem", fill: "var(--text-secondary)" }}>
        Score
      </text>

      {Object.entries(TIER_COLORS).filter(([t]) => points.some((p) => p.tier === t)).map(([tier, color], i) => (
        <g key={tier} transform={`translate(${PAD + i * 90}, ${PAD - 15})`}>
          <circle cx={0} cy={0} r={4} fill={color} />
          <text x={8} y={3} style={{ fontSize: "0.55rem", fill: "var(--text-secondary)" }}>{tier}</text>
        </g>
      ))}
    </svg>
  );
}

export default function ParetoContent({ dataPoints: initialData }: ParetoContentProps) {
  const { t } = useI18n();
  const [liveData, setLiveData] = useState<ParetoPoint[] | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [lbRes, cfgRes] = await Promise.all([
          fetch("/api/leaderboard"),
          fetch("/api/config/models").catch(() => null),
        ]);
        if (!lbRes.ok) return;
        const entries = await lbRes.json();
        if (!Array.isArray(entries) || entries.length === 0) return;

        let costs: Record<string, number> = {};
        let tiers: Record<string, string> = {};
        if (cfgRes && cfgRes.ok) {
          const cfg = await cfgRes.json();
          costs = cfg.costs || {};
          tiers = cfg.tiers || {};
        }

        const points: ParetoPoint[] = entries.map((e: Record<string, unknown>) => {
          const model = (e.model as string) || "";
          const costNum = costs[model] || 0.10;
          return {
            fw: (e.framework as string) || "",
            model,
            tier: tiers[model] || "Other",
            score: (e.overall as number) || 0,
            cost: `$${costNum.toFixed(2)}`,
            costNum,
            optimal: false,
          };
        });

        const sorted = [...points].sort((a, b) => a.costNum - b.costNum || b.score - a.score);
        let bestScore = -Infinity;
        for (const p of sorted) {
          if (p.score > bestScore) { p.optimal = true; bestScore = p.score; }
        }
        points.sort((a, b) => b.score - a.score);
        setLiveData(points);
      } catch {}
    };
    load();
  }, []);

  const dataPoints = liveData || initialData;
  const frontierCount = dataPoints.filter((p) => p.optimal).length;

  if (dataPoints.length === 0) {
    return (
      <>
        <header className="page-header">
          <h1>{t("pareto.title")}</h1>
          <p>{t("pareto.subtitle")}</p>
        </header>
        <div className="card" style={{ textAlign: "center", padding: "3rem", color: "var(--text-tertiary)" }}>
          {t("common.noRuns")}
        </div>
      </>
    );
  }

  return (
    <>
      <header className="page-header">
        <h1>{t("pareto.title")}</h1>
        <p>{t("pareto.subtitle")}</p>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
        {[
          { label: t("pareto.totalConfigs"), value: String(dataPoints.length), sub: t("pareto.frameworkModelPairs") },
          { label: t("pareto.paretoOptimal"), value: String(frontierCount), sub: t("pareto.frontierPoints") },
          { label: t("pareto.bestScore"), value: Math.max(...dataPoints.map((p) => p.score)).toFixed(2), sub: dataPoints.reduce((best, p) => (p.score > best.score ? p : best)).fw },
          { label: t("pareto.cheapestOptimal"), value: dataPoints.filter((p) => p.optimal).reduce((best, p) => (p.costNum < best.costNum ? p : best)).cost, sub: dataPoints.filter((p) => p.optimal).reduce((best, p) => (p.costNum < best.costNum ? p : best)).fw },
        ].map((stat) => (
          <div key={stat.label} className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-secondary)", marginBottom: "0.25rem" }}>{stat.label}</div>
            <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{stat.value}</div>
            <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "0.15rem" }}>{stat.sub}</div>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <ScatterPlot points={dataPoints} />
      </div>

      <div className="card" style={{ marginTop: "1.5rem" }}>
        <h3 style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "0.75rem" }}>{t("pareto.dataPoints")}</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{t("pareto.framework")}</th>
                <th>{t("pareto.model")}</th>
                <th>{t("common.tier")}</th>
                <th>{t("pareto.score")}</th>
                <th>{t("pareto.costPerTask")}</th>
                <th>{t("pareto.paretoOptimalCol")}</th>
              </tr>
            </thead>
            <tbody>
              {dataPoints.map((p, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{p.fw}</td>
                  <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{p.model}</td>
                  <td><span style={{ fontSize: "0.75rem", padding: "0.1rem 0.5rem", borderRadius: "4px", background: "var(--bg-secondary)" }}>{p.tier}</span></td>
                  <td><span className={`score ${p.score >= 85 ? "score-high" : p.score >= 70 ? "score-mid" : "score-low"}`}>{p.score.toFixed(2)}</span></td>
                  <td style={{ fontFamily: "var(--font-mono)" }}>{p.cost}</td>
                  <td style={{ textAlign: "center", fontWeight: p.optimal ? 700 : 400, color: p.optimal ? "var(--success)" : "var(--text-tertiary)" }}>
                    {p.optimal ? t("pareto.yes") : t("pareto.no")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
