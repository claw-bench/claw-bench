"use client";

import { useState, useEffect, useCallback } from "react";

const API = "/api/admin";

/* ── Types ──────────────────────────────────────────────────────── */

interface Result {
  _filename?: string;
  framework: string;
  model: string;
  overall: number;
  taskCompletion: number;
  efficiency: number;
  security: number;
  skills: number;
  ux: number;
  testTier?: string;
  agentProfile?: {
    profileId?: string;
    displayName: string;
    model: string;
    framework: string;
    skillsMode: string;
    skills: string[];
    mcpServers: string[];
    memoryModules: string[];
    modelTier?: string;
    tags: Record<string, string>;
  };
  progressive?: {
    baseline_pass_rate: number;
    current_pass_rate: number;
    absolute_gain: number;
    normalized_gain: number;
  };
}

interface SkillsGainEntry {
  framework: string;
  model: string;
  vanilla: number;
  curated: number;
  native: number;
}

interface MoltBookAgent {
  clawId: string;
  displayName: string;
  framework: string;
  model: string;
  submitter?: string;
  modelTier?: string;
  runs: { date: string; tier: string; overall: number; passRate: number }[];
}

interface Proposal {
  _proposalId: string;
  _submittedAt: string;
  _status: string;
  _generatedTaskId?: string;
  domain: string;
  taskTitle: string;
  difficulty: string;
  context: string;
  instruction: string;
  requiredActions: string[];
  successCriteria: string;
  dataRequirements?: string;
  expertName?: string;
  expertEmail?: string;
}

interface GeneratedTaskSummary {
  _id: string;
  taskId: string;
  taskDirName: string;
  proposalId: string;
  domain: string;
  taskTitle: string;
  difficulty: string;
  status: string;
  fileCount: number;
  filePaths: string[];
  generatedAt: string;
  error?: string | null;
}

interface GeneratedTaskDetail {
  _id: string;
  taskId: string;
  taskDirName: string;
  proposalId: string;
  domain: string;
  taskTitle: string;
  difficulty: string;
  status: string;
  files: Record<string, string>;
  generatedAt: string;
  error?: string | null;
}

const emptyResult: Result = {
  framework: "", model: "", overall: 0, taskCompletion: 0, efficiency: 0,
  security: 0, skills: 0, ux: 0, testTier: "comprehensive",
  agentProfile: { displayName: "", model: "", framework: "", skillsMode: "vanilla", skills: [], mcpServers: [], memoryModules: [], modelTier: "flagship", tags: {} },
  progressive: { baseline_pass_rate: 0, current_pass_rate: 0, absolute_gain: 0, normalized_gain: 0 },
};

const emptySkillsGain: SkillsGainEntry = { framework: "", model: "", vanilla: 0, curated: 0, native: 0 };

const emptyAgent: MoltBookAgent = { clawId: "", displayName: "", framework: "", model: "", submitter: "", modelTier: "flagship", runs: [] };

type Tab = "pending" | "results" | "skills" | "moltbook" | "config" | "proposals" | "generated" | "experts";

/* ── Components ─────────────────────────────────────────────────── */

const Field = ({ label, value, onChange, type = "text", half = false }: {
  label: string; value: string | number; onChange: (v: string) => void; type?: string; half?: boolean;
}) => (
  <div style={{ flex: half ? "1 1 45%" : "1 1 100%", minWidth: half ? 140 : 0 }}>
    <label style={{ display: "block", fontSize: "0.7rem", color: "var(--text-tertiary)", marginBottom: "0.15rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>{label}</label>
    <input type={type} value={value} onChange={(e) => onChange(e.target.value)}
      style={{ width: "100%", padding: "0.4rem 0.65rem", border: "1px solid var(--border)", borderRadius: "5px", fontSize: "0.82rem", background: "var(--bg)", color: "var(--text)" }} />
  </div>
);

const Btn = ({ children, onClick, variant = "primary", disabled = false }: {
  children: React.ReactNode; onClick: () => void; variant?: "primary" | "secondary" | "danger" | "success"; disabled?: boolean;
}) => {
  const styles: Record<string, React.CSSProperties> = {
    primary: { background: "var(--accent)", color: "#fff", border: "none" },
    secondary: { background: "transparent", color: "var(--text-secondary)", border: "1px solid var(--border)" },
    danger: { background: "transparent", color: "var(--danger)", border: "1px solid var(--danger)" },
    success: { background: "#22c55e", color: "#fff", border: "none" },
  };
  return (
    <button onClick={onClick} disabled={disabled}
      style={{ padding: "0.4rem 1rem", borderRadius: "6px", fontWeight: 500, fontSize: "0.8rem", cursor: disabled ? "wait" : "pointer", opacity: disabled ? 0.6 : 1, ...styles[variant] }}>
      {children}
    </button>
  );
};

const StatusBadge = ({ status }: { status: string }) => {
  const colors: Record<string, { bg: string; text: string }> = {
    pending: { bg: "rgba(234, 179, 8, 0.15)", text: "#ca8a04" },
    generating: { bg: "rgba(59, 130, 246, 0.15)", text: "#2563eb" },
    generated: { bg: "rgba(34, 197, 94, 0.15)", text: "#16a34a" },
    ready: { bg: "rgba(34, 197, 94, 0.15)", text: "#16a34a" },
    approved: { bg: "rgba(34, 197, 94, 0.25)", text: "#15803d" },
    rejected: { bg: "rgba(239, 68, 68, 0.15)", text: "#dc2626" },
    error: { bg: "rgba(239, 68, 68, 0.15)", text: "#dc2626" },
  };
  const c = colors[status] || colors.pending;
  return (
    <span style={{
      display: "inline-block", padding: "0.15rem 0.55rem", borderRadius: "12px",
      fontSize: "0.72rem", fontWeight: 600, background: c.bg, color: c.text,
    }}>
      {status.toUpperCase()}
    </span>
  );
};

/* ── Main ───────────────────────────────────────────────────────── */

export default function AdminPage() {
  const [token, setToken] = useState<string | null>(null);
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [activeTab, setActiveTab] = useState<Tab>("proposals");
  const [message, setMessage] = useState("");
  const [rebuilding, setRebuilding] = useState(false);

  // Results state
  const [results, setResults] = useState<Result[]>([]);
  const [editResult, setEditResult] = useState<Result | null>(null);
  const [editFilename, setEditFilename] = useState<string | null>(null);

  // Skills gain state
  const [skillsGain, setSkillsGain] = useState<SkillsGainEntry[]>([]);
  const [editSkill, setEditSkill] = useState<SkillsGainEntry | null>(null);
  const [editSkillIdx, setEditSkillIdx] = useState<number | null>(null);

  // MoltBook state
  const [agents, setAgents] = useState<MoltBookAgent[]>([]);
  const [editAgent, setEditAgent] = useState<MoltBookAgent | null>(null);
  const [editAgentId, setEditAgentId] = useState<string | null>(null);

  // Pending state
  const [pending, setPending] = useState<Record<string, unknown>[]>([]);

  // Config state
  const [configDomains, setConfigDomains] = useState("");
  const [configModels, setConfigModels] = useState("");
  const [configCapabilities, setConfigCapabilities] = useState("");

  // Expert management
  const [experts, setExperts] = useState<Record<string, unknown>[]>([]);
  const [allInviteCodes, setAllInviteCodes] = useState<Record<string, unknown>[]>([]);
  const [newInviteCount, setNewInviteCount] = useState(1);

  // Proposals state
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [expandedProposal, setExpandedProposal] = useState<string | null>(null);
  const [generatingIds, setGeneratingIds] = useState<Set<string>>(new Set());

  // Task generation model state
  const [taskGenModels, setTaskGenModels] = useState<{id: string; label: string; provider: string}[]>([]);
  const [activeModel, setActiveModel] = useState<string>("");
  const [modelSaving, setModelSaving] = useState(false);

  // Generated tasks state
  const [generatedTasks, setGeneratedTasks] = useState<GeneratedTaskSummary[]>([]);
  const [reviewingTask, setReviewingTask] = useState<GeneratedTaskDetail | null>(null);
  const [editingFiles, setEditingFiles] = useState<Record<string, string>>({});
  const [activeFileTab, setActiveFileTab] = useState<string>("");

  const headers = useCallback(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);
  const showMsg = (m: string) => { setMessage(m); setTimeout(() => setMessage(""), 4000); };

  // Auth
  const login = async () => {
    try {
      const res = await fetch(`${API}/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ password }) });
      if (!res.ok) { setLoginError("密码错误"); return; }
      const data = await res.json();
      setToken(data.token);
      sessionStorage.setItem("admin_token", data.token);
    } catch { setLoginError("连接失败"); }
  };

  useEffect(() => { const saved = sessionStorage.getItem("admin_token"); if (saved) setToken(saved); }, []);

  // Load data
  const loadPending = useCallback(async () => { if (!token) return; try { const r = await fetch(`${API}/pending`, { headers: headers() }); if (r.ok) setPending(await r.json()); } catch {} }, [token, headers]);
  const loadResults = useCallback(async () => { if (!token) return; try { const r = await fetch(`${API}/results`, { headers: headers() }); if (r.ok) setResults(await r.json()); } catch {} }, [token, headers]);
  const loadSkillsGain = useCallback(async () => { if (!token) return; try { const r = await fetch(`${API}/skills-gain`, { headers: headers() }); if (r.ok) setSkillsGain(await r.json()); } catch {} }, [token, headers]);
  const loadAgents = useCallback(async () => { if (!token) return; try { const r = await fetch(`${API}/moltbook`, { headers: headers() }); if (r.ok) setAgents(await r.json()); } catch {} }, [token, headers]);
  const loadConfig = useCallback(async () => {
    if (!token) return;
    for (const name of ["domains", "models", "capabilities"]) {
      try {
        const r = await fetch(`${API}/config/${name}`, { headers: headers() });
        if (r.ok) {
          const text = JSON.stringify(await r.json(), null, 2);
          if (name === "domains") setConfigDomains(text);
          if (name === "models") setConfigModels(text);
          if (name === "capabilities") setConfigCapabilities(text);
        }
      } catch {}
    }
  }, [token, headers]);

  const loadTaskGenModels = useCallback(async () => {
    if (!token) return;
    try {
      const r = await fetch(`${API}/task-gen-models`, { headers: headers() });
      if (r.ok) {
        const data = await r.json();
        setTaskGenModels(data.models || []);
        setActiveModel(data.active || "");
      }
    } catch {}
  }, [token, headers]);

  const saveTaskGenModel = async (modelId: string) => {
    setModelSaving(true);
    try {
      const r = await fetch(`${API}/task-gen-models`, { method: "PUT", headers: headers(), body: JSON.stringify({ model: modelId }) });
      if (r.ok) { setActiveModel(modelId); showMsg(`任务生成模型已切换为 ${taskGenModels.find(m => m.id === modelId)?.label || modelId}`); }
      else showMsg("切换失败");
    } catch { showMsg("切换失败"); }
    setModelSaving(false);
  };

  const loadProposals = useCallback(async () => {
    if (!token) return;
    try {
      const r = await fetch(`${API}/expert-proposals`, { headers: headers() });
      if (r.ok) setProposals(await r.json());
    } catch {}
  }, [token, headers]);

  const loadGeneratedTasks = useCallback(async () => {
    if (!token) return;
    try {
      const r = await fetch(`${API}/generated-tasks`, { headers: headers() });
      if (r.ok) setGeneratedTasks(await r.json());
    } catch {}
  }, [token, headers]);

  const loadExperts = useCallback(async () => {
    if (!token) return;
    try {
      const r = await fetch(`${API}/experts`, { headers: headers() });
      if (r.ok) setExperts(await r.json());
    } catch {}
  }, [token, headers]);

  const loadAllInviteCodes = useCallback(async () => {
    if (!token) return;
    try {
      const r = await fetch(`${API}/invite-codes`, { headers: headers() });
      if (r.ok) setAllInviteCodes(await r.json());
    } catch {}
  }, [token, headers]);

  const adminGenerateInvites = async () => {
    const r = await fetch(`${API}/invite-codes/generate?count=${newInviteCount}`, { method: "POST", headers: headers() });
    if (r.ok) { showMsg(`Generated ${newInviteCount} invite codes`); loadAllInviteCodes(); }
  };

  const toggleExpertStatus = async (un: string, current: string) => {
    const newStatus = current === "active" ? "disabled" : "active";
    const r = await fetch(`${API}/experts/${un}/status?status=${newStatus}`, { method: "PUT", headers: headers() });
    if (r.ok) { showMsg(`${un}: ${newStatus}`); loadExperts(); }
  };

  const changeExpertRole = async (un: string, role: string) => {
    const r = await fetch(`${API}/experts/${un}/role?role=${role}`, { method: "PUT", headers: headers() });
    if (r.ok) { showMsg(`${un}: role → ${role}`); loadExperts(); }
  };

  const deleteExpert = async (un: string) => {
    if (!confirm(`Delete expert ${un}?`)) return;
    const r = await fetch(`${API}/experts/${un}`, { method: "DELETE", headers: headers() });
    if (r.ok) { showMsg(`Deleted ${un}`); loadExperts(); }
  };

  useEffect(() => {
    if (token) {
      loadPending(); loadResults(); loadSkillsGain(); loadAgents(); loadConfig();
      loadProposals(); loadGeneratedTasks(); loadExperts(); loadAllInviteCodes();
      loadTaskGenModels();
    }
  }, [token, loadPending, loadResults, loadSkillsGain, loadAgents, loadConfig, loadProposals, loadGeneratedTasks, loadTaskGenModels]);

  // Result CRUD
  const saveResult = async () => {
    if (!editResult) return;
    const { _filename, ...data } = editResult;
    if (data.agentProfile) { data.agentProfile.model = data.model; data.agentProfile.framework = data.framework; if (!data.agentProfile.displayName) data.agentProfile.displayName = `${data.framework} / ${data.model}`; }
    const url = editFilename ? `${API}/results/${editFilename}` : `${API}/results`;
    const r = await fetch(url, { method: editFilename ? "PUT" : "POST", headers: headers(), body: JSON.stringify(data) });
    if (r.ok) { showMsg("已保存"); setEditResult(null); setEditFilename(null); loadResults(); } else showMsg("保存失败");
  };
  const deleteResult = async (fn: string) => { if (!confirm("确定删除？")) return; const r = await fetch(`${API}/results/${fn}`, { method: "DELETE", headers: headers() }); if (r.ok) { showMsg("已删除"); loadResults(); } };

  // Skills Gain CRUD
  const saveSkillsGain = async () => {
    if (!editSkill) return;
    const updated = [...skillsGain];
    if (editSkillIdx !== null) updated[editSkillIdx] = editSkill;
    else updated.push(editSkill);
    const r = await fetch(`${API}/skills-gain`, { method: "POST", headers: headers(), body: JSON.stringify(updated) });
    if (r.ok) { showMsg("已保存"); setEditSkill(null); setEditSkillIdx(null); loadSkillsGain(); } else showMsg("保存失败");
  };
  const deleteSkillsGainEntry = async (idx: number) => {
    if (!confirm("确定删除？")) return;
    const updated = skillsGain.filter((_, i) => i !== idx);
    const r = await fetch(`${API}/skills-gain`, { method: "POST", headers: headers(), body: JSON.stringify(updated) });
    if (r.ok) { showMsg("已删除"); loadSkillsGain(); }
  };

  // MoltBook CRUD
  const saveAgent = async () => {
    if (!editAgent) return;
    const url = editAgentId ? `${API}/moltbook/${editAgentId}` : `${API}/moltbook`;
    const r = await fetch(url, { method: editAgentId ? "PUT" : "POST", headers: headers(), body: JSON.stringify(editAgent) });
    if (r.ok) { showMsg("已保存"); setEditAgent(null); setEditAgentId(null); loadAgents(); } else showMsg("保存失败");
  };
  const deleteAgent = async (id: string) => { if (!confirm("确定删除？")) return; const r = await fetch(`${API}/moltbook/${id}`, { method: "DELETE", headers: headers() }); if (r.ok) { showMsg("已删除"); loadAgents(); } };

  // Pending approve/reject
  const approvePending = async (fn: string) => {
    const r = await fetch(`${API}/pending/${fn}/approve`, { method: "POST", headers: headers() });
    if (r.ok) { showMsg("已批准，数据已加入排行榜"); loadPending(); loadResults(); } else showMsg("操作失败");
  };
  const rejectPending = async (fn: string) => {
    if (!confirm("确定拒绝此提交？")) return;
    const r = await fetch(`${API}/pending/${fn}/reject`, { method: "POST", headers: headers() });
    if (r.ok) { showMsg("已拒绝"); loadPending(); } else showMsg("操作失败");
  };

  // Config save
  const saveConfig = async (name: string, text: string) => {
    try {
      const data = JSON.parse(text);
      const r = await fetch(`${API}/config/${name}`, { method: "PUT", headers: headers(), body: JSON.stringify(data) });
      if (r.ok) { showMsg(`${name} 配置已保存`); } else { showMsg("保存失败"); }
    } catch { showMsg("JSON 格式错误"); }
  };

  const triggerRebuild = async () => {
    setRebuilding(true);
    try { const r = await fetch(`${API}/rebuild`, { method: "POST", headers: headers() }); const d = await r.json(); showMsg(d.status === "rebuilt" ? "前端重建成功" : `重建失败: ${d.message || d.stderr}`); } catch { showMsg("重建请求失败"); }
    setRebuilding(false);
  };

  // ── Proposal actions ──
  const triggerGenerate = async (proposalId: string) => {
    setGeneratingIds(prev => new Set(prev).add(proposalId));
    try {
      const r = await fetch(`${API}/generate-task`, {
        method: "POST", headers: headers(),
        body: JSON.stringify({ proposalId }),
      });
      if (r.ok) {
        const data = await r.json();
        showMsg(`任务生成已启动 (ID: ${data.generatedTaskId})，请在「生成任务」标签页查看进度`);
        loadProposals();
        // Poll for completion
        const pollId = setInterval(async () => {
          await loadGeneratedTasks();
          try {
            const check = await fetch(`${API}/generated-tasks/${data.generatedTaskId}`, { headers: headers() });
            if (check.ok) {
              const detail = await check.json();
              if (detail.status !== "generating") {
                clearInterval(pollId);
                setGeneratingIds(prev => { const n = new Set(prev); n.delete(proposalId); return n; });
                loadProposals();
                loadGeneratedTasks();
                if (detail.status === "ready") {
                  showMsg(`任务 ${detail.taskId} 生成完成，请前往「生成任务」标签页审核`);
                } else if (detail.status === "error") {
                  showMsg(`任务生成失败: ${detail.error}`);
                }
              }
            }
          } catch {}
        }, 3000);
        // Safety timeout: stop polling after 5 minutes
        setTimeout(() => {
          clearInterval(pollId);
          setGeneratingIds(prev => { const n = new Set(prev); n.delete(proposalId); return n; });
        }, 300000);
      } else {
        const err = await r.json().catch(() => ({}));
        showMsg(`生成失败: ${err.detail || r.status}`);
        setGeneratingIds(prev => { const n = new Set(prev); n.delete(proposalId); return n; });
      }
    } catch {
      showMsg("生成请求失败");
      setGeneratingIds(prev => { const n = new Set(prev); n.delete(proposalId); return n; });
    }
  };

  const deleteProposal = async (proposalId: string) => {
    if (!confirm("确定删除此提案？")) return;
    const r = await fetch(`${API}/expert-proposals/${proposalId}`, { method: "DELETE", headers: headers() });
    if (r.ok) { showMsg("已删除"); loadProposals(); } else showMsg("删除失败");
  };

  // ── Generated task actions ──
  const openReview = async (genId: string) => {
    try {
      const r = await fetch(`${API}/generated-tasks/${genId}`, { headers: headers() });
      if (r.ok) {
        const detail: GeneratedTaskDetail = await r.json();
        setReviewingTask(detail);
        setEditingFiles({ ...detail.files });
        const firstFile = Object.keys(detail.files)[0] || "";
        setActiveFileTab(firstFile);
      } else showMsg("加载失败");
    } catch { showMsg("加载失败"); }
  };

  const approveTask = async () => {
    if (!reviewingTask) return;
    const r = await fetch(`${API}/generated-tasks/${reviewingTask._id}/approve`, {
      method: "POST", headers: headers(),
      body: JSON.stringify({ files: editingFiles }),
    });
    if (r.ok) {
      const data = await r.json();
      showMsg(`任务 ${data.taskId} 已批准，${data.filesWritten?.length || 0} 个文件已写入 tasks/ 目录`);
      setReviewingTask(null);
      loadGeneratedTasks();
      loadProposals();
    } else showMsg("批准失败");
  };

  const rejectTask = async (genId: string) => {
    if (!confirm("确定拒绝此生成任务？")) return;
    const r = await fetch(`${API}/generated-tasks/${genId}/reject`, { method: "POST", headers: headers() });
    if (r.ok) { showMsg("已拒绝"); setReviewingTask(null); loadGeneratedTasks(); loadProposals(); } else showMsg("操作失败");
  };

  const regenerateTask = async (genId: string) => {
    const r = await fetch(`${API}/generated-tasks/${genId}/regenerate`, { method: "POST", headers: headers() });
    if (r.ok) {
      showMsg("重新生成已启动");
      setReviewingTask(null);
      loadGeneratedTasks();
    } else showMsg("操作失败");
  };

  const deleteGeneratedTask = async (genId: string) => {
    if (!confirm("确定删除？")) return;
    const r = await fetch(`${API}/generated-tasks/${genId}`, { method: "DELETE", headers: headers() });
    if (r.ok) { showMsg("已删除"); setReviewingTask(null); loadGeneratedTasks(); } else showMsg("删除失败");
  };

  // ── Login ──
  if (!token) return (
    <div style={{ maxWidth: 360, margin: "6rem auto", textAlign: "center" }}>
      <img src="/logo.png" alt="ClawBench" width={64} height={64} style={{ marginBottom: "1.5rem" }} />
      <h2 style={{ fontSize: "1.3rem", fontWeight: 600, marginBottom: "0.5rem" }}>Admin Console</h2>
      <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "1.5rem" }}>请输入管理密码</p>
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} onKeyDown={(e) => e.key === "Enter" && login()} placeholder="Password"
        style={{ width: "100%", padding: "0.6rem 1rem", border: "1px solid var(--border)", borderRadius: "6px", fontSize: "0.9rem", marginBottom: "0.75rem", background: "var(--bg-card)", color: "var(--text)" }} />
      {loginError && <p style={{ color: "var(--danger)", fontSize: "0.82rem", marginBottom: "0.5rem" }}>{loginError}</p>}
      <button onClick={login} style={{ width: "100%", padding: "0.6rem", background: "var(--accent)", color: "#fff", border: "none", borderRadius: "6px", fontWeight: 500, fontSize: "0.85rem", cursor: "pointer" }}>登录</button>
    </div>
  );

  // ── Main UI ──
  return (
    <div style={{ paddingTop: "1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.4rem", fontWeight: 600, letterSpacing: "-0.02em" }}>Admin Console</h1>
          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>管理排行榜数据、专家提案与任务生成</p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <Btn onClick={triggerRebuild} disabled={rebuilding}>{rebuilding ? "重建中..." : "重建前端"}</Btn>
          <Btn onClick={() => { sessionStorage.removeItem("admin_token"); setToken(null); }} variant="secondary">退出</Btn>
        </div>
      </div>

      {message && <div style={{ padding: "0.6rem 1rem", background: "var(--accent-light)", border: "1px solid var(--accent)", borderRadius: "6px", marginBottom: "1rem", fontSize: "0.82rem", color: "var(--accent)", fontWeight: 500 }}>{message}</div>}

      {/* Tabs */}
      <div style={{ display: "flex", gap: "0.4rem", marginBottom: "1.5rem", borderBottom: "1px solid var(--border)", paddingBottom: "0.5rem", flexWrap: "wrap" }}>
        {([
          ["proposals", `专家提案 (${proposals.length})`],
          ["generated", `生成任务 (${generatedTasks.length})`],
          ["pending", `待审核 (${pending.length})`],
          ["results", "排行榜数据"],
          ["skills", "技能增益"],
          ["moltbook", "身份册"],
          ["experts", `专家管理 (${experts.length})`],
          ["config", "配置管理"],
        ] as [Tab, string][]).map(([key, label]) => (
          <button key={key} onClick={() => setActiveTab(key)}
            style={{ padding: "0.4rem 1rem", border: "none", borderRadius: "6px", background: activeTab === key ? "var(--accent)" : "transparent", color: activeTab === key ? "#fff" : "var(--text-secondary)", fontWeight: 500, fontSize: "0.82rem", cursor: "pointer" }}>
            {label}
          </button>
        ))}
      </div>

      {/* ── Proposals Tab ── */}
      {activeTab === "proposals" && (<>
        {/* Model selector */}
        <div className="card" style={{ marginBottom: "1rem", padding: "0.8rem 1.2rem", display: "flex", alignItems: "center", gap: "0.8rem", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--text-secondary)", whiteSpace: "nowrap" }}>任务生成模型</span>
          <select
            value={activeModel}
            onChange={(e) => saveTaskGenModel(e.target.value)}
            disabled={modelSaving}
            style={{
              padding: "0.35rem 0.7rem", border: "1px solid var(--border)", borderRadius: "6px",
              fontSize: "0.82rem", background: "var(--bg)", color: "var(--text)",
              cursor: modelSaving ? "wait" : "pointer", minWidth: "240px",
            }}
          >
            {activeModel && !taskGenModels.find(m => m.id === activeModel) && (
              <option value={activeModel}>{activeModel}</option>
            )}
            {taskGenModels.map((m) => (
              <option key={m.id} value={m.id}>{m.provider} — {m.label}</option>
            ))}
          </select>
          <span style={{ fontSize: "0.72rem", color: "var(--text-tertiary)" }}>
            切换后对新的任务生成立即生效
          </span>
        </div>

        <div style={{ marginBottom: "1rem", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
          {proposals.length > 0
            ? `${proposals.length} 条专家提案 — 点击「生成任务」调用 LLM 自动构建完整任务文件`
            : "暂无专家提案。专家可通过 /expert-submit 页面提交任务提案。"}
        </div>
        {proposals.map((p) => {
          const isExpanded = expandedProposal === p._proposalId;
          const isGenerating = generatingIds.has(p._proposalId);
          return (
            <div key={p._proposalId} className="card" style={{ marginBottom: "1rem", padding: "1.2rem" }}>
              {/* Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.3rem" }}>
                    <span style={{ fontWeight: 600, fontSize: "0.95rem" }}>{p.taskTitle}</span>
                    <StatusBadge status={p._status} />
                    <code style={{ fontSize: "0.7rem", padding: "0.1rem 0.4rem", background: "var(--bg-secondary)", borderRadius: "4px" }}>{p.difficulty}</code>
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)" }}>
                    {p.domain} · {p.expertName || "匿名"} · {(p._submittedAt || "").split("T")[0]}
                  </div>
                </div>
                <div style={{ display: "flex", gap: "0.4rem", flexShrink: 0 }}>
                  <Btn onClick={() => setExpandedProposal(isExpanded ? null : p._proposalId)} variant="secondary">
                    {isExpanded ? "收起" : "详情"}
                  </Btn>
                  {(p._status === "pending" || p._status === "rejected" || p._status === "error") && (
                    <Btn onClick={() => triggerGenerate(p._proposalId)} disabled={isGenerating}>
                      {isGenerating ? "生成中..." : "生成任务"}
                    </Btn>
                  )}
                  {p._status === "generated" && p._generatedTaskId && (
                    <Btn onClick={() => { setActiveTab("generated"); openReview(p._generatedTaskId!); }} variant="success">
                      查看生成结果
                    </Btn>
                  )}
                  <Btn onClick={() => deleteProposal(p._proposalId)} variant="danger">删除</Btn>
                </div>
              </div>

              {/* Expanded detail */}
              {isExpanded && (
                <div style={{ borderTop: "1px solid var(--border)", paddingTop: "0.75rem", fontSize: "0.82rem", lineHeight: 1.7 }}>
                  <div style={{ marginBottom: "0.6rem" }}>
                    <strong>真实场景：</strong>
                    <div style={{ color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>{p.context}</div>
                  </div>
                  <div style={{ marginBottom: "0.6rem" }}>
                    <strong>Agent 指令：</strong>
                    <div style={{ color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>{p.instruction}</div>
                  </div>
                  <div style={{ marginBottom: "0.6rem" }}>
                    <strong>必需操作：</strong>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.3rem", marginTop: "0.3rem" }}>
                      {p.requiredActions.map((a) => (
                        <span key={a} style={{ padding: "0.15rem 0.5rem", background: "var(--accent-light)", color: "var(--accent)", borderRadius: "12px", fontSize: "0.72rem", fontWeight: 500 }}>
                          {a}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div style={{ marginBottom: "0.6rem" }}>
                    <strong>成功标准：</strong>
                    <div style={{ color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>{p.successCriteria}</div>
                  </div>
                  {p.dataRequirements && (
                    <div style={{ marginBottom: "0.6rem" }}>
                      <strong>数据需求：</strong>
                      <div style={{ color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>{p.dataRequirements}</div>
                    </div>
                  )}
                  {p.expertEmail && (
                    <div><strong>联系邮箱：</strong> <span style={{ color: "var(--text-secondary)" }}>{p.expertEmail}</span></div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </>)}

      {/* ── Generated Tasks Tab ── */}
      {activeTab === "generated" && (<>
        {/* Review modal */}
        {reviewingTask && (
          <div style={{
            position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
            background: "rgba(0,0,0,0.6)", zIndex: 1000,
            display: "flex", justifyContent: "center", alignItems: "center",
            padding: "2rem",
          }}>
            <div style={{
              background: "var(--bg-card)", borderRadius: "12px", width: "100%", maxWidth: "1100px",
              maxHeight: "90vh", display: "flex", flexDirection: "column", overflow: "hidden",
              border: "1px solid var(--border)",
            }}>
              {/* Review header */}
              <div style={{ padding: "1.2rem 1.5rem", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <h2 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                    审核生成任务: {reviewingTask.taskId}
                  </h2>
                  <div style={{ fontSize: "0.78rem", color: "var(--text-tertiary)" }}>
                    {reviewingTask.domain} · {reviewingTask.difficulty} · {reviewingTask.taskTitle}
                  </div>
                </div>
                <div style={{ display: "flex", gap: "0.4rem" }}>
                  <Btn onClick={approveTask} variant="success">批准并写入</Btn>
                  <Btn onClick={() => regenerateTask(reviewingTask._id)}>重新生成</Btn>
                  <Btn onClick={() => rejectTask(reviewingTask._id)} variant="danger">拒绝</Btn>
                  <Btn onClick={() => setReviewingTask(null)} variant="secondary">关闭</Btn>
                </div>
              </div>

              {/* File tabs */}
              <div style={{ display: "flex", borderBottom: "1px solid var(--border)", overflowX: "auto", flexShrink: 0 }}>
                {Object.keys(editingFiles).map((path) => {
                  const shortName = path.split("/").slice(-1)[0];
                  const isActive = activeFileTab === path;
                  return (
                    <button key={path} onClick={() => setActiveFileTab(path)}
                      style={{
                        padding: "0.5rem 1rem", border: "none", borderBottom: isActive ? "2px solid var(--accent)" : "2px solid transparent",
                        background: "transparent", color: isActive ? "var(--accent)" : "var(--text-secondary)",
                        fontSize: "0.78rem", fontWeight: isActive ? 600 : 400, cursor: "pointer", whiteSpace: "nowrap",
                        fontFamily: "var(--font-mono)",
                      }}>
                      {shortName}
                    </button>
                  );
                })}
              </div>

              {/* File editor */}
              <div style={{ overflow: "auto", padding: "0" }}>
                <div style={{ padding: "0.5rem 1rem", fontSize: "0.72rem", color: "var(--text-tertiary)", fontFamily: "var(--font-mono)", background: "var(--bg-secondary)", position: "sticky", top: 0, zIndex: 1 }}>
                  {activeFileTab}
                </div>
                <textarea
                  value={editingFiles[activeFileTab] || ""}
                  onChange={(e) => setEditingFiles(prev => ({ ...prev, [activeFileTab]: e.target.value }))}
                  style={{
                    width: "100%", height: "55vh", padding: "1rem", border: "none",
                    fontFamily: "var(--font-mono)", fontSize: "0.8rem",
                    background: "var(--bg)", color: "var(--text)",
                    resize: "vertical", lineHeight: 1.6, outline: "none",
                    display: "block", boxSizing: "border-box",
                  }}
                  spellCheck={false}
                />
              </div>
            </div>
          </div>
        )}

        <div style={{ marginBottom: "1rem", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
          {generatedTasks.length > 0
            ? `${generatedTasks.length} 个生成任务 — 点击「审核」查看和编辑生成的文件，确认后批准写入 tasks/ 目录`
            : "暂无生成任务。请先在「专家提案」标签页中点击「生成任务」。"}
        </div>
        {generatedTasks.map((t) => (
          <div key={t._id} className="card" style={{ marginBottom: "0.75rem", padding: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.25rem" }}>
                  <span style={{ fontWeight: 600, fontSize: "0.9rem", fontFamily: "var(--font-mono)" }}>{t.taskId || "(pending)"}</span>
                  <StatusBadge status={t.status} />
                  <code style={{ fontSize: "0.7rem", padding: "0.1rem 0.4rem", background: "var(--bg-secondary)", borderRadius: "4px" }}>{t.difficulty}</code>
                </div>
                <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                  {t.taskTitle} · {t.domain} · {t.fileCount} files · {(t.generatedAt || "").split("T")[0]}
                </div>
                {t.error && (
                  <div style={{ fontSize: "0.75rem", color: "var(--danger)", marginTop: "0.3rem" }}>
                    Error: {t.error}
                  </div>
                )}
              </div>
              <div style={{ display: "flex", gap: "0.4rem" }}>
                {t.status === "ready" && (
                  <Btn onClick={() => openReview(t._id)} variant="success">审核</Btn>
                )}
                {(t.status === "error" || t.status === "rejected") && (
                  <Btn onClick={() => regenerateTask(t._id)}>重新生成</Btn>
                )}
                {t.status === "generating" && (
                  <Btn onClick={() => loadGeneratedTasks()} variant="secondary">刷新</Btn>
                )}
                <Btn onClick={() => deleteGeneratedTask(t._id)} variant="danger">删除</Btn>
              </div>
            </div>
          </div>
        ))}
      </>)}

      {/* ── Pending Tab ── */}
      {activeTab === "pending" && (<>
        <div style={{ marginBottom: "1rem", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
          {pending.length > 0 ? `${pending.length} 条待审核提交` : "暂无待审核提交"}
        </div>
        {pending.map((p, i) => {
          const fn = (p._filename as string) || "";
          const region = (p.region as Record<string, string>) || {};
          const profile = (p.agentProfile as Record<string, unknown>) || {};
          return (
            <div key={fn || i} className="card" style={{ marginBottom: "1rem", padding: "1rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: "0.95rem" }}>
                    {region.flag || ""} {(profile.displayName as string) || `${p.framework} / ${p.model}`}
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", fontFamily: "var(--font-mono)" }}>
                    {String(p.clawId || "")} · {((p._submittedAt as string) || "").split("T")[0]} · IP: {String(p._submittedBy || "").slice(0, 12)}
                  </div>
                </div>
                <div style={{ display: "flex", gap: "0.4rem" }}>
                  <Btn onClick={() => approvePending(fn)}>批准</Btn>
                  <Btn onClick={() => rejectPending(fn)} variant="danger">拒绝</Btn>
                </div>
              </div>
              <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", fontSize: "0.8rem" }}>
                <span><strong>Overall:</strong> {Number(p.overall || 0).toFixed(2)}</span>
                <span><strong>Task:</strong> {Number(p.taskCompletion || 0).toFixed(2)}</span>
                <span><strong>Eff:</strong> {Number(p.efficiency || 0).toFixed(2)}</span>
                <span><strong>Sec:</strong> {Number(p.security || 0).toFixed(2)}</span>
                <span><strong>Skills:</strong> {Number(p.skills || 0).toFixed(2)}</span>
                <span><strong>UX:</strong> {Number(p.ux || 0).toFixed(2)}</span>
                <span><strong>Tier:</strong> {(p.testTier as string) || "-"}</span>
                <span><strong>Region:</strong> {region.name || "Unknown"}</span>
                {p._previousScore != null && <span><strong>Previous:</strong> {Number(p._previousScore).toFixed(2)}</span>}
              </div>
            </div>
          );
        })}
      </>)}

      {/* ── Results Tab ── */}
      {activeTab === "results" && (<>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <span style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{results.length} 条记录</span>
          <Btn onClick={() => { setEditResult({ ...emptyResult }); setEditFilename(null); }}>+ 新增</Btn>
        </div>
        {editResult && (
          <div className="card" style={{ marginBottom: "1.5rem", padding: "1.2rem" }}>
            <h3 style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "1rem" }}>{editFilename ? "编辑记录" : "新增记录"}</h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem" }}>
              <Field label="Framework" value={editResult.framework} onChange={(v) => setEditResult({ ...editResult, framework: v })} half />
              <Field label="Model" value={editResult.model} onChange={(v) => setEditResult({ ...editResult, model: v })} half />
              <Field label="Overall" value={editResult.overall} type="number" onChange={(v) => setEditResult({ ...editResult, overall: +v })} half />
              <Field label="Task Completion" value={editResult.taskCompletion} type="number" onChange={(v) => setEditResult({ ...editResult, taskCompletion: +v })} half />
              <Field label="Efficiency" value={editResult.efficiency} type="number" onChange={(v) => setEditResult({ ...editResult, efficiency: +v })} half />
              <Field label="Security" value={editResult.security} type="number" onChange={(v) => setEditResult({ ...editResult, security: +v })} half />
              <Field label="Skills" value={editResult.skills} type="number" onChange={(v) => setEditResult({ ...editResult, skills: +v })} half />
              <Field label="UX" value={editResult.ux} type="number" onChange={(v) => setEditResult({ ...editResult, ux: +v })} half />
              <Field label="Test Tier" value={editResult.testTier || ""} onChange={(v) => setEditResult({ ...editResult, testTier: v })} half />
              <Field label="Display Name" value={editResult.agentProfile?.displayName || ""} onChange={(v) => setEditResult({ ...editResult, agentProfile: { ...editResult.agentProfile!, displayName: v } })} />
              <Field label="Skills Mode" value={editResult.agentProfile?.skillsMode || "vanilla"} onChange={(v) => setEditResult({ ...editResult, agentProfile: { ...editResult.agentProfile!, skillsMode: v } })} half />
              <Field label="Model Tier" value={editResult.agentProfile?.modelTier || ""} onChange={(v) => setEditResult({ ...editResult, agentProfile: { ...editResult.agentProfile!, modelTier: v } })} half />
              <Field label="Skills (逗号分隔)" value={editResult.agentProfile?.skills?.join(", ") || ""} onChange={(v) => setEditResult({ ...editResult, agentProfile: { ...editResult.agentProfile!, skills: v.split(",").map(s => s.trim()).filter(Boolean) } })} half />
              <Field label="MCP Servers (逗号分隔)" value={editResult.agentProfile?.mcpServers?.join(", ") || ""} onChange={(v) => setEditResult({ ...editResult, agentProfile: { ...editResult.agentProfile!, mcpServers: v.split(",").map(s => s.trim()).filter(Boolean) } })} half />
              <Field label="Absolute Gain" value={editResult.progressive?.absolute_gain || 0} type="number" onChange={(v) => setEditResult({ ...editResult, progressive: { ...editResult.progressive!, absolute_gain: +v } })} half />
              <Field label="Normalized Gain" value={editResult.progressive?.normalized_gain || 0} type="number" onChange={(v) => setEditResult({ ...editResult, progressive: { ...editResult.progressive!, normalized_gain: +v } })} half />
            </div>
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
              <Btn onClick={saveResult}>保存</Btn>
              <Btn onClick={() => { setEditResult(null); setEditFilename(null); }} variant="secondary">取消</Btn>
            </div>
          </div>
        )}
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Agent</th><th>Framework</th><th>Model</th><th>Overall</th><th>Tier</th><th style={{ textAlign: "right" }}>操作</th></tr></thead>
              <tbody>
                {results.map((r, i) => (
                  <tr key={r._filename || i}>
                    <td style={{ fontWeight: 500 }}>{r.agentProfile?.displayName || `${r.framework} / ${r.model}`}</td>
                    <td>{r.framework}</td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{r.model}</td>
                    <td><span className={`score ${r.overall >= 85 ? "score-high" : r.overall >= 70 ? "score-mid" : "score-low"}`}>{r.overall.toFixed(2)}</span></td>
                    <td><code style={{ fontSize: "0.72rem", padding: "0.1rem 0.4rem", background: "var(--bg-secondary)", borderRadius: "4px" }}>{r.testTier || "-"}</code></td>
                    <td style={{ textAlign: "right" }}>
                      <Btn onClick={() => { setEditResult({ ...r }); setEditFilename(r._filename || null); }} variant="secondary">编辑</Btn>{" "}
                      <Btn onClick={() => r._filename && deleteResult(r._filename)} variant="danger">删除</Btn>
                    </td>
                  </tr>
                ))}
                {results.length === 0 && <tr><td colSpan={6} style={{ textAlign: "center", padding: "2rem", color: "var(--text-tertiary)" }}>暂无数据，点击「新增」添加</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      </>)}

      {/* ── Skills Gain Tab ── */}
      {activeTab === "skills" && (<>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <span style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{skillsGain.length} 条记录</span>
          <Btn onClick={() => { setEditSkill({ ...emptySkillsGain }); setEditSkillIdx(null); }}>+ 新增</Btn>
        </div>
        {editSkill && (
          <div className="card" style={{ marginBottom: "1.5rem", padding: "1.2rem" }}>
            <h3 style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "1rem" }}>{editSkillIdx !== null ? "编辑记录" : "新增记录"}</h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem" }}>
              <Field label="Framework" value={editSkill.framework} onChange={(v) => setEditSkill({ ...editSkill, framework: v })} half />
              <Field label="Model" value={editSkill.model} onChange={(v) => setEditSkill({ ...editSkill, model: v })} half />
              <Field label="Vanilla 分数" value={editSkill.vanilla} type="number" onChange={(v) => setEditSkill({ ...editSkill, vanilla: +v })} half />
              <Field label="Curated 分数" value={editSkill.curated} type="number" onChange={(v) => setEditSkill({ ...editSkill, curated: +v })} half />
              <Field label="Native 分数" value={editSkill.native} type="number" onChange={(v) => setEditSkill({ ...editSkill, native: +v })} half />
            </div>
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
              <Btn onClick={saveSkillsGain}>保存</Btn>
              <Btn onClick={() => { setEditSkill(null); setEditSkillIdx(null); }} variant="secondary">取消</Btn>
            </div>
          </div>
        )}
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Framework</th><th>Model</th><th>Vanilla</th><th>Curated</th><th>Native</th><th>Gain</th><th style={{ textAlign: "right" }}>操作</th></tr></thead>
              <tbody>
                {skillsGain.map((s, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 500 }}>{s.framework}</td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{s.model}</td>
                    <td>{s.vanilla.toFixed(2)}</td>
                    <td>{s.curated.toFixed(2)}</td>
                    <td>{s.native.toFixed(2)}</td>
                    <td style={{ color: "var(--success)", fontWeight: 600 }}>+{(s.curated - s.vanilla).toFixed(2)}</td>
                    <td style={{ textAlign: "right" }}>
                      <Btn onClick={() => { setEditSkill({ ...s }); setEditSkillIdx(i); }} variant="secondary">编辑</Btn>{" "}
                      <Btn onClick={() => deleteSkillsGainEntry(i)} variant="danger">删除</Btn>
                    </td>
                  </tr>
                ))}
                {skillsGain.length === 0 && <tr><td colSpan={7} style={{ textAlign: "center", padding: "2rem", color: "var(--text-tertiary)" }}>暂无数据</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      </>)}

      {/* ── MoltBook Tab ── */}
      {activeTab === "moltbook" && (<>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <span style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{agents.length} 个 Agent</span>
          <Btn onClick={() => { setEditAgent({ ...emptyAgent }); setEditAgentId(null); }}>+ 新增</Btn>
        </div>
        {editAgent && (
          <div className="card" style={{ marginBottom: "1.5rem", padding: "1.2rem" }}>
            <h3 style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "1rem" }}>{editAgentId ? "编辑 Agent" : "新增 Agent"}</h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem" }}>
              <Field label="Claw ID" value={editAgent.clawId} onChange={(v) => setEditAgent({ ...editAgent, clawId: v })} half />
              <Field label="Display Name" value={editAgent.displayName} onChange={(v) => setEditAgent({ ...editAgent, displayName: v })} half />
              <Field label="Framework" value={editAgent.framework} onChange={(v) => setEditAgent({ ...editAgent, framework: v })} half />
              <Field label="Model" value={editAgent.model} onChange={(v) => setEditAgent({ ...editAgent, model: v })} half />
              <Field label="Submitter" value={editAgent.submitter || ""} onChange={(v) => setEditAgent({ ...editAgent, submitter: v })} half />
              <Field label="Model Tier" value={editAgent.modelTier || ""} onChange={(v) => setEditAgent({ ...editAgent, modelTier: v })} half />
            </div>
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
              <Btn onClick={saveAgent}>保存</Btn>
              <Btn onClick={() => { setEditAgent(null); setEditAgentId(null); }} variant="secondary">取消</Btn>
            </div>
          </div>
        )}
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Claw ID</th><th>Display Name</th><th>Framework</th><th>Model</th><th>Submitter</th><th>Runs</th><th style={{ textAlign: "right" }}>操作</th></tr></thead>
              <tbody>
                {agents.map((a) => (
                  <tr key={a.clawId}>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{a.clawId}</td>
                    <td style={{ fontWeight: 500 }}>{a.displayName}</td>
                    <td>{a.framework}</td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{a.model}</td>
                    <td>{a.submitter || "-"}</td>
                    <td>{a.runs?.length || 0}</td>
                    <td style={{ textAlign: "right" }}>
                      <Btn onClick={() => { setEditAgent({ ...a }); setEditAgentId(a.clawId); }} variant="secondary">编辑</Btn>{" "}
                      <Btn onClick={() => deleteAgent(a.clawId)} variant="danger">删除</Btn>
                    </td>
                  </tr>
                ))}
                {agents.length === 0 && <tr><td colSpan={7} style={{ textAlign: "center", padding: "2rem", color: "var(--text-tertiary)" }}>暂无数据</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      </>)}

      {/* ── Config Tab ── */}
      {activeTab === "config" && (<>
        {([
          { name: "domains", label: "领域配置 (domains.json)", value: configDomains, setter: setConfigDomains },
          { name: "models", label: "模型配置 (models.json)", value: configModels, setter: setConfigModels },
          { name: "capabilities", label: "能力配置 (capabilities.json)", value: configCapabilities, setter: setConfigCapabilities },
        ] as const).map(({ name, label, value, setter }) => (
          <div key={name} className="card" style={{ marginBottom: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
              <h3 style={{ fontSize: "0.9rem", fontWeight: 600 }}>{label}</h3>
              <Btn onClick={() => saveConfig(name, value)}>保存</Btn>
            </div>
            <textarea
              value={value}
              onChange={(e) => setter(e.target.value)}
              style={{
                width: "100%", minHeight: "200px", padding: "0.75rem",
                border: "1px solid var(--border)", borderRadius: "6px",
                fontFamily: "var(--font-mono)", fontSize: "0.78rem",
                background: "var(--bg)", color: "var(--text)",
                resize: "vertical", lineHeight: 1.5,
              }}
            />
          </div>
        ))}
      </>)}

      {/* ── Experts Tab ── */}
      {activeTab === "experts" && (<>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <span style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{experts.length} 个专家账号</span>
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
            <input type="number" min={1} max={50} value={newInviteCount} onChange={(e) => setNewInviteCount(+e.target.value)}
              style={{ width: "50px", padding: "0.3rem", border: "1px solid var(--border)", borderRadius: "4px", fontSize: "0.8rem" }} />
            <Btn onClick={adminGenerateInvites}>生成邀请码</Btn>
          </div>
        </div>

        {/* Expert accounts table */}
        <div className="card" style={{ padding: 0, overflow: "hidden", marginBottom: "1.5rem" }}>
          <div className="table-wrap">
            <table>
              <thead><tr><th>用户名</th><th>显示名</th><th>邮箱</th><th>机构</th><th>角色</th><th>提案数</th><th>邀请数</th><th>状态</th><th>注册时间</th><th style={{ textAlign: "right" }}>操作</th></tr></thead>
              <tbody>
                {experts.map((e, i) => (
                  <tr key={String(e.username) || i}>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{String(e.username)}</td>
                    <td style={{ fontWeight: 500 }}>{String(e.displayName || "")}</td>
                    <td style={{ fontSize: "0.78rem" }}>{String(e.email || "-")}</td>
                    <td style={{ fontSize: "0.78rem" }}>{String(e.organization || "-")}</td>
                    <td>
                      <select value={String(e.role || "expert")} onChange={(ev) => changeExpertRole(String(e.username), ev.target.value)}
                        style={{ fontSize: "0.72rem", padding: "0.15rem 0.3rem", border: "1px solid var(--border)", borderRadius: "4px" }}>
                        <option value="expert">expert</option>
                        <option value="senior">senior</option>
                        <option value="reviewer">reviewer</option>
                      </select>
                    </td>
                    <td style={{ textAlign: "center" }}>{String(e.proposalCount || 0)}</td>
                    <td style={{ textAlign: "center" }}>{String(e.inviteCodesGenerated || 0)}</td>
                    <td>
                      <span style={{ fontSize: "0.72rem", padding: "0.1rem 0.4rem", borderRadius: "4px",
                        background: e.status === "active" ? "rgba(76,175,80,0.1)" : "rgba(244,67,54,0.1)",
                        color: e.status === "active" ? "var(--success)" : "var(--danger)" }}>
                        {String(e.status)}
                      </span>
                    </td>
                    <td style={{ fontSize: "0.72rem", color: "var(--text-tertiary)" }}>{String(e.registeredAt || "").split("T")[0]}</td>
                    <td style={{ textAlign: "right" }}>
                      <Btn onClick={() => toggleExpertStatus(String(e.username), String(e.status))} variant="secondary">
                        {e.status === "active" ? "禁用" : "启用"}
                      </Btn>{" "}
                      <Btn onClick={() => deleteExpert(String(e.username))} variant="danger">删除</Btn>
                    </td>
                  </tr>
                ))}
                {experts.length === 0 && <tr><td colSpan={10} style={{ textAlign: "center", padding: "2rem", color: "var(--text-tertiary)" }}>暂无专家账号</td></tr>}
              </tbody>
            </table>
          </div>
        </div>

        {/* Invite codes */}
        <div className="card" style={{ padding: "1.5rem" }}>
          <h3 style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "0.75rem" }}>邀请码管理 ({allInviteCodes.length} total)</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.3rem", maxHeight: "300px", overflow: "auto" }}>
            {allInviteCodes.map((inv, i) => (
              <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.35rem 0.6rem", background: "var(--bg-secondary)", borderRadius: "4px", fontSize: "0.78rem" }}>
                <code style={{ fontFamily: "var(--font-mono)", color: inv.used ? "var(--text-tertiary)" : "var(--accent)", textDecoration: inv.used ? "line-through" : "none" }}>
                  {String(inv.code)}
                </code>
                <span style={{ color: "var(--text-tertiary)" }}>
                  {inv.used ? `已使用: ${inv.usedBy} (${String(inv.usedAt || "").split("T")[0]})` : `可用 · 创建者: ${inv.createdBy}`}
                </span>
              </div>
            ))}
            {allInviteCodes.length === 0 && <p style={{ color: "var(--text-tertiary)", textAlign: "center", padding: "1rem" }}>暂无邀请码</p>}
          </div>
        </div>
      </>)}
    </div>
  );
}
