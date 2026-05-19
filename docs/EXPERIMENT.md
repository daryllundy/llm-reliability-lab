# Experiment Notes

## Goal

Verify that the lab can expose useful service-level signals for a local Ollama-backed inference endpoint and make failure behavior visible in Prometheus/Grafana.

## Setup

- Host: local development machine
- Runtime: Ollama serving `smollm`
- API: FastAPI container exposing `/generate` and `/metrics`
- Monitoring: Prometheus plus provisioned Grafana dashboard

## Baseline Observation

Previous local runs showed large cold-start and warm-up effects:

| Request | Observed latency |
| --- | --- |
| 1 | 316.09 seconds |
| 2 | 146.79 seconds |
| 3 | 104.60 seconds |

Those numbers are not production SLO evidence. They show why this lab uses wide histogram buckets and why the SLO is scoped to local inference rather than a hosted GPU endpoint.

## Failure Modes To Exercise

- Kill the API container and confirm Docker restart policy restores `/health`.
- Kill the Dockerized Ollama container when running with `--profile docker-ollama`.
- Run `remediate.sh` and confirm it avoids rapid restart loops through cooldown.

## Acceptance Criteria

- `/metrics` exposes request count, error count, latency buckets, and in-flight request gauge.
- Grafana shows latency quantiles and request/error movement during experiments.
- Chaos runs only when `python chaos.py` is executed directly, not when the module is imported.
