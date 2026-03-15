"use client";

import { useI18n } from "../i18n";

const domainKeys: Record<string, string> = {
  Calendar: "domains.calendar",
  "Code Assistance": "domains.codeAssistance",
  Communication: "domains.communication",
  "Cross-Domain": "domains.crossDomain",
  "Data Analysis": "domains.dataAnalysis",
  "Document Editing": "domains.documentEditing",
  Email: "domains.email",
  "File Operations": "domains.fileOperations",
  Memory: "domains.memory",
  Multimodal: "domains.multimodal",
  Security: "domains.securityDomain",
  "System Admin": "domains.systemAdmin",
  "Web Browsing": "domains.webBrowsing",
  "Workflow Automation": "domains.workflowAutomation",
};

interface DomainData {
  id: string;
  name: string;
  tasks: number;
  l1: number;
  l2: number;
  l3: number;
  l4: number;
}

interface TotalsData {
  tasks: number;
  l1: number;
  l2: number;
  l3: number;
  l4: number;
}

interface DomainsContentProps {
  domains: DomainData[];
  totals: TotalsData;
}

function difficultyBar(l1: number, l2: number, l3: number, l4: number) {
  const total = l1 + l2 + l3 + l4;
  if (total === 0) return null;
  return (
    <div
      style={{
        display: "flex",
        height: "8px",
        borderRadius: "4px",
        overflow: "hidden",
        width: "100%",
        minWidth: "80px",
      }}
    >
      <div style={{ width: `${(l1 / total) * 100}%`, background: "#22c55e" }} title={`L1: ${l1}`} />
      <div style={{ width: `${(l2 / total) * 100}%`, background: "#eab308" }} title={`L2: ${l2}`} />
      <div style={{ width: `${(l3 / total) * 100}%`, background: "#f97316" }} title={`L3: ${l3}`} />
      <div style={{ width: `${(l4 / total) * 100}%`, background: "#ef4444" }} title={`L4: ${l4}`} />
    </div>
  );
}

export default function DomainsContent({ domains, totals }: DomainsContentProps) {
  const { t } = useI18n();

  const stats = [
    { labelKey: "domains.totalTasks", value: totals.tasks, color: "var(--accent)" },
    { labelKey: "domains.l1", value: totals.l1, color: "#22c55e" },
    { labelKey: "domains.l2", value: totals.l2, color: "#eab308" },
    { labelKey: "domains.l3", value: totals.l3, color: "#f97316" },
    { labelKey: "domains.l4", value: totals.l4, color: "#ef4444" },
  ];

  const legendItems = [
    { labelKey: "domains.l1", color: "#22c55e" },
    { labelKey: "domains.l2", color: "#eab308" },
    { labelKey: "domains.l3", color: "#f97316" },
    { labelKey: "domains.l4", color: "#ef4444" },
  ];

  return (
    <>
      <header className="page-header">
        <h1>{t("domains.title")}</h1>
        <p>{t("domains.subtitle", { total: String(totals.tasks), domains: String(domains.length) })}</p>
      </header>

      <div
        style={{
          display: "flex",
          gap: "1rem",
          marginBottom: "1.5rem",
          flexWrap: "wrap",
        }}
      >
        {stats.map((stat) => (
          <div
            key={stat.labelKey}
            className="card"
            style={{
              flex: "1 1 150px",
              textAlign: "center",
              padding: "1rem",
            }}
          >
            <div
              style={{
                fontSize: "2rem",
                fontWeight: 700,
                fontFamily: "var(--font-mono)",
                color: stat.color,
              }}
            >
              {stat.value}
            </div>
            <div
              style={{
                fontSize: "0.75rem",
                color: "var(--text-secondary)",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                marginTop: "0.25rem",
              }}
            >
              {t(stat.labelKey)}
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{t("domains.domain")}</th>
                <th style={{ textAlign: "right" }}>{t("domains.tasks")}</th>
                <th style={{ textAlign: "right" }}>L1</th>
                <th style={{ textAlign: "right" }}>L2</th>
                <th style={{ textAlign: "right" }}>L3</th>
                <th style={{ textAlign: "right" }}>L4</th>
                <th>{t("domains.difficultyDist")}</th>
              </tr>
            </thead>
            <tbody>
              {domains.map((d) => (
                <tr key={d.id}>
                  <td style={{ fontWeight: 600 }}>{t(domainKeys[d.name] ?? d.name)}</td>
                  <td style={{ textAlign: "right", fontFamily: "var(--font-mono)" }}>{d.tasks}</td>
                  <td style={{ textAlign: "right", fontFamily: "var(--font-mono)", color: "#22c55e" }}>{d.l1}</td>
                  <td style={{ textAlign: "right", fontFamily: "var(--font-mono)", color: "#eab308" }}>{d.l2}</td>
                  <td style={{ textAlign: "right", fontFamily: "var(--font-mono)", color: "#f97316" }}>{d.l3}</td>
                  <td style={{ textAlign: "right", fontFamily: "var(--font-mono)", color: "#ef4444" }}>{d.l4}</td>
                  <td>{difficultyBar(d.l1, d.l2, d.l3, d.l4)}</td>
                </tr>
              ))}
              <tr style={{ fontWeight: 700 }}>
                <td>{t("domains.total")}</td>
                <td style={{ textAlign: "right", fontFamily: "var(--font-mono)" }}>{totals.tasks}</td>
                <td style={{ textAlign: "right", fontFamily: "var(--font-mono)" }}>{totals.l1}</td>
                <td style={{ textAlign: "right", fontFamily: "var(--font-mono)" }}>{totals.l2}</td>
                <td style={{ textAlign: "right", fontFamily: "var(--font-mono)" }}>{totals.l3}</td>
                <td style={{ textAlign: "right", fontFamily: "var(--font-mono)" }}>{totals.l4}</td>
                <td>{difficultyBar(totals.l1, totals.l2, totals.l3, totals.l4)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div
        style={{
          marginTop: "1.5rem",
          display: "flex",
          gap: "0.5rem",
          fontSize: "0.75rem",
          color: "var(--text-secondary)",
          alignItems: "center",
        }}
      >
        <span>{t("domains.difficultyLegend")}</span>
        {legendItems.map((l) => (
          <span key={l.labelKey} style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
            <span
              style={{
                display: "inline-block",
                width: "10px",
                height: "10px",
                borderRadius: "2px",
                background: l.color,
              }}
            />
            {t(l.labelKey)}
          </span>
        ))}
      </div>
    </>
  );
}
