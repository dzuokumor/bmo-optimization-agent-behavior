#!/usr/bin/env bash
set -euo pipefail

# The container starts before Harbor launches the agent. Keeping this marker
# in /run makes the timer available without a host-side clock or network.
date +%s > /run/bmo-environment-start-epoch
chmod 0444 /run/bmo-environment-start-epoch

exec "$@"
