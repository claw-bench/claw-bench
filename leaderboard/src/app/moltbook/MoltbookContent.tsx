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
}

interface MoltBookData {
  clawId: string;
  submitter?: { github_user?: string; display_name?: string };
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
  moltbook?: MoltBookData | null;
}

interface MoltbookContentProps {
  byFramework: Record<string, BenchResult[]>;
}

function scoreClass(score: number): string {
  if (score >= 85) return "score score-high";
  if (score >= 70) return "score score-mid";
  return "score score-low";
}

export default function MoltbookContent({ byFramework }: MoltbookContentProps) {
  const { t } = useI18n();

  const [liveByFramework, setLiveByFramework] = useState<Record<string, BenchResult[]> | null>(null);
  useEffect(() => {
    fetch("/api/leaderboard")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d && Array.isArray(d) && d.length > 0) {
          const grouped: Record<string, BenchResult[]> = {};
          for (const entry of d) {
            (grouped[entry.framework] ??= []).push(entry);
          }
          setLiveByFramework(grouped);
        }
      })
      .catch(() => {});
  }, []);
  const activeByFramework = liveByFramework || byFramework;

  return (
    <>
      <header className="page-header">
        <h1>{t("moltbook.title")}</h1>
        <p>{t("moltbook.subtitle")}</p>
        <div style={{ marginTop: "1rem", display: "flex", gap: "0.75rem" }}>
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
            {t("moltbook.backToLeaderboard")}
          </a>
        </div>
      </header>

      <section style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>
          {t("moltbook.howItWorks")}
        </h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1rem",
            marginBottom: "2rem",
          }}
        >
          {[
            { step: "1", titleKey: "moltbook.step1", descKey: "moltbook.step1Desc" },
            { step: "2", titleKey: "moltbook.step2", descKey: "moltbook.step2Desc" },
            { step: "3", titleKey: "moltbook.step3", descKey: "moltbook.step3Desc" },
            { step: "4", titleKey: "moltbook.step4", descKey: "moltbook.step4Desc" },
          ].map((item) => (
            <div
              key={item.step}
              className="card"
              style={{ padding: "1rem", textAlign: "center" }}
            >
              <div
                style={{
                  fontSize: "1.5rem",
                  fontWeight: 700,
                  color: "var(--accent)",
                  marginBottom: "0.25rem",
                }}
              >
                {item.step}
              </div>
              <div style={{ fontWeight: 600, marginBottom: "0.25rem" }}>
                {t(item.titleKey)}
              </div>
              <div
                style={{
                  fontSize: "0.75rem",
                  color: "var(--text-secondary)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {t(item.descKey)}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
          {t("moltbook.registeredAgents")}
        </h2>

        {Object.entries(activeByFramework)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([framework, entries]) => (
            <div
              key={framework}
              className="card"
              style={{
                marginBottom: "1.5rem",
                padding: "1rem",
                overflow: "hidden",
              }}
            >
              <h3 style={{ fontSize: "1rem", marginBottom: "0.75rem" }}>
                {framework}
              </h3>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>{t("moltbook.clawId")}</th>
                      <th>{t("common.agent")}</th>
                      <th>{t("moltbook.submitter")}</th>
                      <th>{t("moltbook.modelTier")}</th>
                      <th>{t("common.overall")}</th>
                      <th>{t("common.tier")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {entries
                      .sort((a, b) => b.overall - a.overall)
                      .map((row, idx) => {
                        const clawId =
                          row.moltbook?.clawId ??
                          row.agentProfile?.profileId?.slice(0, 12) ??
                          `anon-${idx}`;
                        const submitter =
                          row.moltbook?.submitter?.github_user ??
                          row.moltbook?.submitter?.display_name ??
                          "-";
                        return (
                          <tr key={`${framework}-${idx}`}>
                            <td>
                              <code
                                style={{
                                  fontSize: "0.8rem",
                                  fontFamily: "var(--font-mono)",
                                  fontWeight: 600,
                                  color: "var(--accent)",
                                }}
                              >
                                {clawId}
                              </code>
                            </td>
                            <td>
                              {row.agentProfile?.displayName ??
                                `${row.framework} / ${row.model}`}
                            </td>
                            <td>{submitter}</td>
                            <td>
                              {row.agentProfile?.modelTier ?? "-"}
                            </td>
                            <td>
                              <span className={scoreClass(row.overall)}>
                                {row.overall.toFixed(2)}
                              </span>
                            </td>
                            <td>
                              <code
                                style={{
                                  fontSize: "0.75rem",
                                  background: "var(--bg-secondary)",
                                  padding: "0.1rem 0.3rem",
                                  borderRadius: "3px",
                                }}
                              >
                                {row.testTier ?? "-"}
                              </code>
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

      <footer
        style={{
          marginTop: "3rem",
          paddingBottom: "2rem",
          textAlign: "center",
          fontSize: "0.8rem",
          color: "var(--text-secondary)",
        }}
      >
        {t("moltbook.footer")}{" "}
        <code style={{ fontFamily: "var(--font-mono)" }}>
          claw-bench moltbook register --claw-id my-agent --model my-model
        </code>
      </footer>
    </>
  );
}
