#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
variant="${BMO_VARIANT:-answer-artifact}"
task="$repo_root/experiments/frontiermath/bmo-optimization/$variant"
trials_dir="${BMO_TRIALS_DIR:-$repo_root/trials/openrouter-$variant}"
harbor_bin="${HARBOR_BIN:-harbor}"

[[ -d "$task" ]] || {
  echo "unknown BMO_VARIANT: $variant" >&2
  exit 2
}
command -v "$harbor_bin" >/dev/null 2>&1 || {
  echo "Harbor was not found. Install it with: uv tool install harbor==0.23.0" >&2
  exit 2
}
: "${OPENROUTER_API_KEY:?set OPENROUTER_API_KEY for the OpenRouter backend}"

mkdir -p "$trials_dir"
set +e
"$harbor_bin" trial start \
  --path "$task" \
  --trials-dir "$trials_dir" \
  --force-build \
  --agent terminus-2 \
  --model "${BMO_MODEL:-openrouter/openai/gpt-6-sol}" \
  --agent-kwarg "api_base=${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}" \
  --agent-kwarg "max_turns=${BMO_MAX_TURNS:-40}" \
  --agent-kwarg "reasoning_effort=${BMO_REASONING_EFFORT:-high}" \
  --agent-kwarg store_all_messages=true \
  --agent-kwarg record_terminal_session=true \
  --agent-kwarg 'trajectory_config={"raw_content":true,"linear_history":true}'
harbor_status=$?
set -e

# Index partial output as well as successful trials, then preserve Harbor's
# status for automation and batch analyses.
python3 "$repo_root/scripts/index_trial_traces.py" "$trials_dir" || true
exit "$harbor_status"
