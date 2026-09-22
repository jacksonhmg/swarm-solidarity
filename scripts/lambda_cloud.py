#!/usr/bin/env python3
"""Small owner-scoped Lambda client. Credentials stay on the controlling Mac.

Set LAMBDA_API_KEY_FILE to an existing file, or LAMBDA_API_KEY in the environment.
Only the exact instance recorded in --state can be terminated. Launch POSTs are
never retried automatically: a timed-out launch must be reconciled by name.
"""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request
import uuid

BASE = "https://cloud.lambda.ai/api/v1/"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def api(endpoint, payload=None):
    key = os.environ.get("LAMBDA_API_KEY")
    if not key:
        key = Path(os.environ["LAMBDA_API_KEY_FILE"]).expanduser().read_text().strip()
    headers = {"Authorization": "Bearer " + key, "Accept": "application/json", "User-Agent": "swarm-solidarity/0.1"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    request = urllib.request.Request(BASE + endpoint, data=data, headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=45) as response:
            return json.load(response)["data"]
    except urllib.error.HTTPError as error:
        try:
            detail = json.loads(error.read()).get("error", {})
            code = detail.get("code", "unknown")
        except ValueError:
            code = "non-json-response"
        raise RuntimeError(f"Lambda {endpoint}: HTTP {error.code} ({code}); request not retried") from None


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.chmod(0o600)
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["capacity", "launch", "status", "terminate", "delete-key"])
    parser.add_argument("--state", default=".local/lambda-pilot/state.json")
    parser.add_argument("--instance-type", default="gpu_1x_a100_sxm4")
    parser.add_argument("--region", default="us-west-2")
    parser.add_argument("--max-hourly-usd", type=float, default=3.29)
    args = parser.parse_args()
    state_path = Path(args.state)
    if args.action == "capacity":
        for name, entry in api("instance-types").items():
            if entry["regions_with_capacity_available"]:
                print(json.dumps({"type": name, "usd_per_hour": entry["instance_type"]["price_cents_per_hour"] / 100,
                                  "regions": entry["regions_with_capacity_available"]}))
        return
    if args.action == "launch":
        if state_path.exists():
            raise SystemExit("State already exists. Inspect/reconcile it before creating another instance.")
        entry = api("instance-types")[args.instance_type]
        price = entry["instance_type"]["price_cents_per_hour"] / 100
        if price > args.max_hourly_usd:
            raise SystemExit(f"Rate ${price}/hour exceeds limit")
        if args.region not in [r["name"] for r in entry["regions_with_capacity_available"]]:
            raise SystemExit("Requested region currently has no capacity")
        state_path.parent.mkdir(parents=True, exist_ok=True)
        private_key = state_path.parent / "id_ed25519"
        if not private_key.exists():
            subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "swarm-solidarity-pilot", "-f", str(private_key)], check=True)
        name = "swarm-solidarity-pilot-" + uuid.uuid4().hex[:8]
        state = {"name": name, "ssh_key_name": name, "private_key_path": str(private_key.resolve()),
                 "instance_type": args.instance_type, "region": args.region, "usd_per_hour": price,
                 "created_at": now(), "status": "registering_key"}
        save(state_path, state)
        time.sleep(1.1)
        key = api("ssh-keys", {"name": name, "public_key": private_key.with_suffix(".pub").read_text().strip()})
        state["ssh_key_id"] = key["id"]
        state["status"] = "launch_requested"
        state["launch_requested_at"] = now()
        save(state_path, state)
        time.sleep(1.1)
        result = api("instance-operations/launch", {"region_name": args.region, "instance_type_name": args.instance_type,
                     "ssh_key_names": [name], "file_system_names": [], "name": name})
        state["instance_id"] = result["instance_ids"][0]
        state["status"] = "booting"
        save(state_path, state)
        print(json.dumps({k: state[k] for k in ["name", "instance_id", "instance_type", "region", "usd_per_hour", "status"]}))
        return
    state = json.loads(state_path.read_text())
    if args.action == "delete-key":
        if state.get("status") != "terminated":
            raise SystemExit("Confirm instance termination before deleting its key")
        # Explicit DELETE; do not remove unrelated SSH keys.
        key = os.environ.get("LAMBDA_API_KEY") or Path(os.environ["LAMBDA_API_KEY_FILE"]).expanduser().read_text().strip()
        request = urllib.request.Request(BASE + "ssh-keys/" + state["ssh_key_id"], method="DELETE",
            headers={"Authorization": "Bearer " + key, "User-Agent": "swarm-solidarity/0.1"})
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=30) as response:
            print("SSH key deleted:", response.status)
        state["ssh_key_deleted_at"] = now()
        save(state_path, state)
        return
    if not state.get("instance_id"):
        # Reconcile an uncertain launch without issuing a second launch.
        matches = [x for x in api("instances") if x.get("name") == state["name"]]
        if len(matches) != 1:
            raise SystemExit(f"Uncertain launch: found {len(matches)} matching instances; inspect before proceeding")
        state["instance_id"] = matches[0]["id"]
        time.sleep(1.1)
    instance = api("instances/" + state["instance_id"])
    if instance.get("name") != state["name"] or state["ssh_key_name"] not in instance.get("ssh_key_names", []):
        raise SystemExit("Ownership verification failed")
    state["status"] = instance["status"]
    state["last_checked_at"] = now()
    if instance.get("ip"):
        state["ip"] = instance["ip"]
    if args.action == "terminate" and state["status"] not in ("terminated", "terminating"):
        time.sleep(1.1)
        api("instance-operations/terminate", {"instance_ids": [state["instance_id"]]})
        state["status"] = "terminating"
        state["termination_requested_at"] = now()
    save(state_path, state)
    print(json.dumps({k: state.get(k) for k in ["name", "instance_id", "status", "ip", "usd_per_hour"]}))


if __name__ == "__main__":
    main()
