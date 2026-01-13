# LLM Reliability Lab (MVP)

A production-style SRE sandbox that serves an LLM endpoint, injects failures, tracks SLOs, emits Prometheus metrics, and auto-heals on incidents.

## 🎯 Goals
- Demonstrate SRE fundamentals applied to inference endpoints
- Instrument SLIs: latency, availability, error rate, GPU utilization
- Run chaos tests and automated remediation
- AI-assisted development with human review and safety guardrails

## �️ Architecture
- **LLM Service**: Ollama running `smollm`
- **API Service**: FastAPI wrapper with instrumentation
- **Monitoring**: Prometheus (metrics) + Grafana (visualization)

## �📊 SLIs (out of the box)
| SLI | Captured Metric |
|---|---|
| Latency | `llm_request_latency_seconds_bucket` (histogram) |
| Availability | `llm_request_total` + `llm_request_errors_total` |
| Error Rate | `llm_request_errors_total` |
| GPU Utilization | `llm_gpu_utilization_percent` (simulated) |
| Saturation | `llm_inference_in_flight` |

## 🏁 SLO
See **SLO.md**

## 🚨 Alerts + Remediation
Alerts trigger container restarts via the remediation script.

## 🚀 Quick Start
1. Start the stack:
   ```bash
   docker compose up --build -d
   ```

2. Run chaos experiments (optional):
   ```bash
   python chaos.py
   ```

3. Run remediation (optional):
   ```bash
   ./remediate.sh
   ```

## 📈 Monitoring
The project includes a pre-configured monitoring stack:

- **Prometheus**: [http://localhost:9090](http://localhost:9090)
  - Scrapes metrics from the API service and itself.
- **Grafana**: [http://localhost:3000](http://localhost:3000)
  - **Login**: `admin` / `admin`
  - **Dashboards**: The "LLM Reliability (MVP)" dashboard is automatically provisioned and ready to view.

## 🧪 Testing
To run the test suite (including infrastructure tests):

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest
```

## ⚠️ Security
- No secrets in plaintext
- Uses environment variables (see `.env.example`)
- Always key-rotate before production reuse
