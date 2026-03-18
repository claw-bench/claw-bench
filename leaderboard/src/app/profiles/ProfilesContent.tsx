"use client";

import { useEffect, useState } from "react";
import { useI18n } from "../i18n";

interface AgentProfileData {
  profileId: string;
  displayName: string;
  model: string;
  framework: string;
  skillsMode: string;
  skills: string[];
  mcpServers: string[];
  memoryModules: string[];
  modelTier: string | null;
  tags: Record<string, string>;
}

interface ProgressiveData {
  baseline_pass_rate: number;
  current_pass_rate: number;
  absolute_gain: number;
  normalized_gain: number;
  gain_by_domain?: Record<
    string,
    { baseline: number; current: number; gain: number }
  >;
}

interface BenchResult {
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
}

interface ProfilesContentProps {
  byModel: Record<string, BenchResult[]>;
  byFramework: Record<string, BenchResult[]>;
}

function scoreClass(score: number): string {
  if (score >= 85) return "score score-high";
  if (score >= 70) return "score score-mid";
  return "score score-low";
}

export default function ProfilesContent({ byModel, byFramework }: ProfilesContentProps) {
  const { t } = useI18n();

  const [liveData, setLiveData] = useState<{ byModel: Record<string, BenchResult[]>; byFramework: Record<string, BenchResult[]> } | null>(null);
  useEffect(() => {
    fetch("/api/leaderboard")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d && Array.isArray(d) && d.length > 0) {
          const gModel: Record<string, BenchResult[]> = {};
          const gFw: Record<string, BenchResult[]> = {};
          for (const entry of d) {
            (gModel[entry.model] ??= []).push(entry);
            (gFw[entry.framework] ??= []).push(entry);
          }
          setLiveData({ byModel: gModel, byFramework: gFw });
        }
      })
      .catch(() => {});
  }, []);
  const activeByModel = liveData?.byModel || byModel;
  const activeByFramework = liveData?.byFramework || byFramework;

  return (
    <>
      <header className="page-header">
        <h1>{t("profiles.title")}</h1>
        <p>{t("profiles.subtitle")}</p>
        <div style={{ marginTop: "1rem" }}>
          <a
            href="/"
            style={{
              display: "inline-block",
              padding: "0.5rem 1.25rem",
              border: "1px solid var(--border)",
              borderRadius: "6px",
              textDecoration: "none",
              fontWeight: 600,
              fontSize: "0.9rem",
              color: "var(--text-primary)",
            }}
          >
            {t("profiles.backToLeaderboard")}
          </a>
        </div>
      </header>

      {/* Group by Model */}
      <section style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>
          {t("profiles.byModel")}
        </h2>
        <p
          style={{
            fontSize: "0.85rem",
            color: "var(--text-secondary)",
            marginBottom: "1rem",
          }}
        >
          {t("profiles.byModelDesc")}
        </p>

        {Object.entries(activeByModel)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([model, entries]) => (
            <div
              key={model}
              className="card"
              style={{ marginBottom: "1.5rem", padding: "1rem", overflow: "hidden" }}
            >
              <h3
                style={{
                  fontSize: "1rem",
                  marginBottom: "0.75rem",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {model}
              </h3>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>{t("common.agent")}</th>
                      <th>{t("profiles.skillsMode")}</th>
                      <th>{t("profiles.mcp")}</th>
                      <th>{t("table.overall")}</th>
                      <th>{t("table.gain")}</th>
                      <th>{t("table.taskCompletion")}</th>
                      <th>{t("table.efficiency")}</th>
                      <th>{t("table.security")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {entries
                      .sort((a, b) => b.overall - a.overall)
                      .map((row, idx) => {
                        const displayName =
                          row.agentProfile?.displayName ??
                          `${row.framework} / ${row.model}`;
                        const gain = row.progressive?.absolute_gain;
                        const mcpCount =
                          row.agentProfile?.mcpServers?.length ?? 0;
                        return (
                          <tr key={`${model}-${idx}`}>
                            <td style={{ fontWeight: 600 }}>{displayName}</td>
                            <td>
                              <code
                                style={{
                                  fontSize: "0.75rem",
                                  background: "var(--bg-secondary)",
                                  padding: "0.1rem 0.3rem",
                                  borderRadius: "3px",
                                }}
                              >
                                {row.agentProfile?.skillsMode ?? "vanilla"}
                              </code>
                            </td>
                            <td>{mcpCount > 0 ? mcpCount : "-"}</td>
                            <td>
                              <span className={scoreClass(row.overall)}>
                                {row.overall.toFixed(2)}
                              </span>
                            </td>
                            <td>
                              {gain != null ? (
                                <span
                                  style={{
                                    color:
                                      gain >= 0
                                        ? "var(--color-green, #22c55e)"
                                        : "var(--color-red, #ef4444)",
                                    fontWeight: 600,
                                  }}
                                >
                                  {gain >= 0 ? "+" : ""}
                                  {(gain * 100).toFixed(2)}%
                                </span>
                              ) : (
                                <span
                                  style={{
                                    color: "var(--text-secondary)",
                                    fontSize: "0.8rem",
                                  }}
                                >
                                  {t("profiles.baseline")}
                                </span>
                              )}
                            </td>
                            <td>
                              <span
                                className={scoreClass(row.taskCompletion)}
                              >
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
                          </tr>
                        );
                      })}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
      </section>

      {/* Group by Framework */}
      <section style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>
          {t("profiles.byFramework")}
        </h2>
        <p
          style={{
            fontSize: "0.85rem",
            color: "var(--text-secondary)",
            marginBottom: "1rem",
          }}
        >
          {t("profiles.byFrameworkDesc")}
        </p>

        {Object.entries(activeByFramework)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([framework, entries]) => (
            <div
              key={framework}
              className="card"
              style={{ marginBottom: "1.5rem", padding: "1rem", overflow: "hidden" }}
            >
              <h3 style={{ fontSize: "1rem", marginBottom: "0.75rem" }}>
                {framework}
              </h3>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>{t("common.model")}</th>
                      <th>{t("profiles.skillsMode")}</th>
                      <th>{t("common.tier")}</th>
                      <th>{t("table.overall")}</th>
                      <th>{t("table.taskCompletion")}</th>
                      <th>{t("table.efficiency")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {entries
                      .sort((a, b) => b.overall - a.overall)
                      .map((row, idx) => (
                        <tr key={`${framework}-${idx}`}>
                          <td>
                            <code
                              style={{
                                fontSize: "0.8rem",
                                fontFamily: "var(--font-mono)",
                              }}
                            >
                              {row.model}
                            </code>
                          </td>
                          <td>
                            {row.agentProfile?.skillsMode ?? "vanilla"}
                          </td>
                          <td>{row.testTier ?? "-"}</td>
                          <td>
                            <span className={scoreClass(row.overall)}>
                              {row.overall.toFixed(2)}
                            </span>
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
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
      </section>

      {/* Radar Chart placeholder */}
      <section style={{ marginBottom: "2rem" }}>
        <div
          className="card"
          style={{
            padding: "2rem",
            textAlign: "center",
            color: "var(--text-secondary)",
          }}
        >
          <h3 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>
            {t("profiles.radarChart")}
          </h3>
          <p style={{ fontSize: "0.85rem" }}>
            {t("profiles.radarChartDesc")}
          </p>
        </div>
      </section>

      <footer
        style={{
          marginTop: "3rem",
          paddingBottom: "2rem",
          textAlign: "center",
          fontSize: "0.8rem",
          color: "var(--text-secondary)",
        }}
      >
        {t("profiles.footer")}{" "}
        <code style={{ fontFamily: "var(--font-mono)" }}>data/results/</code>.
      </footer>
    </>
  );
}
