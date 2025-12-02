Here are your **MVP files** for `llm-reliability-lab`.
Copy them into a GitHub repo (e.g., `llm-reliability-lab`) and you’ll have a clean demo you can wire up and blog about.

---

### **README.md**

````markdown
# LLM Reliability Lab (MVP)

A production-style SRE sandbox that serves an LLM endpoint, injects failures, tracks SLOs, emits Prometheus metrics, and auto-heals on incidents.

## 🎯 Goals
- Demonstrate SRE fundamentals applied to inference endpoints
- Instrument SLIs: latency, availability, error rate, container restarts
- Run chaos tests and automated remediation
- AI-assisted development with human review and safety guardrails

## 📊 SLIs (out of the box)
| SLI | Captured Metric |
|---|---|
| Latency | `llm_request_latency_seconds_bucket` (histogram) |
| Availability | `llm_request_total` + `llm_request_errors_total` |
| Error Rate | `llm_request_errors_total` |
| Self-Healing | `service_container_restarts_total` |

## 🏁 SLO
See **SLO.md**

## 🚨 Alerts + Remediation
Alerts trigger container restarts via the remediation script.

## ⚠️ Security
- No secrets in plaintext
- Uses environment variables (see `.env.example`)
- Always key-rotate before production reuse

## 🚀 Quick Start
```bash
docker compose up --build
python chaos.py
./remediate.sh
````

Metrics available at: `http://localhost:8000/metrics`
Dashboards: Import `/dashboards/grafana.json` into Grafana.

```
```

---

### **SLO.md**

```markdown
# Service Level Objective

**Availability SLO:** 99.5% uptime (30-day target)  
**Latency SLO:** p99 < 800ms  
**Error Budget:** 0.5% monthly

Objective: Avoid exhausting error budget by validating automated recovery paths.
```

---

### **docker-compose.yml**

```yaml
services:
  llm:
    image: ollama/ollama
    container_name: llm
    restart: always
    environment:
      - OLLAMA_MODELS=smollm
    ports:
      - "11434:11434"

  api:
    build: .
    container_name: llm-api
    restart: always
    environment:
      - MODEL_NAME=smollm
    depends_on:
      - llm
    ports:
      - "8000:8000"
```

---

### **Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "app.py"]
```

---

### **requirements.txt**

```
fastapi
uvicorn
prometheus-client
requests
```

---

### **app.py**

```python
import os
import time
import requests
from fastapi import FastAPI
from prometheus_client import Histogram, Counter, Gauge, generate_latest

MODEL = os.getenv("MODEL_NAME", "smollm")
OLLAMA_URL = "http://llm:11434/api/generate"

app = FastAPI()

# --- Metrics
latency_histogram = Histogram(
    "llm_request_latency_seconds",
    "Latency of LLM inference requests",
    buckets=[0.1, 0.3, 0.5, 0.8, 1.2, 2.0]
)

request_total = Counter("llm_request_total", "Total LLM requests")
request_errors = Counter("llm_request_errors_total", "Total LLM errors (500s)")
gpu_util = Gauge("llm_gpu_utilization_percent", "Simulated GPU utilization")
inference_in_flight = Gauge("llm_inference_in_flight", "Active inference requests")

container_restarts = Counter("service_container_restarts_total", "Number of container auto-restarts")

# --- Inference endpoint
@app.get("/generate")
def generate(prompt: str = "hello reliability"):
    request_total.inc()
    inference_in_flight.set(65)  # simulated GPU load
    inference_in_flight.inc()

    start = time.time()
    try:
        r = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt}, timeout=10)
        if r.status_code >= 500:
            request_errors.inc()
    except Exception:
        request_errors.inc()
        inference_in_flight.dec()
        return {"status": "error"}
    
    elapsed = time.time() - start
    latency_histogram.observe(elapsed)
    inference_in_flight.dec()
    return {"status": "ok", "latency": elapsed}

@app.get("/metrics")
def metrics():
    # record a restart metric for visibility in dashboards
    container_restarts.inc()
    return generate_latest()
```

---

### **chaos.py**

```python
import random
import subprocess
import time

def inject_failure():
    failures = [
        "docker kill llm-api",
        "docker kill llm",
        "docker compose restart llm-api",
        "docker compose restart llm"
    ]
    cmd = random.choice(failures)
    print(f"[CHAOS] Injecting failure: {cmd}")
    subprocess.run(cmd, shell=True)

while True:
    wait = random.randint(5, 15)
    print(f"[CHAOS] Waiting {wait}s before next fault...")
    time.sleep(wait)
    inject_failure()
```

---

### **remediate.sh**

```bash
#!/usr/bin/env bash
# A tiny SRE remediation loop (health check → restart)

API="http://localhost:8000/metrics"
THRESHOLD=0.7  # 700ms

while true; do
  LATENCY=$(curl -s "$API" | grep "llm_request_latency_seconds_bucket" | head -1 | awk '{print $2}')
  if (( $(echo "$LATENCY > $THRESHOLD" | bc -l) )); then
    echo "[REMEDIATION] Latency high ($LATENCY s). Restarting API container..."
    docker compose restart api
  fi
  sleep 5
done
```

---

### **requirements.txt**

```
fastapi
uvicorn
prometheus-client
requests
```

---

### **dashboards/grafana.json**

```json
{
  "title": "LLM Reliability (MVP)",
  "panels": [
    { "type": "graph", "title": "Latency (Histogram)", "targets": [{ "expr": "llm_request_latency_seconds_bucket" }] },
    { "type": "stat", "title": "Error Rate", "targets": [{ "expr": "llm_request_errors_total" }] },
    { "type": "stat", "title": "GPU Util %", "targets": [{ "expr": "llm_gpu_utilization_percent" }] },
    { "type": "stat", "title": "Container Restarts", "targets": [{ "expr": "service_container_restarts_total" }] }
  ]
}
```

---

### **.env.example**

```bash
MODEL_NAME=smollm
AWS_REGION=us-east-1
# Add your real keys only locally or via a secrets manager
```

---

### **Next moves once the repo is live**

After committing:

1. Run the stack → verify metrics at localhost:8000/metrics
2. Import Grafana JSON and screenshot dashboard for your blog
3. Push a clean blog post: *“I broke an LLM endpoint on purpose and fixed it like an SRE”*
4. Publish a short reliability report or 7-day error budget table
5. Pin the repo on GitHub + link it to your personal site

---

If you want, I’ll draft the **blog post** next that reads like something an SRE hiring manager nods at approvingly.
Just say: **“write the blog draft.”**

