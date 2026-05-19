import argparse
import random
import subprocess
import time

FAILURES = [
    ["docker", "kill", "llm-api"],
    ["docker", "kill", "llm"],
    ["docker", "compose", "restart", "llm-api"],
    ["docker", "compose", "restart", "llm"],
]


def inject_failure(rng):
    cmd = rng.choice(FAILURES)
    print(f"[CHAOS] Injecting failure: {' '.join(cmd)}")
    subprocess.run(cmd, shell=False)


def parse_args():
    parser = argparse.ArgumentParser(description="Inject random container failures.")
    parser.add_argument("--seed", type=int, default=None, help="Seed for reproducible runs.")
    parser.add_argument("--iterations", type=int, default=0, help="Stop after N failures (0 = forever).")
    parser.add_argument("--min-wait", type=int, default=5, help="Minimum seconds between failures.")
    parser.add_argument("--max-wait", type=int, default=15, help="Maximum seconds between failures.")
    return parser.parse_args()


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    count = 0
    try:
        while args.iterations == 0 or count < args.iterations:
            wait = rng.randint(args.min_wait, args.max_wait)
            print(f"[CHAOS] Waiting {wait}s before next fault...")
            time.sleep(wait)
            inject_failure(rng)
            count += 1
    except KeyboardInterrupt:
        print("[CHAOS] Stopped.")


if __name__ == "__main__":
    main()
