"use client";

import { useState, useMemo, useEffect } from "react";
import { useI18n } from "./i18n";

type WeightProfile = "general" | "security" | "performance";

const WEIGHT_PROFILES: Record<
  WeightProfile,
  { labelKey: string; weights: Record<string, number> }
> = {
  general: {
    labelKey: "table.general",
    weights: {
      taskCompletion: 0.4,
      efficiency: 0.2,
      security: 0.15,
      skills: 0.15,
      ux: 0.1,
    },
  },
  security: {
    labelKey: "table.securityFirst",
    weights: {
      taskCompletion: 0.25,
      efficiency: 0.1,
      security: 0.4,
      skills: 0.15,
      ux: 0.1,
    },
  },
  performance: {
    labelKey: "table.performanceFirst",
    weights: {
      taskCompletion: 0.3,
      efficiency: 0.35,
      security: 0.1,
      skills: 0.15,
      ux: 0.1,
    },
  },
};

interface AgentProfileData {
  profileId: string;
  displayName: string;
}

interface ProgressiveData {
  absolute_gain: number;
}

export interface BenchResultData {
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
  progressive?: ProgressiveData | null;
  region?: { code: string; name: string; flag: string } | null;
  clawId?: string | null;
  submissionCount?: number | null;
  lastUpdated?: string | null;
}

function scoreClass(score: number): string {
  if (score >= 85) return "score score-high";
  if (score >= 70) return "score score-mid";
  return "score score-low";
}

function computeOverall(
  row: BenchResultData,
  weights: Record<string, number>
): number {
  return (
    row.taskCompletion * weights.taskCompletion +
    row.efficiency * weights.efficiency +
    row.security * weights.security +
    row.skills * weights.skills +
    row.ux * weights.ux
  );
}

type TierFilter = "all" | "quick" | "full" | "track";

export default function LeaderboardTable({
  data: initialData,
}: {
  data: BenchResultData[];
}) {
  const [profile, setProfile] = useState<WeightProfile>("general");
  const [tierFilter, setTierFilter] = useState<TierFilter>("all");
  const [liveData, setLiveData] = useState<BenchResultData[] | null>(null);
  const { t } = useI18n();

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch("/api/leaderboard");
        if (res.ok) {
          const d = await res.json();
          if (Array.isArray(d) && d.length > 0) setLiveData(d);
        }
      } catch {}
    };
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, []);

  const data = liveData || initialData;

  const sorted = useMemo(() => {
    const weights = WEIGHT_PROFILES[profile].weights;
    let filtered = data;
    if (tierFilter !== "all") {
      filtered = data.filter((r) => r.testTier === tierFilter);
    }
    return [...filtered]
      .map((row) => ({
        ...row,
        overall: Math.round(computeOverall(row, weights) * 10) / 10,
      }))
      .sort((a, b) => b.overall - a.overall);
  }, [data, profile, tierFilter]);

  return (
    <>
      <section style={{ marginBottom: "1.5rem" }}>
        <div
          style={{
            fontSize: "0.8rem",
            fontWeight: 600,
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            color: "var(--text-secondary)",
            marginBottom: "0.5rem",
          }}
        >
          {t("table.weightProfile")}
        </div>
        <div className="weight-selector">
          {Object.entries(WEIGHT_PROFILES).map(([key, p]) => (
            <button
              key={key}
              className={key === profile ? "active" : ""}
              onClick={() => setProfile(key as WeightProfile)}
              title={`Weights: ${Object.entries(p.weights)
                .map(([k, v]) => `${k}: ${(v * 100).toFixed(0)}%`)
                .join(", ")}`}
            >
              {t(p.labelKey)}
            </button>
          ))}
        </div>
        <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
          {([
            ["all", t("table.allTiers")],
            ["quick", t("table.quickTier")],
            ["full", t("table.compTier")],
            ["track", t("table.trackTier")],
          ] as [TierFilter, string][]).map(([key, label]) => (
            <button
              key={key}
              className={key === tierFilter ? "active" : ""}
              onClick={() => setTierFilter(key)}
              style={{
                padding: "0.3rem 0.8rem",
                border: key === tierFilter ? "none" : "1px solid var(--border)",
                borderRadius: "6px",
                background: key === tierFilter ? "var(--text-secondary)" : "transparent",
                color: key === tierFilter ? "#fff" : "var(--text-tertiary)",
                fontWeight: 500,
                fontSize: "0.75rem",
                cursor: "pointer",
              }}
            >
              {label} ({data.filter((r) => key === "all" || r.testTier === key).length})
            </button>
          ))}
        </div>
      </section>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th style={{ width: "3.5rem" }}>{t("table.rank")}</th>
                <th>{t("table.region")}</th>
                <th>{t("table.agent")}</th>
                <th>{t("table.overall")}</th>
                <th>{t("table.gain")}</th>
                <th>{t("table.submissions")}</th>
                <th>{t("table.lastUpdated")}</th>
                <th>{t("table.taskCompletion")}</th>
                <th>{t("table.efficiency")}</th>
                <th>{t("table.security")}</th>
                <th>{t("table.skills")}</th>
                <th>{t("table.ux")}</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((row, i) => {
                const rank = i + 1;
                const rankClass =
                  rank <= 3 ? `rank rank-${rank}` : "rank";
                const displayName =
                  row.agentProfile?.displayName ??
                  `${row.framework} / ${row.model}`;
                const gain = row.progressive?.absolute_gain;
                const regionFlag = row.region?.flag || "🌍";
                const regionName = row.region?.name || "";
                const clawId = row.clawId || row.agentProfile?.profileId || "";
                const subCount = row.submissionCount || 1;
                const lastUp = row.lastUpdated ? row.lastUpdated.split("T")[0] : "-";
                return (
                  <tr
                    key={`${row.framework}-${row.model}-${row.agentProfile?.profileId ?? i}`}
                  >
                    <td className={rankClass}>{rank}</td>
                    <td title={regionName} style={{ fontSize: "1.1rem", textAlign: "center" }}>
                      {regionFlag}
                    </td>
                    <td>
                      <div style={{ fontWeight: 600 }}>{displayName}</div>
                      <div style={{ fontSize: "0.72rem", color: "var(--text-secondary)", marginTop: "0.1rem" }}>
                        {row.framework && row.model && row.framework !== "unknown"
                          ? `${row.framework} · ${row.model}`
                          : row.framework || row.model || ""}
                      </div>
                      {clawId && (
                        <div style={{ fontSize: "0.65rem", color: "var(--text-tertiary)", fontFamily: "var(--font-mono)" }}>
                          {clawId}
                        </div>
                      )}
                    </td>
                    <td>
                      <span className={scoreClass(row.overall)}>
                        {row.overall.toFixed(2)}
                      </span>
                    </td>
                    <td>
                      {gain != null ? (
                        <span style={{ color: gain >= 0 ? "var(--success)" : "var(--danger)", fontWeight: 600, fontSize: "0.85rem" }}>
                          {gain >= 0 ? "+" : ""}{(gain * 100).toFixed(2)}%
                        </span>
                      ) : (
                        <span style={{ color: "var(--text-tertiary)", fontSize: "0.8rem" }}>-</span>
                      )}
                    </td>
                    <td style={{ textAlign: "center", fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>
                      {subCount}
                    </td>
                    <td style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>
                      {lastUp}
                    </td>
                    <td>
                      <span className={scoreClass(row.taskCompletion)}>
                        {row.taskCompletion.toFixed(2)}
                      </span>
                    </td>
                    <td>
                      <span className={scoreClass(row.efficiency)}>
                        {row.efficiency.toFixed(2)}
                      </span>
                    </td>
                    <td>
                      <span className={scoreClass(row.security)}>
                        {row.security.toFixed(2)}
                      </span>
                    </td>
                    <td>
                      <span className={scoreClass(row.skills)}>
                        {row.skills.toFixed(2)}
                      </span>
                    </td>
                    <td>
                      <span className={scoreClass(row.ux)}>
                        {row.ux.toFixed(2)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
