# Service Level Objective

This is a local reliability lab, not a production GPU service. The default target assumes Ollama is running natively on an Apple Silicon Mac and serving a small local model such as `smollm`.

## Local Lab Targets

| Objective | Target |
| --- | --- |
| Availability | 99.0% successful `/generate` requests during a manual experiment window |
| Latency | p95 under 120 seconds for short prompts |
| Error rate | under 1% outside deliberate chaos windows |
| Recovery | failed API or Dockerized Ollama container returns after Compose restart policy or manual remediation |

The latency target is intentionally broad because local inference latency depends on model size, prompt length, cold-start state, and whether Ollama is running natively or in Docker.

## SLIs

- Availability: `llm_request_total` and `llm_request_errors_total`
- Latency: `llm_request_latency_seconds_bucket`
- Saturation: `llm_inference_in_flight`
- Simulated accelerator load: `llm_gpu_utilization_percent`

## Notes

For a real hosted inference service, define separate SLOs per model class and hardware profile. Do not reuse this local lab SLO for production GPU endpoints.
