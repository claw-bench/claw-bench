"use client";

import { useState, useCallback, useEffect, useRef } from "react";
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
    waitingTitle: "Generating Your Task...",
    waitingMessage: "Our AI is converting your proposal into a complete benchmark task. This usually takes 30-60 seconds.",
    previewTitle: "Review Generated Task",
    previewMessage: "Please review the generated task below. You can request revisions or confirm to submit for admin approval.",
    reviseLabel: "Revision Notes",
    revisePlaceholder: "Describe what needs to be changed (e.g., 'make the data more realistic', 'add edge case handling')...",
    reviseButton: "Request Revision",
    confirmButton: "Looks Good — Submit for Approval",
    confirmedTitle: "Task Confirmed!",
    confirmedMessage: "Your task has been sent to the admin team for final review and deployment. Thank you!",
    generationError: "Generation failed. You can try revising your requirements.",
    filePreviewLabel: "Generated Files",
    revisionHistory: "Revision History",
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
    waitingTitle: "正在生成任务...",
    waitingMessage: "AI 正在将您的提案转化为完整的评测任务，通常需要 30-60 秒。",
    previewTitle: "审核生成结果",
    previewMessage: "请审核下方生成的任务内容。您可以要求修改，或确认提交给管理员审批。",
    reviseLabel: "修改说明",
    revisePlaceholder: "请描述需要修改的内容（例如：'数据需要更真实'、'增加边界情况处理'）...",
    reviseButton: "要求修改",
    confirmButton: "满意 — 提交审批",
    confirmedTitle: "任务已确认！",
    confirmedMessage: "您的任务已发送给管理团队进行最终审核和部署，感谢您的贡献！",
    generationError: "生成失败，您可以修改需求后重试。",
    filePreviewLabel: "生成的文件",
    revisionHistory: "修改历史",
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

  // Auth state
  type AuthMode = "login" | "register";
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [organization, setOrganization] = useState("");
  const [inviteCode, setInviteCode] = useState("");
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<string>("");
  const [loginError, setLoginError] = useState("");
  const [inviteCodes, setInviteCodes] = useState<{ code: string; used: boolean; usedBy?: string }[]>([]);
  const [generatingCode, setGeneratingCode] = useState(false);
  const [showInvites, setShowInvites] = useState(false);
  const [form, setForm] = useState<FormData>({ ...emptyForm });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");

  // Staging workflow state
  type Stage = "form" | "waiting" | "preview" | "confirmed";
  const [stage, setStage] = useState<Stage>("form");
  const [proposalId, setProposalId] = useState<string | null>(null);
  const [preview, setPreview] = useState<Record<string, string>>({});
  const [previewMeta, setPreviewMeta] = useState<{ taskId: string; domain: string; difficulty: string }>({ taskId: "", domain: "", difficulty: "" });
  const [revisionNotes, setRevisionNotes] = useState("");
  const [revisions, setRevisions] = useState<{ notes: string; timestamp: string }[]>([]);
  const [genError, setGenError] = useState("");
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  /* ── Auth ── */
  const login = useCallback(async () => {
    setLoginError("");
    try {
      const res = await fetch(`${API_BASE}/expert-login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        setLoginError(d.detail || "Login failed");
        return;
      }
      const data = await res.json();
      setToken(data.token);
      setCurrentUser(data.username);
      sessionStorage.setItem("expert_token", data.token);
      sessionStorage.setItem("expert_user", data.username);
    } catch {
      setLoginError(t.connectionFailed);
    }
  }, [username, password, t]);

  const register = useCallback(async () => {
    setLoginError("");
    if (!inviteCode.trim()) { setLoginError("Invite code is required"); return; }
    if (username.length < 3) { setLoginError("Username must be at least 3 characters"); return; }
    if (password.length < 6) { setLoginError("Password must be at least 6 characters"); return; }
    if (!displayName.trim()) { setLoginError("Display name is required"); return; }
    try {
      const res = await fetch(`${API_BASE}/expert-register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, displayName, email, organization, inviteCode }),
      });
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        setLoginError(d.detail || "Registration failed");
        return;
      }
      const data = await res.json();
      setToken(data.token);
      setCurrentUser(data.username);
      sessionStorage.setItem("expert_token", data.token);
      sessionStorage.setItem("expert_user", data.username);
    } catch {
      setLoginError(t.connectionFailed);
    }
  }, [username, password, displayName, email, organization, inviteCode, t]);

  const loadInviteCodes = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/expert-invite-codes`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setInviteCodes(await res.json());
    } catch {}
  }, [token]);

  const generateInviteCode = useCallback(async () => {
    if (!token) return;
    setGeneratingCode(true);
    try {
      const res = await fetch(`${API_BASE}/expert-invite-codes`, {
        method: "POST", headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) loadInviteCodes();
    } catch {}
    setGeneratingCode(false);
  }, [token, loadInviteCodes]);

  useEffect(() => {
    const saved = sessionStorage.getItem("expert_token");
    const savedUser = sessionStorage.getItem("expert_user");
    if (saved) { setToken(saved); setCurrentUser(savedUser || ""); }
  }, []);

  useEffect(() => { if (token) loadInviteCodes(); }, [token, loadInviteCodes]);

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

  /* ── Poll for generation status ── */
  const startPolling = useCallback((pid: string) => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/expert-proposals/${pid}/status`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) return;
        const data = await res.json();
        setRevisions(data.revisions || []);

        if (data.generationStatus === "ready" || data.status === "generated") {
          if (pollRef.current) clearInterval(pollRef.current);
          const previewRes = await fetch(`${API_BASE}/expert-proposals/${pid}/preview`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (previewRes.ok) {
            const pv = await previewRes.json();
            setPreview(pv.files || {});
            setPreviewMeta({ taskId: pv.taskId || "", domain: pv.domain || "", difficulty: pv.difficulty || "" });
            setGenError("");
            setStage("preview");
          }
        } else if (data.status === "error" || data.generationStatus === "error") {
          if (pollRef.current) clearInterval(pollRef.current);
          setGenError(data.error || t.generationError);
          setStage("preview");
        }
      } catch { /* ignore */ }
    }, 5000);
  }, [token, t]);

  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  /* ── Submit ── */
  const handleSubmit = useCallback(async () => {
    if (!validate()) return;
    setSubmitting(true);
    setSubmitError("");
    try {
      const res = await fetch(`${API_BASE}/expert-proposals`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setSubmitError(data.detail || `Error ${res.status}`);
        return;
      }
      const data = await res.json();
      setProposalId(data.proposalId);
      setStage("waiting");
      startPolling(data.proposalId);
    } catch {
      setSubmitError(t.connectionFailed);
    } finally {
      setSubmitting(false);
    }
  }, [form, token, t, startPolling]);

  /* ── Revise ── */
  const handleRevise = useCallback(async () => {
    if (!proposalId || !revisionNotes.trim()) return;
    setStage("waiting");
    setGenError("");
    try {
      await fetch(`${API_BASE}/expert-proposals/${proposalId}/revise`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ notes: revisionNotes }),
      });
      setRevisionNotes("");
      startPolling(proposalId);
    } catch { setGenError(t.connectionFailed); setStage("preview"); }
  }, [proposalId, revisionNotes, token, t, startPolling]);

  /* ── Confirm ── */
  const handleConfirm = useCallback(async () => {
    if (!proposalId) return;
    try {
      const res = await fetch(`${API_BASE}/expert-proposals/${proposalId}/confirm`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setStage("confirmed");
    } catch { /* ignore */ }
  }, [proposalId, token]);

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

  /* ── Login / Register screen ── */
  if (!token) {
    const btnStyle: React.CSSProperties = { width: "100%", padding: "0.65rem", background: "var(--accent)", color: "#fff", border: "none", borderRadius: "6px", fontWeight: 600, fontSize: "0.88rem", cursor: "pointer" };
    const tabStyle = (active: boolean): React.CSSProperties => ({
      flex: 1, padding: "0.5rem", border: "none", borderBottom: active ? "2px solid var(--accent)" : "2px solid transparent",
      background: "transparent", color: active ? "var(--accent)" : "var(--text-tertiary)",
      fontWeight: 600, fontSize: "0.88rem", cursor: "pointer",
    });
    return (
      <>
        <div className="page-header">
          <h1>{t.title}</h1>
          <p>{t.subtitle}</p>
        </div>
        <div style={{ maxWidth: 420, margin: "2rem auto" }}>
          <div className="card" style={{ padding: "2rem" }}>
            <div style={{ display: "flex", marginBottom: "1.5rem" }}>
              <button style={tabStyle(authMode === "login")} onClick={() => { setAuthMode("login"); setLoginError(""); }}>
                {lang === "zh" ? "登录" : "Login"}
              </button>
              <button style={tabStyle(authMode === "register")} onClick={() => { setAuthMode("register"); setLoginError(""); }}>
                {lang === "zh" ? "注册" : "Register"}
              </button>
            </div>

            {authMode === "login" ? (
              <>
                <div style={fieldGroup}>
                  <label style={labelStyle}>{lang === "zh" ? "用户名" : "Username"}</label>
                  <input type="text" value={username} onChange={(e) => { setUsername(e.target.value); setLoginError(""); }}
                    onKeyDown={(e) => e.key === "Enter" && login()} placeholder="username" style={inputStyle} />
                </div>
                <div style={fieldGroup}>
                  <label style={labelStyle}>{lang === "zh" ? "密码" : "Password"}</label>
                  <input type="password" value={password} onChange={(e) => { setPassword(e.target.value); setLoginError(""); }}
                    onKeyDown={(e) => e.key === "Enter" && login()} placeholder="••••••" style={inputStyle} />
                </div>
                {loginError && <p style={{ ...errorStyle, marginBottom: "0.75rem" }}>{loginError}</p>}
                <button onClick={login} style={btnStyle}>{lang === "zh" ? "登录" : "Login"}</button>
              </>
            ) : (
              <>
                <div style={fieldGroup}>
                  <label style={labelStyle}>{lang === "zh" ? "邀请码 *" : "Invite Code *"}</label>
                  <input type="text" value={inviteCode} onChange={(e) => setInviteCode(e.target.value)}
                    placeholder={lang === "zh" ? "请输入邀请码" : "Enter invite code"} style={inputStyle} />
                </div>
                <div style={fieldGroup}>
                  <label style={labelStyle}>{lang === "zh" ? "用户名 *" : "Username *"}</label>
                  <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}
                    placeholder={lang === "zh" ? "3-30 个字符" : "3-30 characters"} style={inputStyle} />
                </div>
                <div style={fieldGroup}>
                  <label style={labelStyle}>{lang === "zh" ? "密码 *" : "Password *"}</label>
                  <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                    placeholder={lang === "zh" ? "至少 6 个字符" : "At least 6 characters"} style={inputStyle} />
                </div>
                <div style={fieldGroup}>
                  <label style={labelStyle}>{lang === "zh" ? "显示名称 *" : "Display Name *"}</label>
                  <input type="text" value={displayName} onChange={(e) => setDisplayName(e.target.value)}
                    placeholder={lang === "zh" ? "例如：张教授" : "e.g., Dr. Smith"} style={inputStyle} />
                </div>
                <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem" }}>
                  <div style={{ flex: 1 }}>
                    <label style={labelStyle}>{lang === "zh" ? "邮箱" : "Email"}</label>
                    <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="optional" style={inputStyle} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <label style={labelStyle}>{lang === "zh" ? "机构" : "Organization"}</label>
                    <input type="text" value={organization} onChange={(e) => setOrganization(e.target.value)} placeholder="optional" style={inputStyle} />
                  </div>
                </div>
                {loginError && <p style={{ ...errorStyle, marginBottom: "0.75rem" }}>{loginError}</p>}
                <button onClick={register} style={btnStyle}>{lang === "zh" ? "注册" : "Register"}</button>
              </>
            )}
          </div>
        </div>
      </>
    );
  }

  /* ── Waiting screen ── */
  if (stage === "waiting") {
    return (
      <>
        <div className="page-header"><h1>{t.title}</h1></div>
        <div style={{ maxWidth: 600, margin: "3rem auto", textAlign: "center" }}>
          <div className="card" style={{ padding: "2.5rem" }}>
            <div style={{ fontSize: "2.5rem", marginBottom: "1rem", animation: "spin 2s linear infinite" }}>&#9881;</div>
            <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
            <h2 style={{ fontSize: "1.3rem", fontWeight: 600, marginBottom: "0.75rem" }}>{t.waitingTitle}</h2>
            <p style={{ color: "var(--text-secondary)", lineHeight: 1.7 }}>{t.waitingMessage}</p>
            <p style={{ fontSize: "0.78rem", color: "var(--text-tertiary)", marginTop: "1rem", fontFamily: "var(--font-mono)" }}>
              ID: {proposalId}
            </p>
          </div>
        </div>
      </>
    );
  }

  /* ── Preview / Revision screen ── */
  if (stage === "preview") {
    const fileEntries = Object.entries(preview);
    return (
      <>
        <div className="page-header"><h1>{t.title}</h1></div>
        <div style={{ maxWidth: 900, margin: "0 auto 3rem" }}>
          {genError ? (
            <div className="card" style={{ padding: "2rem", marginBottom: "1.5rem", borderLeft: "3px solid var(--danger)" }}>
              <h3 style={{ color: "var(--danger)", marginBottom: "0.5rem" }}>{t.generationError}</h3>
              <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{genError}</p>
            </div>
          ) : (
            <div className="card" style={{ padding: "2rem", marginBottom: "1.5rem", borderLeft: "3px solid var(--accent)" }}>
              <h2 style={{ fontSize: "1.15rem", fontWeight: 600, marginBottom: "0.5rem" }}>{t.previewTitle}</h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem" }}>{t.previewMessage}</p>
              {previewMeta.taskId && (
                <p style={{ fontSize: "0.78rem", color: "var(--text-tertiary)", marginTop: "0.5rem", fontFamily: "var(--font-mono)" }}>
                  Task: {previewMeta.taskId} &middot; {previewMeta.domain} &middot; {previewMeta.difficulty}
                </p>
              )}
            </div>
          )}

          {fileEntries.length > 0 && (
            <div className="card" style={{ padding: "1.5rem", marginBottom: "1.5rem" }}>
              <h3 style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "1rem" }}>{t.filePreviewLabel}</h3>
              {fileEntries.map(([path, content]) => (
                <div key={path} style={{ marginBottom: "1rem" }}>
                  <div style={{ fontSize: "0.75rem", fontFamily: "var(--font-mono)", color: "var(--accent)", marginBottom: "0.3rem", fontWeight: 600 }}>
                    {path.split("/").slice(-2).join("/")}
                  </div>
                  <pre style={{
                    background: "var(--bg-secondary)", padding: "0.75rem", borderRadius: "6px",
                    fontSize: "0.75rem", lineHeight: 1.5, overflow: "auto", maxHeight: "300px",
                    border: "1px solid var(--border)", whiteSpace: "pre-wrap", wordBreak: "break-all",
                  }}>
                    {content}
                  </pre>
                </div>
              ))}
            </div>
          )}

          {revisions.length > 0 && (
            <div className="card" style={{ padding: "1.5rem", marginBottom: "1.5rem" }}>
              <h3 style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "0.75rem" }}>{t.revisionHistory}</h3>
              {revisions.map((r, i) => (
                <div key={i} style={{ padding: "0.5rem 0", borderBottom: i < revisions.length - 1 ? "1px solid var(--border)" : "none" }}>
                  <span style={{ fontSize: "0.72rem", color: "var(--text-tertiary)" }}>#{i + 1} &middot; {r.timestamp?.split("T")[0]}</span>
                  <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", margin: "0.25rem 0 0" }}>{r.notes}</p>
                </div>
              ))}
            </div>
          )}

          <div className="card" style={{ padding: "1.5rem" }}>
            <label style={{ display: "block", fontSize: "0.82rem", fontWeight: 600, marginBottom: "0.35rem" }}>{t.reviseLabel}</label>
            <textarea
              value={revisionNotes}
              onChange={(e) => setRevisionNotes(e.target.value)}
              placeholder={t.revisePlaceholder}
              style={{ width: "100%", minHeight: "100px", padding: "0.6rem 0.8rem", border: "1px solid var(--border)", borderRadius: "6px", fontSize: "0.85rem", background: "var(--bg)", color: "var(--text)", resize: "vertical", lineHeight: 1.6, marginBottom: "1rem" }}
            />
            <div style={{ display: "flex", gap: "0.75rem" }}>
              <button
                onClick={handleRevise}
                disabled={!revisionNotes.trim()}
                style={{ flex: 1, padding: "0.7rem", background: "transparent", color: "var(--accent)", border: "1.5px solid var(--accent)", borderRadius: "8px", fontWeight: 600, fontSize: "0.88rem", cursor: revisionNotes.trim() ? "pointer" : "not-allowed", opacity: revisionNotes.trim() ? 1 : 0.5 }}
              >
                {t.reviseButton}
              </button>
              <button
                onClick={handleConfirm}
                disabled={!!genError}
                style={{ flex: 1, padding: "0.7rem", background: genError ? "var(--text-tertiary)" : "var(--accent)", color: "#fff", border: "none", borderRadius: "8px", fontWeight: 600, fontSize: "0.88rem", cursor: genError ? "not-allowed" : "pointer" }}
              >
                {t.confirmButton}
              </button>
            </div>
          </div>
        </div>
      </>
    );
  }

  /* ── Confirmed screen ── */
  if (stage === "confirmed") {
    return (
      <>
        <div className="page-header"><h1>{t.title}</h1></div>
        <div style={{ maxWidth: 600, margin: "3rem auto", textAlign: "center" }}>
          <div className="card" style={{ padding: "2.5rem" }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>&#10003;</div>
            <h2 style={{ fontSize: "1.3rem", fontWeight: 600, marginBottom: "0.75rem" }}>{t.confirmedTitle}</h2>
            <p style={{ color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "1.5rem" }}>{t.confirmedMessage}</p>
            <button
              onClick={() => { setStage("form"); setForm({ ...emptyForm }); setProposalId(null); setPreview({}); setRevisions([]); setGenError(""); }}
              style={{ padding: "0.6rem 1.5rem", background: "var(--accent)", color: "#fff", border: "none", borderRadius: "6px", fontWeight: 500, fontSize: "0.88rem", cursor: "pointer" }}
            >
              {t.submitAnother}
            </button>
          </div>
        </div>
      </>
    );
  }

  /* ── Invite Code Panel (collapsible) ── */
  const invitePanel = (
    <div style={{ maxWidth: 720, margin: "0 auto 1rem" }}>
      <div className="card" style={{ padding: "1rem 1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <span style={{ fontWeight: 600, fontSize: "0.85rem" }}>{currentUser}</span>
            <button onClick={() => { setToken(null); setCurrentUser(""); sessionStorage.removeItem("expert_token"); sessionStorage.removeItem("expert_user"); }}
              style={{ marginLeft: "1rem", fontSize: "0.75rem", color: "var(--text-tertiary)", background: "none", border: "none", cursor: "pointer", textDecoration: "underline" }}>
              {lang === "zh" ? "退出" : "Logout"}
            </button>
          </div>
          <button onClick={() => setShowInvites(!showInvites)}
            style={{ fontSize: "0.78rem", color: "var(--accent)", background: "none", border: "1px solid var(--accent)", borderRadius: "6px", padding: "0.25rem 0.7rem", cursor: "pointer" }}>
            {showInvites ? (lang === "zh" ? "收起邀请码" : "Hide Invites") : (lang === "zh" ? "我的邀请码" : "My Invite Codes")}
          </button>
        </div>
        {showInvites && (
          <div style={{ marginTop: "0.75rem", borderTop: "1px solid var(--border)", paddingTop: "0.75rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
              <span style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                {lang === "zh" ? "分享邀请码给其他专家注册" : "Share invite codes with other experts to register"}
              </span>
              <button onClick={generateInviteCode} disabled={generatingCode}
                style={{ fontSize: "0.75rem", padding: "0.2rem 0.6rem", background: "var(--accent)", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}>
                {generatingCode ? "..." : (lang === "zh" ? "+ 生成邀请码" : "+ Generate Code")}
              </button>
            </div>
            {inviteCodes.length === 0 ? (
              <p style={{ fontSize: "0.75rem", color: "var(--text-tertiary)" }}>{lang === "zh" ? "还没有生成过邀请码" : "No invite codes yet"}</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                {inviteCodes.map((inv, i) => (
                  <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.3rem 0.5rem", background: "var(--bg-secondary)", borderRadius: "4px", fontSize: "0.75rem" }}>
                    <code style={{ fontFamily: "var(--font-mono)", color: inv.used ? "var(--text-tertiary)" : "var(--accent)", textDecoration: inv.used ? "line-through" : "none" }}>
                      {inv.code}
                    </code>
                    <span style={{ color: "var(--text-tertiary)" }}>
                      {inv.used ? `${lang === "zh" ? "已使用" : "Used"}: ${inv.usedBy}` : (lang === "zh" ? "未使用" : "Available")}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );

  /* ── Form ── */
  return (
    <>
      <div className="page-header">
        <h1>{t.title}</h1>
        <p>{t.subtitle}</p>
      </div>

      {invitePanel}

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
