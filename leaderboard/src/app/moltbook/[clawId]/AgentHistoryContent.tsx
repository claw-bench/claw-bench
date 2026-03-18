"use client";

import { useI18n } from "../../i18n";

interface HistoryEntry {
  date: string;
  tier: string;
  overall: number;
  passRate: number;
}

interface AgentHistoryContentProps {
  clawId: string;
  displayName: string;
  framework: string;
  model: string;
  submitter: string;
  history: HistoryEntry[];
}

function scoreClass(score: number): string {
  if (score >= 85) return "score score-high";
  if (score >= 70) return "score score-mid";
  return "score score-low";
}

export default function AgentHistoryContent({
  clawId,
  displayName,
  framework,
  model,
  submitter,
  history,
}: AgentHistoryContentProps) {
  const { t } = useI18n();

  const best =
    history.length > 0
      ? Math.max(...history.map((h) => h.overall))
      : 0;
  const totalRuns = history.length;

  return (
    <>
      <header className="page-header">
        <h1 style={{ fontFamily: "var(--font-mono)", fontSize: "1.5rem" }}>
          {clawId}
        </h1>
        <p>{displayName}</p>
        <div style={{ marginTop: "1rem", display: "flex", gap: "0.75rem" }}>
          <a
            href="/moltbook"
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
            {t("common.backToMoltbook")}
          </a>
        </div>
      </header>

      {/* Identity card */}
      <section style={{ marginBottom: "2rem" }}>
        <div
          className="card"
          style={{
            padding: "1.25rem",
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "1rem",
          }}
        >
          {[
            { label: t("common.framework"), value: framework },
            { label: t("common.model"), value: model },
            { label: t("moltbook.submitter"), value: `@${submitter}` },
            { label: t("common.totalRuns"), value: String(totalRuns) },
            { label: t("common.bestScore"), value: best.toFixed(2) },
          ].map((item) => (
            <div key={item.label}>
              <div
                style={{
                  fontSize: "0.7rem",
                  fontWeight: 600,
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  color: "var(--text-secondary)",
                  marginBottom: "0.15rem",
                }}
              >
                {item.label}
              </div>
              <div style={{ fontSize: "1.1rem", fontWeight: 600 }}>
                {item.value}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Score progression */}
      <section style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
          {t("common.scoreProgression")}
        </h2>

        <div
          className="card"
          style={{ padding: "1.25rem", overflow: "hidden" }}
        >
          {history.length === 0 ? (
            <p style={{ color: "var(--text-secondary)" }}>
              {t("common.noRuns")}
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {history.map((h, i) => {
                const pct = Math.min(h.overall, 100);
                return (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.75rem",
                    }}
                  >
                    <div
                      style={{
                        width: "5.5rem",
                        fontSize: "0.8rem",
                        fontFamily: "var(--font-mono)",
                        color: "var(--text-secondary)",
                        flexShrink: 0,
                      }}
                    >
                      {h.date}
                    </div>
                    <div
                      style={{
                        flex: 1,
                        height: "1.25rem",
                        background: "var(--bg-secondary)",
                        borderRadius: "4px",
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          width: `${pct}%`,
                          height: "100%",
                          background:
                            h.overall >= 80
                              ? "#22c55e"
                              : h.overall >= 65
                                ? "#eab308"
                                : "#ef4444",
                          borderRadius: "4px",
                          transition: "width 0.3s",
                        }}
                      />
                    </div>
                    <div
                      style={{
                        width: "3rem",
                        textAlign: "right",
                        fontWeight: 600,
                        fontFamily: "var(--font-mono)",
                        fontSize: "0.85rem",
                      }}
                    >
                      {h.overall.toFixed(2)}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* Run history table */}
      <section style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
          {t("common.runHistory")}
        </h2>
        <div
          className="card"
          style={{ padding: 0, overflow: "hidden" }}
        >
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>{t("common.date")}</th>
                  <th>{t("common.tier")}</th>
                  <th>{t("common.overall")}</th>
                  <th>{t("common.passRate")}</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: "var(--font-mono)" }}>
                      {h.date}
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
                        {h.tier}
                      </code>
                    </td>
                    <td>
                      <span className={scoreClass(h.overall)}>
                        {h.overall.toFixed(2)}
                      </span>
                    </td>
                    <td>{(h.passRate * 100).toFixed(0)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
        {t("common.historyFooter", { clawId })}
      </footer>
    </>
  );
}
