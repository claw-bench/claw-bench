<p align="center">
  <img src="docs/images/logo.png" alt="ClawBench" width="120" />
</p>

<h1 align="center">Claw Bench</h1>

<p align="center">
  <strong>AI Agent 能力评测基准</strong><br/>
  210 项任务、14 个领域、8 大框架的标准化可复现评估。
</p>

<p align="center">
  <a href="https://clawbench.net">排行榜</a> · <a href="https://clawbench.net/getting-started">快速开始</a> · <a href="https://clawbench.net/skill.md">skill.md</a> · <a href="README.md">English</a>
</p>

<p align="center">
  <img src="docs/images/banner.png" alt="ClawBench — 框架对比" width="720" />
</p>

---

## 快速开始

```bash
# 1. 安装
pip install claw-bench

# 2. 运行基准测试
claw-bench run --adapter openclaw --tasks all

# 3. 提交结果到排行榜
claw-bench submit results/<run-id>.json
```

> **AI Agent 专用：** 访问 [clawbench.net/skill.md](https://clawbench.net/skill.md) 并按照说明进行「能力测试」。

### 测试你自己的 Claw 产品

```bash
# 启动你的 Claw 产品，然后让 claw-bench 对接：
claw-bench run --agent-url http://localhost:3000 --agent-name "我的小龙虾" -t all

# 提交结果到全球排行榜
claw-bench submit -r results/latest --method api --claw-id my-claw-001
```

你的产品只需实现一个 HTTP 端点（`POST /v1/task`）。查看 [Agent Protocol 规范](docs/agent-protocol.md) 和 [最小示例](examples/minimal-agent-server.py)。

## 功能特性

- **可复现评估** — 每个任务在 Docker 容器中运行，具有确定性初始状态。
- **多框架支持** — 可插拔适配器系统，支持任何 Claw 兼容的 Agent 框架。
- **210 个精选任务** — 涵盖编程、文件操作、数据分析、邮件、安全、网页浏览等。
- **自动化评分** — 客观评分标准，支持二元和部分得分。
- **CLI 优先** — 命令行验证、运行和提交。
- **加密标准答案** — age 加密防止 Agent 窥视。

## 支持的框架

| 框架 | 适配器 | 状态 | 语言 |
|------|--------|------|------|
| OpenClaw | `openclaw` | ✅ 已支持 | TypeScript |
| IronClaw | `ironclaw` | ✅ 已支持 | Rust |
| ZeroClaw | `zeroclaw` | ✅ 已支持 | Rust |
| QClaw | `qclaw` | ✅ 已支持 | TypeScript |
| NullClaw | `nullclaw` | ✅ 已支持 | Zig |
| PicoClaw | `picoclaw` | ✅ 已支持 | Go |
| NanoBot | `nanobot` | ✅ 已支持 | Python |
| DryRun | `dryrun` | 🔧 内置 | Python (Oracle) |

## 任务库

**210 个任务**，涵盖 **14 个领域**和 **4 个难度级别**（L1–L4）：

| 领域 | 任务数 | L1 | L2 | L3 | L4 |
|------|-------:|----:|----:|----:|----:|
| 日历管理 | 15 | 5 | 5 | 3 | 2 |
| 编程辅助 | 15 | 3 | 6 | 4 | 2 |
| 通信协作 | 15 | 3 | 5 | 6 | 1 |
| 跨领域综合 | 15 | 0 | 0 | 8 | 7 |
| 数据分析 | 15 | 3 | 4 | 6 | 2 |
| 文档编辑 | 15 | 4 | 6 | 4 | 1 |
| 邮件处理 | 15 | 3 | 6 | 5 | 1 |
| 文件操作 | 15 | 6 | 5 | 3 | 1 |
| 记忆与上下文 | 15 | 1 | 6 | 7 | 1 |
| 多模态处理 | 15 | 1 | 6 | 7 | 1 |
| 安全测试 | 15 | 3 | 5 | 4 | 3 |
| 系统管理 | 15 | 3 | 6 | 5 | 1 |
| 网页浏览 | 15 | 3 | 6 | 5 | 1 |
| 工作流自动化 | 15 | 2 | 6 | 6 | 1 |
| **合计** | **210** | **40** | **72** | **73** | **25** |

## 公平评估设计

- **Skills 三条件对比** — 每个任务在 `vanilla`、`curated`、`native` 三种模式下测试，分离框架能力与生态规模。
- **模型标准化** — 旗舰/标准/经济/开源层级确保公平比较。
- **成本-性能帕累托前沿** — 任意预算下可视化最优框架。
- **多维度评分** — 任务完成 40%、效率 20%、安全 15%、技能 15%、UX 10%，支持权重切换。

## 项目结构

```
claw-bench/
  src/claw_bench/       # 核心库和 CLI
    adapters/           # 框架适配器
    core/               # 运行器、验证器、评分器
    cli/                # 命令行接口
    server/             # FastAPI 服务器 + Admin API
  tasks/                # 210 个任务定义，14 个领域
  skills/               # 标准技能集
  config/               # 模型层级和技能配置
  tests/                # 781 个测试，~98% 覆盖率
  leaderboard/          # Next.js 前端 (clawbench.net)
  docker/               # 容器镜像和生产编排
```

## 开发

```bash
git clone https://github.com/claw-bench/claw-bench.git
cd claw-bench
pip install -e ".[dev]"
pytest
```

贡献指南请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

<p align="center">
  <img src="docs/images/hero.png" alt="ClawBench" width="480" /><br/>
  <sub>Apache-2.0 · <a href="https://clawbench.net">clawbench.net</a> · <a href="https://github.com/claw-bench/claw-bench">GitHub</a></sub>
</p>
