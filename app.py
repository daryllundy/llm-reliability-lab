import os
import time
import requests
import logging
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from prometheus_client import Histogram, Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)

@app.get("/health")
def health():
    return {"status": "healthy"}

# --- Inference endpoint
@app.post("/generate")
def generate(request: GenerateRequest):
    import random
    request_total.inc()
    inference_in_flight.inc()
    # Simulate GPU utilization during inference (60-85%)
    gpu_util.set(random.uniform(60, 85))

    start = time.time()
    try:
        r = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": request.prompt}, timeout=10)
        r.raise_for_status()
    except requests.Timeout:
        logger.error("Ollama request timeout")
        request_errors.inc()
        inference_in_flight.dec()
        raise HTTPException(status_code=504, detail="Request timeout")
    except requests.RequestException as e:
        logger.error(f"Ollama request failed: {e}")
        request_errors.inc()
        inference_in_flight.dec()
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        request_errors.inc()
        inference_in_flight.dec()
        raise HTTPException(status_code=500, detail="Internal server error")
    
    elapsed = time.time() - start
    latency_histogram.observe(elapsed)
    inference_in_flight.dec()
    gpu_util.set(0)  # Reset GPU utilization after inference
    return {"status": "ok", "latency": elapsed}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

