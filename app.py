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

