#!/usr/bin/env bash
# A tiny SRE remediation loop (health check → restart)

API="http://localhost:8000/metrics"
THRESHOLD="${LATENCY_THRESHOLD_SECONDS:-30}"
COOLDOWN_SECONDS="${REMEDIATION_COOLDOWN_SECONDS:-120}"
USE_DOCKER_OLLAMA="${USE_DOCKER_OLLAMA:-false}"
LAST_RESTART=0

while true; do
  # Calculate average latency from sum and count
  METRICS=$(curl -s "$API")
  LATENCY_SUM=$(printf "%s\n" "$METRICS" | grep "llm_request_latency_seconds_sum" | awk '{print $2}')
  LATENCY_COUNT=$(printf "%s\n" "$METRICS" | grep "llm_request_latency_seconds_count" | awk '{print $2}')
  
  # Avoid division by zero
  if [[ -n "$LATENCY_COUNT" && "$LATENCY_COUNT" != "0.0" && "$LATENCY_COUNT" != "0" ]]; then
      AVG_LATENCY=$(echo "$LATENCY_SUM / $LATENCY_COUNT" | bc -l)
      
      if (( $(echo "$AVG_LATENCY > $THRESHOLD" | bc -l) )); then
        NOW=$(date +%s)
        if (( NOW - LAST_RESTART < COOLDOWN_SECONDS )); then
          echo "[REMEDIATION] Latency high ($AVG_LATENCY s), still in cooldown."
        elif [[ "$USE_DOCKER_OLLAMA" == "true" ]]; then
          echo "[REMEDIATION] Latency high ($AVG_LATENCY s). Restarting Docker Ollama container..."
          docker compose --profile docker-ollama restart llm
          LAST_RESTART=$NOW
        else
          echo "[REMEDIATION] Latency high ($AVG_LATENCY s). Native Ollama is outside Compose; restart it manually if needed."
          LAST_RESTART=$NOW
        fi
      fi
  fi
  sleep 5
done
