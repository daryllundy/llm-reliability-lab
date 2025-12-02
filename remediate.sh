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

