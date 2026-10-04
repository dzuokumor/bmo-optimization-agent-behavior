# FrontierMath BMO optimization task family

This directory contains the self-contained Harbor fixtures for the BMO
optimization study. Each task has its own `task.toml`, instruction, LaTeX
problem, Dockerfile, verifier, and solution fixture.

The commented material in selected `problem.tex` files is an intentional
experimental variable. It is not mentioned in the task instruction. The
`solution/` directory is the Harbor oracle fixture and is not copied into the
agent container as part of normal task execution.

Network policy is declared in each `task.toml`:

- `no-network` for the agent and environment phases means the model has only
  the container filesystem and shell tools.
- `public` permits the container to make outbound connections during the agent
  phase.
- The verifier is `no-network` in every fixture.

Run through `scripts/run_openrouter_trial.sh`; it selects the fixture by
`BMO_VARIANT` and writes local traces under the ignored `trials/` directory.
