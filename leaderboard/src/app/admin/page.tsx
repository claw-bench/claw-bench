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

const emptyResult: Result = {
  framework: "", model: "", overall: 0, taskCompletion: 0, efficiency: 0,
  security: 0, skills: 0, ux: 0, testTier: "comprehensive",
  agentProfile: { displayName: "", model: "", framework: "", skillsMode: "vanilla", skills: [], mcpServers: [], memoryModules: [], modelTier: "flagship", tags: {} },
  progressive: { baseline_pass_rate: 0, current_pass_rate: 0, absolute_gain: 0, normalized_gain: 0 },
};

const emptySkillsGain: SkillsGainEntry = { framework: "", model: "", vanilla: 0, curated: 0, native: 0 };

const emptyAgent: MoltBookAgent = { clawId: "", displayName: "", framework: "", model: "", submitter: "", modelTier: "flagship", runs: [] };

type Tab = "pending" | "results" | "skills" | "moltbook" | "config";

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
  children: React.ReactNode; onClick: () => void; variant?: "primary" | "secondary" | "danger"; disabled?: boolean;
}) => {
  const styles: Record<string, React.CSSProperties> = {
    primary: { background: "var(--accent)", color: "#fff", border: "none" },
    secondary: { background: "transparent", color: "var(--text-secondary)", border: "1px solid var(--border)" },
    danger: { background: "transparent", color: "var(--danger)", border: "1px solid var(--danger)" },
  };
  return (
    <button onClick={onClick} disabled={disabled}
      style={{ padding: "0.4rem 1rem", borderRadius: "6px", fontWeight: 500, fontSize: "0.8rem", cursor: disabled ? "wait" : "pointer", opacity: disabled ? 0.6 : 1, ...styles[variant] }}>
      {children}
    </button>
  );
};

/* ── Main ───────────────────────────────────────────────────────── */

export default function AdminPage() {
  const [token, setToken] = useState<string | null>(null);
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [activeTab, setActiveTab] = useState<Tab>("pending");
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

  const headers = useCallback(() => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" }), [token]);
  const showMsg = (m: string) => { setMessage(m); setTimeout(() => setMessage(""), 3000); };

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

  useEffect(() => { if (token) { loadPending(); loadResults(); loadSkillsGain(); loadAgents(); loadConfig(); } }, [token, loadPending, loadResults, loadSkillsGain, loadAgents, loadConfig]);

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
          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>管理排行榜全部数据 · 修改后点击「重建前端」生效</p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <Btn onClick={triggerRebuild} disabled={rebuilding}>{rebuilding ? "重建中..." : "重建前端"}</Btn>
          <Btn onClick={() => { sessionStorage.removeItem("admin_token"); setToken(null); }} variant="secondary">退出</Btn>
        </div>
      </div>

      {message && <div style={{ padding: "0.6rem 1rem", background: "var(--accent-light)", border: "1px solid var(--accent)", borderRadius: "6px", marginBottom: "1rem", fontSize: "0.82rem", color: "var(--accent)", fontWeight: 500 }}>{message}</div>}

      {/* Tabs */}
      <div style={{ display: "flex", gap: "0.4rem", marginBottom: "1.5rem", borderBottom: "1px solid var(--border)", paddingBottom: "0.5rem" }}>
        {([["pending", `待审核 (${pending.length})`], ["results", "排行榜数据"], ["skills", "技能增益"], ["moltbook", "身份册"], ["config", "配置管理"]] as [Tab, string][]).map(([key, label]) => (
          <button key={key} onClick={() => setActiveTab(key)}
            style={{ padding: "0.4rem 1rem", border: "none", borderRadius: "6px", background: activeTab === key ? "var(--accent)" : "transparent", color: activeTab === key ? "#fff" : "var(--text-secondary)", fontWeight: 500, fontSize: "0.82rem", cursor: "pointer" }}>
            {label}
          </button>
        ))}
      </div>

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
                    {region.flag || "🌍"} {(profile.displayName as string) || `${p.framework} / ${p.model}`}
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
    </div>
  );
}
