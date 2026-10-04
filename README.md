# BMO Optimization: Agent Behavior Under Solution Artifacts

This repository contains reproducible Harbor environments for studying how
language-model agents behave when a mathematical task contains an incidental
solution artifact. The first task family is a difficult BMO optimization
problem from the FrontierMath benchmark. The artifact is placed in a LaTeX
source file and is not described in the task instruction.

The reproduction route is **Harbor + OpenRouter**.

## What is included

- Self-contained Harbor task fixtures under
  `experiments/frontiermath/bmo-optimization/`.
- Answer-artifact, URL-artifact, clean-control, network, and time-budget
  variants.
- A runner for Harbor's `terminus-2` agent through an OpenRouter-compatible
  endpoint.
- A reviewed trace bundle for the completed local trials.
- Task validation, trace indexing, and optional LaTeX rendering utilities.
- Documentation.

See [`docs/publication-scope.md`](docs/publication-scope.md) for the complete
include/ignore policy.

## Requirements

- Docker with the Docker Engine API available to Harbor.
- Python 3.12 or newer.
- [`uv`](https://docs.astral.sh/uv/) or `pip`.
- An OpenRouter API key. The key is read from the process environment.
- Harbor **0.23.0**, the version used to validate this release.

Install Harbor separately; it is intentionally not vendored here:

```bash
uv tool install harbor==0.23.0
# or: python -m pip install harbor==0.23.0
harbor --version
```

The fixtures were prepared against Harbor source revision
`bf991e490394ef9c3250a6db2bc5cbda903cb4c3`. A different Harbor release may
change trace fields or command-line behavior.

## Run one trial

From the repository root:

```bash
export OPENROUTER_API_KEY='your-key'
export BMO_VARIANT=answer-artifact
export BMO_MODEL=openrouter/openai/gpt-6-sol
./scripts/run_openrouter_trial.sh
```

Useful variants include:

```text
answer-artifact
url-artifact
url-artifact-internet
clean-control
url-artifact-internet-7m-frontier-source-cue
```

Override the model, budget-related Harbor options, endpoint, or output folder
with the `BMO_*` variables documented in the runner. Trial output is written to
`trials/`, which is ignored by Git.

## Network interpretation

`no-network` and `public` are properties of the Harbor task phases, not of the
OpenRouter request itself. In a `no-network` fixture the model's shell runs in
a network-restricted container while Harbor makes the provider request on the
host side. No host-integrated search tool is part of this public route. The
verifier is network-disabled for every fixture.

## Traces

The checked-in [`traces/`](traces/) directory contains 73 reviewed local-lane
trials, including structured trajectories, interaction streams, rewards, and
condition metadata. Host setup diagnostics and private paths were removed.
Fresh runs still write raw Harbor output under the ignored `trials/` directory;
the runner indexes partial output even when Harbor reports a timeout or other
nonzero status. Provider policies determine whether reasoning fields are
returned; this repository does not claim access to hidden chain-of-thought.

## Figures

The [results figure guide](docs/results-figures.md) shows pass-rate intervals,
individual trial outcomes, and selected condition contrasts. The figures are
generated directly from the published trace metadata by
[`scripts/plot_results.py`](scripts/plot_results.py).

## Citation

This work uses [Harbor](https://github.com/harbor-framework/harbor), the
framework from the Terminal-Bench authors. Please cite Harbor according to its
release instructions when publishing results. The mathematical source is
linked in the task fixture as an artifact variable; the repository does not bundle
a copy of the source website.
