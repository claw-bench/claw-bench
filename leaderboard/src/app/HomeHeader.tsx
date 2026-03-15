"use client";

import { useI18n } from "./i18n";
import { useState } from "react";

export function HomeHeader() {
  const { t } = useI18n();
  const skillUrl = "https://clawbench.net/skill.md";
  const commandText = `${t("home.calloutPrefix")} ${skillUrl} ${t("home.calloutSuffix")}${t("home.calloutAction")}`;
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(commandText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <>
      <header className="page-header">
        <h1>{t("home.title")}</h1>
        <p>{t("home.subtitle")}</p>
        <div
          style={{
            marginTop: "1.25rem",
            display: "flex",
            gap: "0.6rem",
            flexWrap: "wrap",
          }}
        >
          <a
            href="/getting-started"
            style={{
              display: "inline-block",
              padding: "0.55rem 1.4rem",
              background: "var(--accent)",
              color: "#fff",
              borderRadius: "6px",
              textDecoration: "none",
              fontWeight: 500,
              fontSize: "0.85rem",
              letterSpacing: "0.01em",
              transition: "background 0.2s",
            }}
          >
            {t("home.runBenchmark")}
          </a>
          <a
            href="/profiles"
            style={{
              display: "inline-block",
              padding: "0.55rem 1.4rem",
              border: "1px solid var(--border)",
              borderRadius: "6px",
              textDecoration: "none",
              fontWeight: 500,
              fontSize: "0.85rem",
              color: "var(--text-secondary)",
              transition: "all 0.2s",
            }}
          >
            {t("home.agentProfiles")}
          </a>
          <a
            href="/skill.md"
            style={{
              display: "inline-block",
              padding: "0.55rem 1.4rem",
              border: "1px solid var(--border)",
              borderRadius: "6px",
              textDecoration: "none",
              fontWeight: 500,
              fontSize: "0.85rem",
              color: "var(--text-secondary)",
              transition: "all 0.2s",
            }}
          >
            {t("home.skillMd")}
          </a>
        </div>
      </header>

      <div
        style={{
          margin: "0 0 2rem",
          padding: "1.2rem 1.5rem",
          background: "var(--accent-light)",
          border: "1px solid var(--accent)",
          borderRadius: "var(--radius)",
        }}
      >
        <p
          style={{
            fontSize: "0.85rem",
            color: "var(--text-secondary)",
            marginBottom: "0.7rem",
            fontWeight: 400,
          }}
        >
          {t("home.callout")}
        </p>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
            flexWrap: "wrap",
          }}
        >
          <code
            style={{
              flex: 1,
              minWidth: 0,
              padding: "0.6rem 1rem",
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "6px",
              fontFamily: "var(--font-mono)",
              fontSize: "0.85rem",
              color: "var(--text)",
              wordBreak: "break-all",
            }}
          >
            {t("home.calloutPrefix")}{" "}
            <a
              href="/skill.md"
              style={{
                color: "var(--accent)",
                fontWeight: 600,
                textDecoration: "underline",
              }}
            >
              {skillUrl}
            </a>{" "}
            {t("home.calloutSuffix")}
            <strong>{t("home.calloutAction")}</strong>
          </code>
          <button
            onClick={handleCopy}
            style={{
              flexShrink: 0,
              padding: "0.5rem 1rem",
              background: copied ? "var(--success)" : "var(--accent)",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              fontWeight: 500,
              fontSize: "0.8rem",
              cursor: "pointer",
              transition: "all 0.2s",
              whiteSpace: "nowrap",
            }}
          >
            {copied ? "✓" : "Copy"}
          </button>
        </div>
      </div>
    </>
  );
}

export function HomeFooter() {
  return (
    <footer
      style={{
        marginTop: "3rem",
        paddingBottom: "2.5rem",
      }}
    />
  );
}
