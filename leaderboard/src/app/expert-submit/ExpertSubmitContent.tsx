"use client";

import { useState, useCallback } from "react";
import { useI18n } from "../i18n";

/* ── Constants ──────────────────────────────────────────────────── */

const DOMAINS = [
  { value: "computer-science", label: "STEM: Computer Science", labelZh: "STEM：计算机科学" },
  { value: "mathematics", label: "STEM: Mathematics", labelZh: "STEM：数学" },
  { value: "physics-engineering", label: "STEM: Physics / Engineering", labelZh: "STEM：物理/工程" },
  { value: "biology-chemistry", label: "STEM: Biology / Chemistry", labelZh: "STEM：生物/化学" },
  { value: "financial-analysis", label: "Business: Financial Analysis", labelZh: "商业：金融分析" },
  { value: "accounting", label: "Business: Accounting", labelZh: "商业：会计" },
  { value: "marketing", label: "Business: Marketing", labelZh: "商业：市场营销" },
  { value: "contract-review", label: "Law: Contract Review", labelZh: "法律：合同审查" },
  { value: "legal-research", label: "Law: Legal Research", labelZh: "法律：法律研究" },
  { value: "clinical-data", label: "Healthcare: Clinical Data", labelZh: "医疗：临床数据" },
  { value: "medical-research", label: "Healthcare: Medical Research", labelZh: "医疗：医学研究" },
  { value: "sociology", label: "Humanities: Sociology", labelZh: "人文：社会学" },
  { value: "education", label: "Humanities: Education", labelZh: "人文：教育" },
];

const DIFFICULTY_LEVELS = [
  { value: "L1", label: "L1 - Basic (single-step, straightforward)", labelZh: "L1 - 基础（单步骤，直接操作）" },
  { value: "L2", label: "L2 - Intermediate (multi-step, some judgment)", labelZh: "L2 - 中等（多步骤，需要判断）" },
  { value: "L3", label: "L3 - Advanced (complex reasoning, multiple tools)", labelZh: "L3 - 高级（复杂推理，多工具）" },
  { value: "L4", label: "L4 - Expert (requires deep domain expertise)", labelZh: "L4 - 专家（需要深度领域知识）" },
];

const AGENT_ACTIONS = [
  { value: "api-call", label: "API Call", labelZh: "API 调用" },
  { value: "file-read", label: "File Read", labelZh: "文件读取" },
  { value: "file-write", label: "File Write", labelZh: "文件写入" },
  { value: "file-move", label: "File Move / Rename", labelZh: "文件移动/重命名" },
  { value: "database-query", label: "Database Query", labelZh: "数据库查询" },
  { value: "database-write", label: "Database Write", labelZh: "数据库写入" },
  { value: "script-execution", label: "Script Execution", labelZh: "脚本执行" },
  { value: "environment-setup", label: "Environment Setup", labelZh: "环境配置" },
  { value: "web-navigation", label: "Web Navigation", labelZh: "网页导航" },
  { value: "web-scraping", label: "Web Scraping", labelZh: "网页抓取" },
  { value: "git-operation", label: "Git Operation", labelZh: "Git 操作" },
  { value: "email-send", label: "Email Send", labelZh: "邮件发送" },
  { value: "document-conversion", label: "Document Conversion", labelZh: "文档转换" },
  { value: "data-visualization", label: "Data Visualization", labelZh: "数据可视化" },
  { value: "command-line-tool", label: "Command Line Tool", labelZh: "命令行工具" },
  { value: "package-install", label: "Package Install", labelZh: "软件包安装" },
];

const API_BASE = "/api/admin";

/* ── Translations ───────────────────────────────────────────────── */

const T = {
  en: {
    title: "Expert Task Submission",
    subtitle: "Submit a real-world professional task for Claw-Bench. No coding required — just describe the task and we handle the rest.",
    passwordLabel: "Access Password",
    passwordPlaceholder: "Enter expert access password",
    unlock: "Unlock",
    wrongPassword: "Incorrect password. Please try again.",
    notConfigured: "Expert password not configured on server. Please set EXPERT_PASSWORD environment variable.",
    connectionFailed: "Connection failed. Please check if the server is running.",
    formTitle: "Task Proposal Form",
    domainLabel: "Professional Domain",
    domainPlaceholder: "Select a domain...",
    taskTitleLabel: "Task Title",
    taskTitlePlaceholder: "e.g., Automate monthly bank reconciliation from CSV exports",
    difficultyLabel: "Estimated Difficulty",
    difficultyPlaceholder: "Select difficulty...",
    contextLabel: "Real-world Context",
    contextPlaceholder: "Why is this task important in your industry? What business value does it provide?",
    instructionLabel: "Agent Instruction",
    instructionPlaceholder: "What exact instruction should we give to the AI Agent? Write it as if delegating to a new hire.",
    actionsLabel: "Required Agent Actions (select all that apply)",
    actionsHint: "The agent must perform these concrete operations — not just answer questions.",
    criteriaLabel: "Success Criteria",
    criteriaPlaceholder: "How would you verify the agent did a good job? Be as specific as possible (exact values, file formats, field names).",
    dataLabel: "Data & Resources (optional)",
    dataPlaceholder: "What files, tools, or data does the agent need? Describe what kind of data is needed.",
    expertNameLabel: "Your Name (optional)",
    expertNamePlaceholder: "e.g., Dr. Jane Smith",
    expertEmailLabel: "Your Email (optional)",
    expertEmailPlaceholder: "e.g., jane@example.com",
    submit: "Submit Task Proposal",
    submitting: "Submitting...",
    successTitle: "Task Proposal Submitted!",
    successMessage: "Thank you for your contribution! Our team will review your proposal and convert it into a benchmark task. You will be credited as a co-author.",
    submitAnother: "Submit Another Task",
    errorTitle: "Submission Failed",
    requiredField: "This field is required",
    actionsRequired: "Please select at least one agent action",
  },
  zh: {
    title: "专家任务提交",
    subtitle: "为 Claw-Bench 提交真实的专业领域任务。无需编写代码 — 只需描述任务，我们处理其余部分。",
    passwordLabel: "访问密码",
    passwordPlaceholder: "请输入专家访问密码",
    unlock: "解锁",
    wrongPassword: "密码错误，请重试。",
    notConfigured: "服务器未配置专家密码。请设置 EXPERT_PASSWORD 环境变量。",
    connectionFailed: "连接失败，请检查服务器是否运行。",
    formTitle: "任务提案表单",
    domainLabel: "专业领域",
    domainPlaceholder: "选择领域...",
    taskTitleLabel: "任务标题",
    taskTitlePlaceholder: "例如：从 CSV 导出自动完成月度银行对账",
    difficultyLabel: "预估难度",
    difficultyPlaceholder: "选择难度...",
    contextLabel: "真实场景",
    contextPlaceholder: "为什么这个任务在你的行业中很重要？它提供什么商业价值？",
    instructionLabel: "Agent 指令",
    instructionPlaceholder: "你会给 AI Agent 下达什么具体指令？像给新员工布置任务一样写。",
    actionsLabel: "必需的 Agent 操作（选择所有适用的）",
    actionsHint: "Agent 必须执行这些具体操作 — 而不仅仅是回答问题。",
    criteriaLabel: "成功标准",
    criteriaPlaceholder: "你会如何验证 Agent 做得对不对？请尽量具体（精确数值、文件格式、字段名等）。",
    dataLabel: "数据与资源（可选）",
    dataPlaceholder: "Agent 需要哪些文件、工具或数据？描述需要什么样的数据。",
    expertNameLabel: "您的姓名（可选）",
    expertNamePlaceholder: "例如：张教授",
    expertEmailLabel: "您的邮箱（可选）",
    expertEmailPlaceholder: "例如：zhang@example.com",
    submit: "提交任务提案",
    submitting: "提交中...",
    successTitle: "任务提案已提交！",
    successMessage: "感谢您的贡献！我们的团队将审核您的提案并将其转化为评测任务。您将被列为任务的联合创作者。",
    submitAnother: "提交另一个任务",
    errorTitle: "提交失败",
    requiredField: "此字段为必填项",
    actionsRequired: "请至少选择一个 Agent 操作",
  },
};

/* ── Component ──────────────────────────────────────────────────── */

interface FormData {
  domain: string;
  taskTitle: string;
  difficulty: string;
  context: string;
  instruction: string;
  requiredActions: string[];
  successCriteria: string;
  dataRequirements: string;
  expertName: string;
  expertEmail: string;
}

const emptyForm: FormData = {
  domain: "",
  taskTitle: "",
  difficulty: "",
  context: "",
  instruction: "",
  requiredActions: [],
  successCriteria: "",
  dataRequirements: "",
  expertName: "",
  expertEmail: "",
};

export default function ExpertSubmitContent() {
  const { lang } = useI18n();
  const t = T[lang] || T.en;

  const [password, setPassword] = useState("");
  const [token, setToken] = useState<string | null>(null);
  const [loginError, setLoginError] = useState("");
  const [form, setForm] = useState<FormData>({ ...emptyForm });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState("");

  /* ── Auth ── */
  const login = useCallback(async () => {
    setLoginError("");
    try {
      const res = await fetch(`${API_BASE}/expert-login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      if (res.status === 503) {
        setLoginError(t.notConfigured);
        return;
      }
      if (!res.ok) {
        setLoginError(t.wrongPassword);
        return;
      }
      const data = await res.json();
      setToken(data.token);
      sessionStorage.setItem("expert_token", data.token);
    } catch {
      setLoginError(t.connectionFailed);
    }
  }, [password, t]);

  /* ── Form helpers ── */
  const updateField = (field: keyof FormData, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: "" }));
  };

  const toggleAction = (action: string) => {
    setForm((prev) => {
      const actions = prev.requiredActions.includes(action)
        ? prev.requiredActions.filter((a) => a !== action)
        : [...prev.requiredActions, action];
      return { ...prev, requiredActions: actions };
    });
    setErrors((prev) => ({ ...prev, requiredActions: "" }));
  };

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.domain) errs.domain = t.requiredField;
    if (!form.taskTitle.trim()) errs.taskTitle = t.requiredField;
    if (!form.difficulty) errs.difficulty = t.requiredField;
    if (!form.context.trim()) errs.context = t.requiredField;
    if (!form.instruction.trim()) errs.instruction = t.requiredField;
    if (form.requiredActions.length === 0) errs.requiredActions = t.actionsRequired;
    if (!form.successCriteria.trim()) errs.successCriteria = t.requiredField;
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  /* ── Submit ── */
  const handleSubmit = useCallback(async () => {
    if (!validate()) return;
    setSubmitting(true);
    setSubmitError("");
    try {
      const res = await fetch(`${API_BASE}/expert-proposals`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setSubmitError(data.detail || `Error ${res.status}`);
        return;
      }
      setSubmitted(true);
    } catch {
      setSubmitError(t.connectionFailed);
    } finally {
      setSubmitting(false);
    }
  }, [form, token, t]);

  /* ── Styles ── */
  const inputStyle: React.CSSProperties = {
    width: "100%",
    padding: "0.6rem 0.8rem",
    border: "1px solid var(--border)",
    borderRadius: "6px",
    fontSize: "0.88rem",
    background: "var(--bg)",
    color: "var(--text)",
    fontFamily: "var(--font-sans)",
  };

  const textareaStyle: React.CSSProperties = {
    ...inputStyle,
    minHeight: "120px",
    resize: "vertical",
    lineHeight: 1.6,
  };

  const labelStyle: React.CSSProperties = {
    display: "block",
    fontSize: "0.82rem",
    fontWeight: 600,
    color: "var(--text)",
    marginBottom: "0.35rem",
  };

  const errorStyle: React.CSSProperties = {
    fontSize: "0.75rem",
    color: "var(--danger)",
    marginTop: "0.25rem",
  };

  const fieldGroup: React.CSSProperties = {
    marginBottom: "1.5rem",
  };

  /* ── Login screen ── */
  if (!token) {
    return (
      <>
        <div className="page-header">
          <h1>{t.title}</h1>
          <p>{t.subtitle}</p>
        </div>
        <div style={{ maxWidth: 400, margin: "3rem auto" }}>
          <div className="card" style={{ padding: "2rem" }}>
            <label style={labelStyle}>{t.passwordLabel}</label>
            <input
              type="password"
              value={password}
              onChange={(e) => { setPassword(e.target.value); setLoginError(""); }}
              onKeyDown={(e) => e.key === "Enter" && login()}
              placeholder={t.passwordPlaceholder}
              style={{ ...inputStyle, marginBottom: "0.75rem" }}
            />
            {loginError && <p style={{ ...errorStyle, marginBottom: "0.75rem" }}>{loginError}</p>}
            <button
              onClick={login}
              style={{
                width: "100%",
                padding: "0.65rem",
                background: "var(--accent)",
                color: "#fff",
                border: "none",
                borderRadius: "6px",
                fontWeight: 600,
                fontSize: "0.88rem",
                cursor: "pointer",
              }}
            >
              {t.unlock}
            </button>
          </div>
        </div>
      </>
    );
  }

  /* ── Success screen ── */
  if (submitted) {
    return (
      <>
        <div className="page-header">
          <h1>{t.title}</h1>
          <p>{t.subtitle}</p>
        </div>
        <div style={{ maxWidth: 600, margin: "3rem auto", textAlign: "center" }}>
          <div className="card" style={{ padding: "2.5rem" }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>&#10003;</div>
            <h2 style={{ fontSize: "1.3rem", fontWeight: 600, marginBottom: "0.75rem" }}>{t.successTitle}</h2>
            <p style={{ color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "1.5rem" }}>{t.successMessage}</p>
            <button
              onClick={() => { setSubmitted(false); setForm({ ...emptyForm }); }}
              style={{
                padding: "0.6rem 1.5rem",
                background: "var(--accent)",
                color: "#fff",
                border: "none",
                borderRadius: "6px",
                fontWeight: 500,
                fontSize: "0.88rem",
                cursor: "pointer",
              }}
            >
              {t.submitAnother}
            </button>
          </div>
        </div>
      </>
    );
  }

  /* ── Form ── */
  return (
    <>
      <div className="page-header">
        <h1>{t.title}</h1>
        <p>{t.subtitle}</p>
      </div>

      <div style={{ maxWidth: 720, margin: "0 auto 3rem" }}>
        <div className="card" style={{ padding: "2rem" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "1.5rem", paddingBottom: "0.75rem", borderBottom: "1px solid var(--border)" }}>
            {t.formTitle}
          </h2>

          {/* Domain */}
          <div style={fieldGroup}>
            <label style={labelStyle}>{t.domainLabel} *</label>
            <select
              value={form.domain}
              onChange={(e) => updateField("domain", e.target.value)}
              style={{ ...inputStyle, cursor: "pointer" }}
            >
              <option value="">{t.domainPlaceholder}</option>
              {DOMAINS.map((d) => (
                <option key={d.value} value={d.value}>
                  {lang === "zh" ? d.labelZh : d.label}
                </option>
              ))}
            </select>
            {errors.domain && <p style={errorStyle}>{errors.domain}</p>}
          </div>

          {/* Task Title */}
          <div style={fieldGroup}>
            <label style={labelStyle}>{t.taskTitleLabel} *</label>
            <input
              type="text"
              value={form.taskTitle}
              onChange={(e) => updateField("taskTitle", e.target.value)}
              placeholder={t.taskTitlePlaceholder}
              style={inputStyle}
            />
            {errors.taskTitle && <p style={errorStyle}>{errors.taskTitle}</p>}
          </div>

          {/* Difficulty */}
          <div style={fieldGroup}>
            <label style={labelStyle}>{t.difficultyLabel} *</label>
            <select
              value={form.difficulty}
              onChange={(e) => updateField("difficulty", e.target.value)}
              style={{ ...inputStyle, cursor: "pointer" }}
            >
              <option value="">{t.difficultyPlaceholder}</option>
              {DIFFICULTY_LEVELS.map((d) => (
                <option key={d.value} value={d.value}>
                  {lang === "zh" ? d.labelZh : d.label}
                </option>
              ))}
            </select>
            {errors.difficulty && <p style={errorStyle}>{errors.difficulty}</p>}
          </div>

          {/* Context */}
          <div style={fieldGroup}>
            <label style={labelStyle}>{t.contextLabel} *</label>
            <textarea
              value={form.context}
              onChange={(e) => updateField("context", e.target.value)}
              placeholder={t.contextPlaceholder}
              style={textareaStyle}
            />
            {errors.context && <p style={errorStyle}>{errors.context}</p>}
          </div>

          {/* Instruction */}
          <div style={fieldGroup}>
            <label style={labelStyle}>{t.instructionLabel} *</label>
            <textarea
              value={form.instruction}
              onChange={(e) => updateField("instruction", e.target.value)}
              placeholder={t.instructionPlaceholder}
              style={{ ...textareaStyle, minHeight: "160px" }}
            />
            {errors.instruction && <p style={errorStyle}>{errors.instruction}</p>}
          </div>

          {/* Required Actions */}
          <div style={fieldGroup}>
            <label style={labelStyle}>{t.actionsLabel} *</label>
            <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginBottom: "0.75rem" }}>{t.actionsHint}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
              {AGENT_ACTIONS.map((action) => {
                const selected = form.requiredActions.includes(action.value);
                return (
                  <button
                    key={action.value}
                    type="button"
                    onClick={() => toggleAction(action.value)}
                    style={{
                      padding: "0.35rem 0.75rem",
                      border: `1px solid ${selected ? "var(--accent)" : "var(--border)"}`,
                      borderRadius: "20px",
                      background: selected ? "var(--accent-light)" : "transparent",
                      color: selected ? "var(--accent)" : "var(--text-secondary)",
                      fontSize: "0.78rem",
                      fontWeight: selected ? 600 : 400,
                      cursor: "pointer",
                      transition: "all 0.15s",
                    }}
                  >
                    {lang === "zh" ? action.labelZh : action.label}
                  </button>
                );
              })}
            </div>
            {errors.requiredActions && <p style={errorStyle}>{errors.requiredActions}</p>}
          </div>

          {/* Success Criteria */}
          <div style={fieldGroup}>
            <label style={labelStyle}>{t.criteriaLabel} *</label>
            <textarea
              value={form.successCriteria}
              onChange={(e) => updateField("successCriteria", e.target.value)}
              placeholder={t.criteriaPlaceholder}
              style={{ ...textareaStyle, minHeight: "140px" }}
            />
            {errors.successCriteria && <p style={errorStyle}>{errors.successCriteria}</p>}
          </div>

          {/* Data Requirements */}
          <div style={fieldGroup}>
            <label style={labelStyle}>{t.dataLabel}</label>
            <textarea
              value={form.dataRequirements}
              onChange={(e) => updateField("dataRequirements", e.target.value)}
              placeholder={t.dataPlaceholder}
              style={textareaStyle}
            />
          </div>

          {/* Expert Info */}
          <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
            <div style={{ flex: 1 }}>
              <label style={labelStyle}>{t.expertNameLabel}</label>
              <input
                type="text"
                value={form.expertName}
                onChange={(e) => updateField("expertName", e.target.value)}
                placeholder={t.expertNamePlaceholder}
                style={inputStyle}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={labelStyle}>{t.expertEmailLabel}</label>
              <input
                type="email"
                value={form.expertEmail}
                onChange={(e) => updateField("expertEmail", e.target.value)}
                placeholder={t.expertEmailPlaceholder}
                style={inputStyle}
              />
            </div>
          </div>

          {/* Submit */}
          {submitError && (
            <div style={{ padding: "0.75rem 1rem", background: "rgba(212, 93, 93, 0.1)", border: "1px solid var(--danger)", borderRadius: "6px", marginBottom: "1rem" }}>
              <p style={{ fontSize: "0.82rem", color: "var(--danger)", fontWeight: 500 }}>{t.errorTitle}: {submitError}</p>
            </div>
          )}
          <button
            onClick={handleSubmit}
            disabled={submitting}
            style={{
              width: "100%",
              padding: "0.75rem",
              background: submitting ? "var(--text-tertiary)" : "var(--accent)",
              color: "#fff",
              border: "none",
              borderRadius: "8px",
              fontWeight: 600,
              fontSize: "0.95rem",
              cursor: submitting ? "not-allowed" : "pointer",
              transition: "background 0.15s",
            }}
          >
            {submitting ? t.submitting : t.submit}
          </button>
        </div>
      </div>
    </>
  );
}
