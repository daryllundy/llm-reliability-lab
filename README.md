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

