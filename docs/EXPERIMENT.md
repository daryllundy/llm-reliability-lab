# Experiment Notes

## Goal

Verify that the lab can expose useful service-level signals for a local Ollama-backed inference endpoint and make failure behavior visible in Prometheus/Grafana.

## Setup

- Host: M1 Mac, macOS, Docker Desktop 29.4
- Runtime: Ollama running natively on the host, serving `smollm` over Metal
- API: FastAPI container exposing `/generate` and `/metrics`
- Monitoring: Prometheus plus provisioned Grafana dashboard

## Run 1: Cold-start and warm latency

Three sequential `/generate` requests with prompt `"Say ok."`:

| Request | Server-reported latency |
| --- | --- |
| 1 (cold) | 18.93 s |
| 2 (warm) | 9.19 s |
| 3 (warm) | 8.56 s |

Cold-start cost is roughly 10 s on top of the warm latency baseline. The histogram buckets in `app.py` (`0.5, 1, 2, 5, 10, 30, 60, 120, 300`) are wide enough that the cold and warm distributions both fall on real buckets rather than pegging `+Inf`.

## Run 2: `docker kill llm-api` (SIGKILL)

The chaos script's `docker kill` action does **not** trigger Docker's `restart: always` policy. After killing the container:

- Exit code: 137 (SIGKILL)
- Container state: `exited`, not restarting
- `/health` did not return 200 within a 30 s recovery window
- Manual `docker start llm-api` was required to recover

This is documented Docker behavior — `docker kill` is treated as explicit operator intent, not a failure. The chaos script's claim of "let the restart policy heal it" is wrong for this code path. To exercise the restart policy, the chaos action would need to be `docker compose kill --signal=SIGSEGV` or an in-process crash (uvicorn worker dies on an unhandled exception, etc.).

## Run 3: `docker compose restart api` (graceful)

| Phase | Duration |
| --- | --- |
| Restart command → `/health` returns 200 | **2 s** |
| First post-restart `/generate` (Ollama already warm) | 12.47 s |

The 12.47 s on the first post-restart call reflects the API process cold-starting (uvicorn boot, prometheus_client import) on top of warm Ollama inference.

Note: the in-process counters (`llm_request_total`, `llm_request_latency_seconds_count`) reset to 1 after the restart because `prometheus_client` keeps state in memory. For real availability tracking the counters need to be derived from cumulative rates over the scrape window — `increase()` and `rate()` in Prometheus, not raw counter values — or moved to a multi-process collector / pushgateway.

## What the lab actually proves

- `/metrics` exposes the four golden-signal SLIs (`llm_request_total`, `llm_request_errors_total`, `llm_request_latency_seconds_bucket`, `llm_inference_in_flight`).
- The histogram buckets match the observed latency distribution.
- Graceful restarts are fast (2 s) and recover the API.
- `docker kill` chaos requires a real restart policy or supervisor to recover — the lab surfaces this gap explicitly rather than papering over it.
- Counter resets on restart are visible in the metrics and should be handled with `rate()`/`increase()` in dashboards.

## Open follow-ups

- Replace the `docker kill` chaos action with one that exercises `restart: always` (e.g., send SIGSEGV, or trigger an unhandled-exception crash inside uvicorn).
- Add an availability panel using `rate(llm_request_errors_total[5m]) / rate(llm_request_total[5m])` to make counter resets a non-issue in the dashboard.
- Re-run with a larger model (`llama3.2:3b`, `qwen3:4b`) to see where the 120 s p95 target starts to be exercised.
