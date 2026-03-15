#!/usr/bin/env bash
# quickstart.sh — Get up and running with Claw Bench in under 60 seconds.
#
# Usage:
#   curl -fsSL https://clawbench.net/quickstart.sh | bash
#   # or locally:
#   bash scripts/quickstart.sh
#   bash scripts/quickstart.sh --smoke deepseek-v3   # install + run 4 tasks
set -euo pipefail

MODEL="${2:-}"
MODE="${1:-}"

cat << 'BANNER'

   ██████╗██╗      █████╗ ██╗    ██╗    ██████╗ ███████╗███╗   ██╗ ██████╗██╗  ██╗
  ██╔════╝██║     ██╔══██╗██║    ██║    ██╔══██╗██╔════╝████╗  ██║██╔════╝██║  ██║
  ██║     ██║     ███████║██║ █╗ ██║    ██████╔╝█████╗  ██╔██╗ ██║██║     ███████║
  ██║     ██║     ██╔══██║██║███╗██║    ██╔══██╗██╔══╝  ██║╚██╗██║██║     ██╔══██║
  ╚██████╗███████╗██║  ██║╚███╔███╔╝    ██████╔╝███████╗██║ ╚████║╚██████╗██║  ██║
   ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝
  AI Agent Evaluation Benchmark — 210 tasks · 14 domains · L1–L4

BANNER

echo "==> [1/3] Installing claw-bench..."
pip install -e ".[dev]" --quiet 2>/dev/null || pip install git+https://github.com/claw-bench/claw-bench.git --quiet
echo "    ✓ Installed"

echo ""
echo "==> [2/3] Health check..."
claw-bench doctor
echo ""

echo "==> [3/3] Ready!"
echo ""

if [[ "$MODE" == "--smoke" && -n "$MODEL" ]]; then
    echo "==> Running smoke test with model: $MODEL"
    echo ""
    claw-bench run -m "$MODEL" -t file-001,code-002,cal-001,file-003 -n 1
    echo ""
fi

cat << 'USAGE'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Quick Reference
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # Smoke test (4 tasks, ~1 min)
  claw-bench run -m deepseek-v3 -t file-001,code-002,cal-001,file-003 -n 1

  # Test a domain (15 tasks)
  claw-bench run -m gemini-2.5-pro -t code-assistance

  # Full benchmark (210 tasks, ~30 min)
  claw-bench run -m claude-sonnet-4-5-20250929 -t all

  # Custom LLM provider
  export OPENAI_COMPAT_BASE_URL="https://cloud.infini-ai.com/maas/v1"
  export OPENAI_COMPAT_API_KEY="your-key"
  claw-bench run -m deepseek-v3 -t all

  # Compare with skills
  claw-bench skillsbench -f openclaw -m deepseek-v3 -t code-assistance

  # More commands
  claw-bench list tasks          # Browse 210 tasks
  claw-bench list frameworks     # Available adapters
  claw-bench doctor              # Diagnose issues
  claw-bench --help              # Full reference

  Docs: https://clawbench.net/skill.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE
