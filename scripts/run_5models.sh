#!/usr/bin/env bash
set -euo pipefail

export OPENAI_COMPAT_BASE_URL="https://cloud.infini-ai.com/maas/v1"
export OPENAI_COMPAT_API_KEY="sk-l7cfssebep2nfkwn"

MODELS=(
  "deepseek-v3"
  "qwen3-235b-a22b"
  "claude-sonnet-4-6"
  "gpt-5.4"
  "glm-4.6"
)

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BASE_OUTPUT="./results/benchmark-${TIMESTAMP}"
LOG_DIR="${BASE_OUTPUT}/logs"
mkdir -p "$LOG_DIR"

echo "======================================"
echo "Claw Bench - 5 Model Benchmark Run"
echo "Timestamp: $TIMESTAMP"
echo "Output:    $BASE_OUTPUT"
echo "======================================"

for model in "${MODELS[@]}"; do
  safe_name="${model//\//-}"
  output_dir="${BASE_OUTPUT}/${safe_name}"
  log_file="${LOG_DIR}/${safe_name}.log"

  echo ""
  echo ">>> Starting: $model"
  echo "    Output:   $output_dir"
  echo "    Log:      $log_file"
  echo "    Time:     $(date '+%H:%M:%S')"

  if claw-bench run \
    --framework openclaw \
    --model "$model" \
    --tasks all \
    --runs 1 \
    --parallel 1 \
    --timeout 180 \
    --output "$output_dir" \
    > "$log_file" 2>&1; then
    echo "    Status:   COMPLETED"
  else
    echo "    Status:   FAILED (exit code $?)"
  fi

  echo "    Finished: $(date '+%H:%M:%S')"
done

echo ""
echo "======================================"
echo "All models completed at $(date '+%H:%M:%S')"
echo "Results in: $BASE_OUTPUT"
echo "======================================"
