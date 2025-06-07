#!/usr/bin/env bash
# A formatting script helping to follow lint-standards.
set -eux

black --line-length=120 simod controller agent_simulator
isort --profile=black --line-length=120 --force-single-line-imports simod controller agent_simulator