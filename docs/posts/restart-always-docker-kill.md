# Three surprises about Docker's `restart: always`

*Measured on Docker Desktop 29.4 / macOS, May 2026.*

I built a small SRE lab to demonstrate auto-recovery — FastAPI wrapping a local Ollama endpoint, Prometheus scraping `/metrics`, `restart: always` on every container, and a chaos script that randomly kills things. The whole point was "chaos hits, the policy heals it, the SLO holds."

Then I measured the recoveries. `restart: always` turned out to be much more conditional than I expected.

## Surprise 1: `docker kill` doesn't trigger the policy

The first chaos action was the obvious one:

```bash
docker kill llm-api
```

Container exits with code 137 (SIGKILL). `/health` never returns 200. After 30 seconds: still down. `docker inspect`:

```
"ExitCode": 137,
"Running": false,
"Restarting": false
```

`Restarting: false` is the tell. Docker classifies CLI-initiated kills as operator intent — same category as `docker stop` — and the restart policy doesn't fire. Documented behavior, but easy to miss.

## Surprise 2: `docker kill --signal=SIGSEGV` didn't kill the process

The "obvious" fix is to send a signal that doesn't look like operator intent:

```bash
docker kill --signal=SIGSEGV llm-api
```

Result: the container kept running. `ExitCode` stayed 0, `RestartCount` unchanged. The uvicorn process either caught or ignored SIGSEGV — Python's behavior when SIGSEGV arrives via `kill()` instead of an actual memory fault is different from what I assumed. The signal was delivered; the process shrugged.

So "just send a different signal" isn't a real fix. You need an exit that actually happens.

## Surprise 3: the "manually stopped" flag is sticky

After `docker kill`, I ran `docker start llm-api` to bring the container back, then tried a different chaos action — sending SIGTERM to PID 1 from *inside* the container:

```bash
docker exec llm-api python -c "import os, signal; os.kill(1, signal.SIGTERM)"
```

The container exited cleanly. `RestartCount: 0`. After 30 seconds: still down. The restart policy didn't fire even though Docker didn't initiate this exit.

Then I did `docker compose down && docker compose up -d`, repeated the same SIGTERM-from-inside, and *that* worked: `RestartCount: 0 → 1`, `/health` recovered in 12 seconds.

So the "manually stopped" flag set by the original `docker kill` survives `docker start`. Manually starting a container brings it up but does **not** re-arm the restart policy. The only way I found to clear the flag was recreating the container.

## What actually exercises the policy

You need an exit that Docker didn't initiate. Signaling PID 1 from inside the container works because Docker only sees PID 1 die — there's no `kill` or `stop` command in its history. Linux kernel rules block SIGKILL/SIGSTOP to PID 1 from inside its own PID namespace, so SIGTERM (which uvicorn handles by shutting down gracefully) is the cleanest option:

```bash
docker exec llm-api python -c "import os, signal; os.kill(1, signal.SIGTERM)"
```

Measured on a fresh container: graceful exit, policy fires, recovery in ~12 seconds (uvicorn boot).

More realistic: trigger an unhandled exception in the application itself, OOM-kill the container, or simulate a host-level failure. Those are the production failures `restart: always` is actually for.

Drop-in replacement for the broken `docker kill` chaos action:

```python
# chaos.py
FAILURES = [
    # Triggers restart: always — exit originates inside the container.
    ["docker", "exec", "llm-api", "python", "-c",
     "import os, signal; os.kill(1, signal.SIGTERM)"],
    # Does NOT trigger restart: always — Docker treats as operator intent.
    # Useful for testing what your system does when recovery doesn't happen.
    ["docker", "kill", "llm-api"],
    # Graceful restart — always recovers, but doesn't exercise the policy.
    ["docker", "compose", "restart", "llm-api"],
]
```

Mixing the three is what gives you a chaos suite that tests both the happy path and the gap.

## The lesson

`restart: always` is really "always, unless I have any reason to think you wanted this." That's the right behavior in production — host reboots, OOMs, kernel panics all fire it — but it's actively misleading in chaos tests. If your chaos uses `docker kill`, you're not testing the policy. You're testing what Docker does when an operator stops a container, which is nothing.

The more general version: "we have automated recovery" is only as true as the failure mode you tested against. If the chaos doesn't mimic real production failures, the remediation is theater.

---

Source: [github.com/daryllundy/llm-reliability-lab](https://github.com/daryllundy/llm-reliability-lab) — full experiment write-up in `docs/EXPERIMENT.md`.
