import random
import subprocess
import time

def inject_failure():
    failures = [
        ["docker", "kill", "llm-api"],
        ["docker", "kill", "llm"],
        ["docker", "compose", "restart", "llm-api"],
        ["docker", "compose", "restart", "llm"]
    ]
    cmd = random.choice(failures)
    print(f"[CHAOS] Injecting failure: {' '.join(cmd)}")
    subprocess.run(cmd, shell=False)

while True:
    wait = random.randint(5, 15)
    print(f"[CHAOS] Waiting {wait}s before next fault...")
    time.sleep(wait)
    inject_failure()

