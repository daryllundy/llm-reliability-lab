#!/usr/bin/env bash
# A tiny SRE remediation loop (health check → restart)

API="http://localhost:8000/metrics"
THRESHOLD=0.7  # 700ms

while true; do
  # Calculate average latency from sum and count
  LATENCY_SUM=$(curl -s "$API" | grep "llm_request_latency_seconds_sum" | awk '{print $2}')
  LATENCY_COUNT=$(curl -s "$API" | grep "llm_request_latency_seconds_count" | awk '{print $2}')
  
  # Avoid division by zero
  if [[ -n "$LATENCY_COUNT" && "$LATENCY_COUNT" != "0.0" && "$LATENCY_COUNT" != "0" ]]; then
      AVG_LATENCY=$(echo "$LATENCY_SUM / $LATENCY_COUNT" | bc -l)
      
      if (( $(echo "$AVG_LATENCY > $THRESHOLD" | bc -l) )); then
        echo "[REMEDIATION] Latency high ($AVG_LATENCY s). Restarting API container..."
        docker compose restart api
      fi
  fi
  sleep 5
done

