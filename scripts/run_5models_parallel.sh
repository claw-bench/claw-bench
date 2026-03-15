#!/usr/bin/env bash

export OPENAI_COMPAT_BASE_URL="https://cloud.infini-ai.com/maas/v1"
export OPENAI_COMPAT_API_KEY="sk-l7cfssebep2nfkwn"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BASE_OUTPUT="./results/benchmark-${TIMESTAMP}"
LOG_DIR="${BASE_OUTPUT}/logs"
mkdir -p "$LOG_DIR"

echo "======================================"
echo "Claw Bench - 5 Model PARALLEL Run"
echo "Timestamp: $TIMESTAMP"
echo "Output:    $BASE_OUTPUT"
echo "======================================"

launch_model() {
  local model="$1"
  local safe_name="${model//\//-}"
  local output_dir="${BASE_OUTPUT}/${safe_name}"
  local log_file="${LOG_DIR}/${safe_name}.log"

  echo ">>> Launching: $model at $(date '+%H:%M:%S')"

  claw-bench run \
    --framework openclaw \
    --model "$model" \
    --tasks all \
    --runs 1 \
    --parallel 1 \
    --timeout 180 \
    --output "$output_dir" \
    > "$log_file" 2>&1

  local exit_code=$?
  echo "DONE: $model - exit=$exit_code at $(date '+%H:%M:%S')"
  return $exit_code
}

launch_model "deepseek-v3" &
PID1=$!
launch_model "qwen3-235b-a22b" &
PID2=$!
launch_model "claude-sonnet-4-6" &
PID3=$!
launch_model "gpt-5.4" &
PID4=$!
launch_model "glm-4.6" &
PID5=$!

echo ""
echo "All 5 models launched: PIDs $PID1 $PID2 $PID3 $PID4 $PID5"
echo "Waiting for completion..."

FAILED=0
for pid in $PID1 $PID2 $PID3 $PID4 $PID5; do
  if ! wait $pid; then
    FAILED=$((FAILED + 1))
  fi
done

echo ""
echo "======================================"
echo "All models completed at $(date '+%H:%M:%S')"
echo "Failed: $FAILED / 5"
echo "Results in: $BASE_OUTPUT"
echo "======================================"
