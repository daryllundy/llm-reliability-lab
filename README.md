# LLM Reliability Lab

A small SRE lab for treating a local LLM endpoint like a service: FastAPI wraps Ollama, Prometheus scrapes service metrics, Grafana provisions a dashboard, and helper scripts inject faults or trigger remediation.

The default setup is optimized for Apple Silicon Macs: run Ollama natively on macOS for Metal acceleration, then run the API, Prometheus, and Grafana in Docker.

## Architecture

- Ollama serves the model on the host machine.
- FastAPI exposes `/generate`, `/health`, and `/metrics`.
- Prometheus scrapes the API metrics endpoint.
- Grafana loads the Prometheus datasource and dashboard from provisioning files.

## Ollama Setup

Install Ollama for macOS from the official app: [docs.ollama.com/macos](https://docs.ollama.com/macos).

Start Ollama so Docker containers can reach it:

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

Pull the default model:

```bash
ollama pull smollm
```

Smoke test native Ollama:

```bash
curl http://localhost:11434/api/generate \
  -d '{"model":"smollm","prompt":"Say ok.","stream":false}'
```

Model choices that work well on an M1 Mac Studio with 32 GB memory:

| Model | Use case |
| --- | --- |
| `smollm` | Fast default lab model; good for reliability loops and short prompts. |
| `llama3.2` or `llama3.2:3b` | Stronger small general model with reasonable local latency. |
| `qwen3:4b` | Good quality/speed tradeoff. |
| `qwen3:8b` | Higher quality, still practical on 32 GB, but slower. |

Large 30B+ models are intentionally not the default because this lab is designed for repeatable local reliability testing, not maximum model quality.

## Run The Lab

Start the monitoring stack and API:

```bash
MODEL_NAME=smollm docker compose up --build
```

Open:

- API health: [http://localhost:8000/health](http://localhost:8000/health)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3000](http://localhost:3000)

Grafana uses `admin` / `admin` by default for local development only. Override it with:

```bash
GRAFANA_ADMIN_PASSWORD='change-me' docker compose up --build
```

To use Dockerized Ollama instead of native macOS Ollama:

```bash
docker compose --profile docker-ollama up --build
```

Native Ollama is the recommended Apple Silicon path; Dockerized Ollama is useful for portability but is usually slower on an M1 Mac.

## Metrics

The API exports Prometheus metrics for:

| SLI | Metric |
| --- | --- |
| Request volume | `llm_request_total` |
| Errors | `llm_request_errors_total` |
| Latency | `llm_request_latency_seconds_bucket` |
| Saturation | `llm_inference_in_flight` |
| Simulated accelerator load | `llm_gpu_utilization_percent` |

The `/generate` endpoint sends `stream: false` to Ollama so the latency histogram measures a completed generation response.

## Chaos And Remediation

Run the chaos loop manually:

```bash
python chaos.py
```

Run the remediation loop:

```bash
./remediate.sh
```

When native Ollama is used, the remediation script reports high latency and leaves restart control to the host process. When Dockerized Ollama is used, enable container remediation:

```bash
USE_DOCKER_OLLAMA=true ./remediate.sh
```

Tuning knobs:

```bash
LATENCY_THRESHOLD_SECONDS=30 REMEDIATION_COOLDOWN_SECONDS=120 ./remediate.sh
```

## Tests

```bash
pip install -r requirements.txt pytest ruff
PYTHONPATH=. pytest
ruff check .
```

See [docs/SLO.md](docs/SLO.md) for local lab targets and [docs/EXPERIMENT.md](docs/EXPERIMENT.md) for the current experiment notes.
