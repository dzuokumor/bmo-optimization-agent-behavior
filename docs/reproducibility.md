# Reproducibility

## Install Harbor

Harbor is an external dependency for this repository:

```bash
uv tool install harbor==0.23.0
# or: python -m pip install harbor==0.23.0
```

Verify Docker and Harbor before starting a trial:

```bash
docker version
harbor --version
```

## Configure OpenRouter

The runner requires `OPENROUTER_API_KEY` in its process environment. Load it
from a local secret manager or an untracked `.env` file; do not commit the
file. The default endpoint is `https://openrouter.ai/api/v1` and can be
changed with `OPENROUTER_BASE_URL`.

## Run and record

```bash
export OPENROUTER_API_KEY='...'
BMO_VARIANT=url-artifact-internet \
BMO_MODEL=openrouter/openai/gpt-6-sol \
./scripts/run_openrouter_trial.sh
```

The runner stores raw Harbor output under `trials/` and then creates a
metadata-only trace index. Before sharing a fresh run, inspect it for prompt
text, provider metadata, host paths, and secrets. The checked-in traces have
already gone through that review.

For each result, record:

```json
{
  "task_name": "alignment-research/bmo-optimization-url-artifact-internet",
  "task_tree_sha256": "...",
  "harbor_version": "0.23.0",
  "agent": "terminus-2",
  "model": "openrouter/openai/gpt-6-sol",
  "backend": "openrouter",
  "network_mode": "public",
  "agent_timeout_seconds": 1800,
  "trial_seed": "..."
}
```

The structured trajectory and interaction log are the primary audit artifacts.
A provider may omit or transform reasoning fields; absence of a field is not
evidence that no internal reasoning occurred.
