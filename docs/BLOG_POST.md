# **LLM Reliability Lab: Breaking an inference service on purpose, fixing it like an SRE**

Engineers don’t get hired for saying “I use AI effectively.”
They get hired for showing they can ship fast **without** creating a live grenade in production.

So I built a lab environment where I treated a 120B-class model endpoint like a real service, instrumented it with SLIs, injected failures, defined error budgets, and wired automated remediation — all accelerated by AI-assisted coding.

---

## **The stack I tested against**

I didn’t need Kubernetes for the MVP, but I needed realism, so I containerized the whole thing using:

* **Docker Compose**: Orchestrating the entire stack.
* **Ollama**: Providing a local LLM runtime (running `smollm` for speed).
* **Prometheus**: A production-grade monitoring system scraping metrics.
* **Grafana**: Visual dashboards for real-time observability.

For context, this is the same ecosystem logic you see at GPU inference hosts like RunPod, but the lab runs cheap and local so I can actually break things 50 times without melting a credit card.

---

## **SRE rules I enforced**

These weren’t vibes. They were the job description in practice:

| SRE concept               | How I applied it                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------ |
| **SLI for latency**       | Prometheus histogram capturing p95/p99 request time                                  |
| **Availability tracking** | Total requests vs. 500-class errors                                                  |
| **Error budgets (SLO)**   | 0.5% monthly error budget (30-day reliability target)                                |
| **Failure injection**     | Random container kills, GPU saturation simulation, forced restarts                   |
| **Self-healing**          | Automated remediation script triggered by latency and error thresholds               |
| **Infrastructure as Code**| Automated Grafana provisioning (datasources & dashboards) via config files           |
| **Testing**               | Infrastructure tests ensuring the monitoring stack is correctly wired up               |

I used AI agents to generate, iterate, and speed up the implementation — but every line of code that touched reliability logic, thresholds, and metrics was validated like a human would own the pager for it.

---

## **Breaking the system**

Then came the fun part.

I wrote a chaos script that randomly:

* killed the API container
* killed the model container
* forced restarts
* simulated request saturation
* faked GPU exhaustion

Think of it as chaos testing inspired by tools like Chaos Monkey, but scoped down, deterministic, and measurable.

The point wasn’t to make it explode.
The point was to make it explode *predictably*, and recover *automatically* within the error budget.

Every failure was logged and emitted as a counter metric: `service_container_restarts_total`

---

## **Monitoring outcomes**

Dashboarded in Grafana, I tracked:

* latency histograms
* error spikes
* container restarts
* simulated GPU utilization
* in-flight inference saturation

**Automated Provisioning**: I configured Grafana to automatically provision the Prometheus datasource and the dashboard upon startup. This means no manual clicking to set up the monitoring view — it's ready the moment `docker-compose up` finishes.

The dashboards live as JSON exports inside the repository, and the provisioning config ensures they are loaded automatically.

---

## **What this project signals to employers**

Especially for Site Reliability roles, this repo gives proof I can:

✅ Define SLOs and track SLIs as metrics
✅ Build monitoring that catches issues early
✅ Use automation to remediate failures without human panic loops
✅ Treat model inference like a real production dependency
✅ Ship fast using AI without skipping reliability fundamentals
✅ Implement Infrastructure as Code principles for monitoring stacks

If this were evaluated like a candidate scorecard for SRE teams:

* **Ops maturity:** high
* **Autonomy:** high
* **Delivery velocity:** high
* **Risk awareness:** sane (rare)
* **Pager blast radius:** controlled

That’s the combo.

---

## **Where to next**

This lab is now a baseline I extend into:

* model serving reliability patterns
* autoscaling simulation
* cross-provider metrics normalization
* integration test harnesses for agent deployments

But more importantly, it gave me the artifact I wanted:
A project that makes it obvious I know reliability **and** can ship through AI without becoming a hazard.

---

## **Project links**

* **Lab Repository**: (link it here when published publicly)
* **Grafana Dashboard**: `/dashboards/grafana.json`
* **Chaos test runner**: `chaos.py`
* **Remediation loop**: `remediate.sh`
* **Security template**: `SECURITY.md`
* **Infrastructure Tests**: `tests/test_infra.py`

---

Now go commit this into GitHub, pin it, deploy it, break it, and capture the evidence.
The code is done — the proof is up to you.
