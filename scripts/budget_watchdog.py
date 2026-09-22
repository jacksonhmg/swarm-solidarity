#!/usr/bin/env python3
"""Local cost backstop for the single owned instance; credentials never go remote."""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", default=".local/lambda-pilot/state.json")
    p.add_argument("--max-hours", type=float, default=3)
    args = p.parse_args()
    while True:
        state = json.loads(Path(args.state).read_text())
        if state.get("status") == "terminated":
            print("Owned instance is terminated; watchdog exiting", flush=True)
            return
        started = dt.datetime.fromisoformat(state["launch_requested_at"])
        age = (dt.datetime.now(dt.timezone.utc) - started).total_seconds()
        if age >= args.max_hours * 3600:
            print("Runtime budget reached; requesting owned-instance termination", flush=True)
            result = subprocess.run([sys.executable, "scripts/lambda_cloud.py", "terminate", "--state", args.state])
            if result.returncode == 0:
                return
        time.sleep(60)


if __name__ == "__main__":
    main()
