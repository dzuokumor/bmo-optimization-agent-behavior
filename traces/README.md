# Published traces

This directory contains the reviewed evidence bundle for the completed local
model runs. It includes 73 substantive trials across the baseline, capability,
time-pressure, replicate, and explicit-benchmark conditions.

Each run directory contains:

- `agent/trajectory.json`: structured Harbor trajectory;
- `agent/interaction.log`: model/tool interaction stream with host setup noise removed when emitted;
- `result.public.json`: selected trial metadata and reward;
- `verifier/reward.txt`: verifier outcome when emitted;
- `metadata.json`: condition mapping and redaction record;
- `trace-index.json`: file hashes for the published run bundle.

The traces document the local model lane. The public task fixtures and
OpenRouter runner are the reproduction route; the local host launcher and its
authentication environment are not part of this repository.

OpenRouter free-model smoke tests, network canaries, oracle-only runs, and
unexecuted conditions are excluded from this bundle.
