"use client";

import { useState, useMemo, useEffect } from "react";
import { useI18n } from "../i18n";

interface CompareContentProps {
  data: Record<string, Record<string, number>>;
}

const categoryI18nMap: Record<string, string> = {
  "Task Completion": "table.taskCompletion",
  Efficiency: "table.efficiency",
  Security: "table.security",
  Skills: "table.skills",
  UX: "table.ux",
};

const CATEGORIES = ["Task Completion", "Efficiency", "Security", "Skills", "UX"];

function RadarChart({ scoresA, scoresB, nameA, nameB }: {
  scoresA: Record<string, number>;
  scoresB: Record<string, number>;
  nameA: string;
  nameB: string;
}) {
  const cx = 150, cy = 150, r = 110;
  const n = CATEGORIES.length;

  function getPoint(i: number, value: number): [number, number] {
    const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
    const dist = (value / 100) * r;
    return [cx + dist * Math.cos(angle), cy + dist * Math.sin(angle)];
  }

  function polygon(scores: Record<string, number>): string {
    return CATEGORIES.map((cat, i) => getPoint(i, scores[cat] || 0).join(",")).join(" ");
  }

  return (
    <svg viewBox="0 0 300 300" style={{ width: "100%", maxWidth: 360, margin: "0 auto", display: "block" }}>
      {[20, 40, 60, 80, 100].map((level) => (
        <polygon
          key={level}
          points={CATEGORIES.map((_, i) => getPoint(i, level).join(",")).join(" ")}
          fill="none"
          stroke="var(--border)"
          strokeWidth={level === 100 ? 1.5 : 0.5}
        />
      ))}
      {CATEGORIES.map((_, i) => {
        const [x, y] = getPoint(i, 100);
        return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="var(--border)" strokeWidth={0.5} />;
      })}
      <polygon points={polygon(scoresA)} fill="rgba(232, 114, 92, 0.2)" stroke="var(--accent)" strokeWidth={2} />
      <polygon points={polygon(scoresB)} fill="rgba(224, 164, 88, 0.2)" stroke="var(--warning)" strokeWidth={2} />
      {CATEGORIES.map((cat, i) => {
        const [x, y] = getPoint(i, 115);
        return (
          <text key={cat} x={x} y={y} textAnchor="middle" dominantBaseline="middle"
            style={{ fontSize: "0.6rem", fill: "var(--text-secondary)" }}>
            {cat}
          </text>
        );
      })}
      <text x={10} y={290} style={{ fontSize: "0.65rem", fill: "var(--accent)", fontWeight: 600 }}>{nameA}</text>
      <text x={200} y={290} style={{ fontSize: "0.65rem", fill: "var(--warning)", fontWeight: 600 }}>{nameB}</text>
    </svg>
  );
}

export default function CompareContent({ data: initialData }: CompareContentProps) {
  const { t } = useI18n();
  const [liveData, setLiveData] = useState<Record<string, Record<string, number>> | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch("/api/leaderboard");
        if (!res.ok) return;
        const entries = await res.json();
        if (!Array.isArray(entries) || entries.length === 0) return;
        const best: Record<string, Record<string, number>> = {};
        for (const e of entries) {
          const fw = e.framework;
          if (!fw) continue;
          const scores = {
            "Task Completion": e.taskCompletion || 0,
            Efficiency: e.efficiency || 0,
            Security: e.security || 0,
            Skills: e.skills || 0,
            UX: e.ux || 0,
            _overall: e.overall || 0,
          };
          if (!best[fw] || scores._overall > (best[fw]._overall || 0)) {
            best[fw] = scores;
          }
        }
        for (const fw of Object.keys(best)) delete best[fw]._overall;
        setLiveData(best);
      } catch {}
    };
    load();
  }, []);

  const data = liveData || initialData;
  const allFrameworks = useMemo(() => Object.keys(data).sort(), [data]);

  const [fwA, setFwA] = useState(() => {
    if (typeof window !== "undefined") {
      const p = new URLSearchParams(window.location.search);
      const a = p.get("a");
      if (a && data[a]) return a;
    }
    return allFrameworks[0] || "";
  });

  const [fwB, setFwB] = useState(() => {
    if (typeof window !== "undefined") {
      const p = new URLSearchParams(window.location.search);
      const b = p.get("b");
      if (b && data[b]) return b;
    }
    return allFrameworks[1] || "";
  });

  useEffect(() => {
    if (liveData) {
      const fws = Object.keys(liveData).sort();
      if (fws.length >= 2) {
        if (!liveData[fwA]) setFwA(fws[0]);
        if (!liveData[fwB]) setFwB(fws[1]);
      }
    }
  }, [liveData]);

  const scoresA = data[fwA] || {};
  const scoresB = data[fwB] || {};

  const selectFw = (fw: string) => {
    if (fw === fwA) return;
    if (fw === fwB) { setFwB(fwA); setFwA(fw); }
    else { setFwB(fwA); setFwA(fw); }
  };

  function tr(cat: string): string {
    const key = categoryI18nMap[cat];
    return key ? t(key) : cat;
  }

  function cls(score: number): string {
    if (score >= 85) return "score score-high";
    if (score >= 70) return "score score-mid";
    return "score score-low";
  }

  if (allFrameworks.length < 2) {
    return (
      <>
        <header className="page-header">
          <h1>{t("compare.title")}</h1>
          <p>{t("compare.subtitleSimple")}</p>
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
        <h1>{t("compare.title")}</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>{t("compare.subtitleSimple")}</p>
      </header>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        {allFrameworks.map((fw) => {
          const isA = fw === fwA;
          const isB = fw === fwB;
          return (
            <button key={fw} onClick={() => selectFw(fw)}
              style={{
                padding: "0.4rem 0.9rem", borderRadius: "6px",
                border: isA || isB ? "none" : "1px solid var(--border)",
                background: isA ? "var(--accent)" : isB ? "var(--warning)" : "transparent",
                color: isA || isB ? "#fff" : "var(--text-secondary)",
                fontWeight: isA || isB ? 600 : 400, fontSize: "0.85rem", cursor: "pointer",
              }}>
              {fw}
            </button>
          );
        })}
      </div>

      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <RadarChart scoresA={scoresA} scoresB={scoresB} nameA={fwA} nameB={fwB} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
        {[
          { name: fwA, scores: scoresA, color: "var(--accent)" },
          { name: fwB, scores: scoresB, color: "var(--warning)" },
        ].map(({ name, scores, color }) => (
          <div key={name} className="card">
            <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem", color }}>{name}</h3>
            <table>
              <tbody>
                {CATEGORIES.map((cat) => {
                  const score = scores[cat] ?? 0;
                  return (
                    <tr key={cat}>
                      <td style={{ fontWeight: 500 }}>{tr(cat)}</td>
                      <td style={{ textAlign: "right" }}><span className={cls(score)}>{score.toFixed(2)}</span></td>
                      <td style={{ width: "40%" }}>
                        <div style={{ height: "8px", borderRadius: "4px", background: "var(--bg-secondary)", overflow: "hidden" }}>
                          <div style={{ height: "100%", width: `${score}%`, borderRadius: "4px", background: color, transition: "width 0.3s" }} />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: "1.5rem" }}>
        <h3 style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "0.75rem" }}>{t("compare.headToHead")}</h3>
        <table>
          <thead>
            <tr>
              <th>{t("compare.category")}</th>
              <th style={{ color: "var(--accent)" }}>{fwA}</th>
              <th style={{ color: "var(--warning)" }}>{fwB}</th>
              <th>{t("compare.delta")}</th>
            </tr>
          </thead>
          <tbody>
            {CATEGORIES.map((cat) => {
              const a = scoresA[cat] ?? 0;
              const b = scoresB[cat] ?? 0;
              const delta = a - b;
              return (
                <tr key={cat}>
                  <td style={{ fontWeight: 500 }}>{tr(cat)}</td>
                  <td style={{ fontFamily: "var(--font-mono)" }}>{a.toFixed(2)}</td>
                  <td style={{ fontFamily: "var(--font-mono)" }}>{b.toFixed(2)}</td>
                  <td style={{
                    fontFamily: "var(--font-mono)", fontWeight: 600,
                    color: delta > 0 ? "var(--success)" : delta < 0 ? "var(--danger)" : "var(--text-secondary)",
                  }}>
                    {delta > 0 ? "+" : ""}{delta.toFixed(2)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}
