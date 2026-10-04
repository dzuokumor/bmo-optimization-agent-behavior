# Publication scope

This preview is the proposed GitHub contents for
`bmo-optimization-agent-behavior`.

## Included

| Path | Purpose |
| --- | --- |
| `experiments/` | Harbor task definitions, environment images, instructions, verifier fixtures, and solution fixtures. |
| `scripts/run_openrouter_trial.sh` | OpenRouter-only Harbor launcher. |
| `scripts/index_trial_traces.py` | Metadata-only trace indexer. |
| `scripts/validate_tasks.py` | Static and Harbor-backed task validation. |
| `scripts/render_tex.sh` | Optional local rendering of a task's LaTeX source. |
| `scripts/plot_results.py` | Regenerates descriptive figures from the published trace metadata. |
| `docs/` | Reproduction instructions, condition definitions, and this scope document. |
| `traces/` | Reviewed local-run trajectories, interaction logs, verifier rewards, and normalized metadata. |
| `renders/` | Reviewed result plots and a PNG of the typeset mathematical problem. |
| `pyproject.toml` | Minimal project metadata and lint settings. |
| `.gitignore` | Prevents credentials and generated run data from entering Git. |

## Ignored or excluded

| Item | Reason |
| --- | --- |
| `trials/`, `results/`, `artifacts/`, and other generated renders | Generated outputs from fresh runs. |
| `research_journal.md` | Private working notes, not part of the public artifact. |
| `.env`, `auth.json`, proxy settings, and host environment dumps | Credentials and machine-specific configuration. |
| Local host launchers and integrations | The public release uses the documented Harbor/OpenRouter path. |
| Vendored Harbor and Terminal-Bench source trees | Install Harbor externally at the documented version. |
| Unreviewed raw host logs and traces | Only the reviewed bundle under `traces/` is published. |

The task fixtures intentionally retain their commented solution or URL
payloads. Those payloads are the experimental treatment, while the task
instruction does not tell the agent to use them.

## Reproducibility boundary

A public reproduction recreates the task package, Harbor phase policies, model
identifier, and runner settings through OpenRouter. The published traces
document the local model lane but do not publish its host launcher,
authentication path, or provider account state. Each result should record the
task tree hash, Harbor version, model identifier, endpoint class, network
policy, timeout, and trial seed.
