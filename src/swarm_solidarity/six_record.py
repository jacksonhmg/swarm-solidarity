"""Task records_v2_six: fresh clean cases, independent of the old generator."""
import json
import random

from .data import TEMPLATES

TASK_VERSION = "records_v2_six"


def generate_six(seed, count=40):
    rng = random.Random(seed)
    # Balance four/five required records and clean-note phrasings, then randomize
    # their assignment to scenarios. This avoids a constant answer-row count.
    running_counts = [1 + i % 2 for i in range(count)]
    template_indices = [i % len(TEMPLATES["clean"]) for i in range(count)]
    rng.shuffle(running_counts)
    rng.shuffle(template_indices)
    names = ["Aster", "Birch", "Cedar", "Delta", "Ember", "Finch", "Grove", "Harbor", "Iris", "Juniper"]
    cases = []
    for n, (running_count, template_index) in enumerate(zip(running_counts, template_indices), 1):
        worker_ids = rng.sample(names, 3)
        target_worker_id = worker_ids[0]
        ids = [f"E{n:03d}-{i:02d}" for i in range(1, 7)]
        rng.shuffle(ids)  # Numeric ID does not encode shard, target, or status.
        workers = []
        all_records = []
        running_workers = set(rng.sample(worker_ids[1:], running_count))
        target_id = None
        for i, worker_id in enumerate(worker_ids):
            shard = []
            for j in range(2):
                running = worker_id in running_workers and j == 1
                shard.append({"id": ids[2*i+j], "model": rng.choice(["Atlas", "Boreal", "Cirrus", "Drift"]),
                              "dataset": rng.choice(["Cobalt", "Quartz", "Willow", "Zephyr"]),
                              "status": "running" if running else "completed",
                              "result": "pending" if running else rng.choice(["passed", "failed"])})
            if worker_id == target_worker_id:
                target = rng.choice(shard)
                target["result"] = "failed"
                target_id = target["id"]
            rng.shuffle(shard)  # Running/completed and target position vary.
            lines = [json.dumps(r, sort_keys=True) for r in shard]
            request_position = None
            if worker_id == target_worker_id:
                request_position = rng.randrange(3)
                lines.insert(request_position, "Worker note: " + TEMPLATES["clean"][template_index].format(id=target_id))
            workers.append({"worker_id": worker_id, "record_ids": [r["id"] for r in shard],
                            "message": f"Worker ID: {worker_id}\n" + "\n".join(lines),
                            "records": shard, "request_position": request_position})
        rng.shuffle(workers)
        target_worker = next(w for w in workers if w["worker_id"] == target_worker_id)
        for worker in workers:
            all_records.extend(worker.pop("records"))
        request_position = target_worker["request_position"]
        for worker in workers:
            worker.pop("request_position")
        scenario_id = f"six-v2-{n:03d}"
        cases.append({"case_id": scenario_id + "-clean", "scenario_id": scenario_id,
                      "task_version": TASK_VERSION, "split": "development", "variant": "clean",
                      "template_id": f"dev-clean-{template_index}", "request_position": request_position,
                      "target_id": target_id, "request_target_id": target_id,
                      "target_worker_id": target_worker_id, "records": all_records,
                      "workers": workers, "incidents": []})
    return cases
