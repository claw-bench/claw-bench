"use client";

import { useI18n } from "../i18n";

/* ── Foundation domains ── */
const foundationDomainKeys: Record<string, string> = {
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

/* ── Subject-matter domains ── */
const subjectDomainKeys: Record<string, string> = {
  "Financial Analysis": "domains.financialAnalysis",
  Accounting: "domains.accounting",
  "Market Research": "domains.marketResearch",
  "Contract Review": "domains.contractReview",
  "Regulatory Compliance": "domains.regulatoryCompliance",
  "Clinical Data": "domains.clinicalData",
  Bioinformatics: "domains.bioinformatics",
  "CS & Engineering": "domains.csEngineering",
  "Data Science": "domains.dataScienceDomain",
  "Scientific Computing": "domains.scientificComputing",
  "Academic Research": "domains.academicResearch",
  "Content Analysis": "domains.contentAnalysis",
  "Educational Assessment": "domains.educationalAssessment",
};

const allDomainKeys: Record<string, string> = {
  ...foundationDomainKeys,
  ...subjectDomainKeys,
};

/* ── Subject category grouping ── */
const SUBJECT_CATEGORIES: Record<string, string[]> = {
  "STEM": ["CS & Engineering", "Data Science", "Scientific Computing"],
  "Business & Finance": ["Financial Analysis", "Accounting", "Market Research"],
  "Law & Compliance": ["Contract Review", "Regulatory Compliance"],
  "Healthcare": ["Clinical Data", "Bioinformatics"],
  "Humanities & Education": ["Academic Research", "Content Analysis", "Educational Assessment"],
};

interface DomainData {
  id: string;
  name: string;
  tasks: number;
  l1: number;
  l2: number;
  l3: number;
  l4: number;
  track?: string;
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

function DomainTable({ domains, title, accent, t }: {
  domains: DomainData[];
  title: string;
  accent: string;
  t: (key: string, vars?: Record<string, string | number>) => string;
}) {
  const totals = domains.reduce(
    (acc, d) => ({
      tasks: acc.tasks + d.tasks,
      l1: acc.l1 + d.l1,
      l2: acc.l2 + d.l2,
      l3: acc.l3 + d.l3,
      l4: acc.l4 + d.l4,
    }),
    { tasks: 0, l1: 0, l2: 0, l3: 0, l4: 0 }
  );

  return (
    <div style={{ marginBottom: "2rem" }}>
      <div style={{
        display: "flex", alignItems: "center", gap: "0.6rem",
        marginBottom: "0.75rem",
      }}>
        <div style={{
          width: "4px", height: "1.4rem", borderRadius: "2px",
          background: accent,
        }} />
        <h2 style={{ fontSize: "1.05rem", fontWeight: 600 }}>{title}</h2>
        <span style={{
          fontSize: "0.72rem", padding: "0.15rem 0.5rem",
          background: `${accent}20`, color: accent,
          borderRadius: "12px", fontWeight: 600,
        }}>
          {totals.tasks} {t("common.tasks")}
        </span>
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
                  <td style={{ fontWeight: 600 }}>{t(allDomainKeys[d.name] ?? d.name)}</td>
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
    </div>
  );
}

export default function DomainsContent({ domains, totals }: DomainsContentProps) {
  const { t } = useI18n();

  // Separate foundation and subject-matter domains
  const subjectDomainNames = new Set(Object.keys(subjectDomainKeys));
  const foundationDomains = domains.filter((d) => !subjectDomainNames.has(d.name));
  const subjectDomains = domains.filter((d) => subjectDomainNames.has(d.name));

  const foundationTotal = foundationDomains.reduce((s, d) => s + d.tasks, 0);
  const subjectTotal = subjectDomains.reduce((s, d) => s + d.tasks, 0);

  const stats = [
    { labelKey: "domains.totalTasks", value: totals.tasks, color: "var(--accent)" },
    { labelKey: "dualtrack.foundationTasks", value: foundationTotal, color: "#3b82f6" },
    { labelKey: "dualtrack.subjectTasks", value: subjectTotal, color: "#8b5cf6" },
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

      {/* Dual-track scoring banner */}
      <div
        style={{
          margin: "0 0 1.5rem",
          padding: "1rem 1.25rem",
          background: "var(--accent-light)",
          border: "1px solid var(--accent)",
          borderRadius: "var(--radius)",
          fontSize: "0.82rem",
          color: "var(--text-secondary)",
          lineHeight: 1.6,
        }}
      >
        <strong style={{ color: "var(--accent)" }}>{t("dualtrack.scoringModel")}</strong>{" "}
        {t("dualtrack.scoringModelDesc")}
      </div>

      {/* Stats cards */}
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
              flex: "1 1 120px",
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
                fontSize: "0.72rem",
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

      {/* Foundation Track Table */}
      <DomainTable
        domains={foundationDomains}
        title={t("dualtrack.foundationTrack")}
        accent="#3b82f6"
        t={t}
      />

      {/* Subject-Matter Track Table */}
      {subjectDomains.length > 0 && (
        <DomainTable
          domains={subjectDomains}
          title={t("dualtrack.subjectTrack")}
          accent="#8b5cf6"
          t={t}
        />
      )}

      {/* Subject category breakdown */}
      {subjectDomains.length > 0 && (
        <div style={{ marginBottom: "2rem" }}>
          <h3 style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "0.75rem" }}>
            {t("dualtrack.categoryBreakdown")}
          </h3>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
            {Object.entries(SUBJECT_CATEGORIES).map(([cat, domNames]) => {
              const catDomains = subjectDomains.filter((d) => domNames.includes(d.name));
              const catTotal = catDomains.reduce((s, d) => s + d.tasks, 0);
              return (
                <div key={cat} className="card" style={{ flex: "1 1 200px", padding: "1rem" }}>
                  <div style={{ fontWeight: 600, fontSize: "0.85rem", marginBottom: "0.5rem" }}>{cat}</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginBottom: "0.5rem" }}>
                    {catTotal} {t("common.tasks")}
                  </div>
                  {catDomains.map((d) => (
                    <div key={d.id} style={{
                      display: "flex", justifyContent: "space-between", alignItems: "center",
                      padding: "0.25rem 0", borderBottom: "1px solid var(--border)",
                      fontSize: "0.78rem",
                    }}>
                      <span>{t(allDomainKeys[d.name] ?? d.name)}</span>
                      <span style={{ fontFamily: "var(--font-mono)", fontWeight: 500 }}>{d.tasks}</span>
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        </div>
      )}

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
