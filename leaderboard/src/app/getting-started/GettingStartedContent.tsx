"use client";

import { useI18n } from "../i18n";
import { useState, useEffect } from "react";

function fillTemplate(s: string, vars: Record<string, string | number>): string {
  return s.replace(/\{(\w+)\}/g, (_, k) => String(vars[k] ?? `{${k}}`));
}

interface DomainInfo {
  id: string;
  name: string;
  tasks: number;
}

const domainI18nKeys: Record<string, string> = {
  calendar: "domains.calendar",
  "code-assistance": "domains.codeAssistance",
  communication: "domains.communication",
  "cross-domain": "domains.crossDomain",
  "data-analysis": "domains.dataAnalysis",
  "document-editing": "domains.documentEditing",
  email: "domains.email",
  "file-operations": "domains.fileOperations",
  memory: "domains.memory",
  "multi-agent": "domains.multiAgent",
  multimodal: "domains.multimodal",
  security: "domains.securityDomain",
  "system-admin": "domains.systemAdmin",
  "web-browsing": "domains.webBrowsing",
  "workflow-automation": "domains.workflowAutomation",
};

export default function GettingStartedContent({ domains }: { domains: DomainInfo[] }) {
  const { t } = useI18n();
  const [stats, setStats] = useState({ totalTasks: 0, totalDomains: 0 });
  useEffect(() => { fetch("/api/stats").then(r => r.json()).then(setStats).catch(() => {}); }, []);
  const vars = { total: stats.totalTasks || "…", domains: stats.totalDomains || "…" };
  return (
    <>
      <header className="page-header">
        <h1>{t("gettingStarted.title")}</h1>
        <p>{fillTemplate(t("gettingStarted.subtitle"), vars)}</p>
      </header>

      <section className="card" style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ marginTop: 0 }}>{t("gettingStarted.step1")}</h2>
        <pre><code>pip install claw-bench</code></pre>
        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
          {t("gettingStarted.step1FromSource")}{" "}
          <code>git clone https://github.com/claw-bench/claw-bench.git && cd claw-bench && pip install -e .</code>
        </p>
      </section>

      <section className="card" style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ marginTop: 0 }}>{t("gettingStarted.step2")}</h2>
        <pre><code>{`export OPENAI_COMPAT_BASE_URL="https://cloud.infini-ai.com/maas/v1"\nexport OPENAI_COMPAT_API_KEY="your-api-key"`}</code></pre>
        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>{t("gettingStarted.step2Desc")}</p>
      </section>

      <section className="card" style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ marginTop: 0 }}>{t("gettingStarted.step3")}</h2>
        <h3>{t("gettingStarted.smokeTest")}</h3>
        <pre><code>claw-bench run -m deepseek-v3 -t file-001,code-002,cal-001,file-003 -n 1</code></pre>
        <h3>{t("gettingStarted.testDomain")}</h3>
        <pre><code>claw-bench run -m gemini-2.5-pro -t code-assistance</code></pre>
        <h3>{fillTemplate(t("gettingStarted.fullBenchmark"), vars)}</h3>
        <pre><code>claw-bench run -m claude-sonnet-4-5-20250929 -t all -n 5</code></pre>
      </section>

      <section className="card" style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ marginTop: 0 }}>{t("gettingStarted.capabilityTests")}</h2>
        <p>{t("gettingStarted.capabilityDesc")}</p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{t("domains.domain")}</th>
                <th>{t("domains.tasks")}</th>
                <th>{t("gettingStarted.command")}</th>
              </tr>
            </thead>
            <tbody>
              {domains.map((d) => (
                <tr key={d.id}>
                  <td style={{ fontWeight: 600 }}>{t(domainI18nKeys[d.id] || d.name)}</td>
                  <td>{d.tasks}</td>
                  <td><code style={{ fontSize: "0.8rem" }}>claw-bench run -m MODEL -t {d.id}</code></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card" style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ marginTop: 0 }}>{t("gettingStarted.forAiAgents")}</h2>
        <p>{t("gettingStarted.forAiAgentsDesc")}</p>
        <pre><code>{`# The skill file contains complete evaluation instructions\n# your AI agent can read and follow:\nhttps://clawbench.net/skill.md`}</code></pre>
        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>{t("gettingStarted.skillMdDesc")}</p>
      </section>

      <footer style={{ marginTop: "3rem", paddingBottom: "2rem", textAlign: "center", fontSize: "0.8rem", color: "var(--text-secondary)" }}>
        {t("gettingStarted.fullDocs")}{" "}
        <a href="https://github.com/claw-bench/claw-bench">github.com/claw-bench/claw-bench</a>
      </footer>
    </>
  );
}
