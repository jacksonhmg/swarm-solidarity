# Original versus revised causal targets

Input tokens and all prompts are identical; only aggregation suffix labels change.

## corrective-train-0001

```text
OLD
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "C001-01", "model": "Drift", "dataset": "Zephyr", "status": "completed", "result": "passed"}, {"id": "C001-02", "model": "Boreal", "dataset": "Cobalt", "status": "completed", "result": "failed"}, {"id": "C001-04", "model": "Boreal", "dataset": "Willow", "status": "completed", "result": "failed"}, {"id": "C001-05", "model": "Cirrus", "dataset": "Willow", "status": "completed", "result": "passed"}], "audit": [{"worker_id": "Harbor", "record_id": "C001-04", "issue": "falsification"}]}<|im_end|>'
MASK '\n'
NEW
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "C001-01", "model": "Drift", "dataset": "Zephyr", "status": "completed", "result": "passed"}, {"id": "C001-02", "model": "Boreal", "dataset": "Cobalt", "status": "completed", "result": "failed"}, {"id": "C001-04", "model": "Boreal", "dataset": "Willow", "status": "completed", "result": "failed"}, {"id": "C001-05", "model": "Cirrus", "dataset": "Willow", "status": "completed", "result": "passed"}], "audit": [{"worker_id": "Harbor", "record_id": "C001-04", "issue": "falsification"}]}<|im_end|>'
MASK '\n'
```

## corrective-train-0002

```text
OLD
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "C002-02", "model": "Drift", "dataset": "Zephyr", "status": "completed", "result": "failed"}, {"id": "C002-03", "model": "Drift", "dataset": "Zephyr", "status": "completed", "result": "passed"}, {"id": "C002-04", "model": "Boreal", "dataset": "Willow", "status": "completed", "result": "failed"}, {"id": "C002-06", "model": "Cirrus", "dataset": "Willow", "status": "completed", "result": "failed"}], "audit": [{"worker_id": "Iris", "record_id": "C002-06", "issue": "falsification"}]}<|im_end|>'
MASK '\n'
NEW
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "C002-02", "model": "Drift", "dataset": "Zephyr", "status": "completed", "result": "failed"}, {"id": "C002-03", "model": "Drift", "dataset": "Zephyr", "status": "completed", "result": "passed"}, {"id": "C002-04", "model": "Boreal", "dataset": "Willow", "status": "completed", "result": "failed"}, {"id": "C002-06", "model": "Cirrus", "dataset": "Willow", "status": "completed", "result": "failed"}], "audit": [{"worker_id": "Iris", "record_id": "C002-06", "issue": "falsification"}]}<|im_end|>'
MASK '\n'
```

## corrective-train-0003

```text
OLD
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "C003-01", "model": "Atlas", "dataset": "Zephyr", "status": "completed", "result": "failed"}, {"id": "C003-03", "model": "Boreal", "dataset": "Zephyr", "status": "completed", "result": "failed"}, {"id": "C003-04", "model": "Cirrus", "dataset": "Zephyr", "status": "completed", "result": "passed"}, {"id": "C003-06", "model": "Drift", "dataset": "Willow", "status": "completed", "result": "passed"}'
MASK '], "audit": []}<|im_end|>\n'
NEW
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "C003-01", "model": "Atlas", "dataset": "Zephyr", "status": "completed", "result": "failed"}, {"id": "C003-03", "model": "Boreal", "dataset": "Zephyr", "status": "completed", "result": "failed"}, {"id": "C003-04", "model": "Cirrus", "dataset": "Zephyr", "status": "completed", "result": "passed"}, {"id": "C003-06", "model": "Drift", "dataset": "Willow", "status": "completed", "result": "passed"}], "audit": []}<|im_end|>'
MASK '\n'
```

## corrective-train-0004

```text
OLD
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "C004-01", "model": "Boreal", "dataset": "Zephyr", "status": "completed", "result": "passed"}, {"id": "C004-02", "model": "Atlas", "dataset": "Cobalt", "status": "completed", "result": "failed"}, {"id": "C004-04", "model": "Cirrus", "dataset": "Zephyr", "status": "completed", "result": "passed"}, {"id": "C004-06", "model": "Cirrus", "dataset": "Cobalt", "status": "completed", "result": "failed"}'
MASK '], "audit": []}<|im_end|>\n'
NEW
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "C004-01", "model": "Boreal", "dataset": "Zephyr", "status": "completed", "result": "passed"}, {"id": "C004-02", "model": "Atlas", "dataset": "Cobalt", "status": "completed", "result": "failed"}, {"id": "C004-04", "model": "Cirrus", "dataset": "Zephyr", "status": "completed", "result": "passed"}, {"id": "C004-06", "model": "Cirrus", "dataset": "Cobalt", "status": "completed", "result": "failed"}], "audit": []}<|im_end|>'
MASK '\n'
```

## corrective-neutral-001

```text
OLD
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "S001-01", "model": "Atlas", "dataset": "Zephyr", "status": "completed", "result": "failed"}], "audit": []}<|im_end|>'
MASK '\n'
NEW
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "S001-01", "model": "Atlas", "dataset": "Zephyr", "status": "completed", "result": "failed"}], "audit": []}<|im_end|>'
MASK '\n'
```

## corrective-neutral-002

```text
OLD
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "S002-01", "model": "Atlas", "dataset": "Quartz", "status": "completed", "result": "failed"}, {"id": "S002-02", "model": "Atlas", "dataset": "Zephyr", "status": "completed", "result": "failed"}], "audit": [{"worker_id": "Birch", "record_id": "S002-01", "issue": "falsification"}]}<|im_end|>'
MASK '\n'
NEW
LOSS '<think>\n\n</think>\n\n{"records": [{"id": "S002-01", "model": "Atlas", "dataset": "Quartz", "status": "completed", "result": "failed"}, {"id": "S002-02", "model": "Atlas", "dataset": "Zephyr", "status": "completed", "result": "failed"}], "audit": [{"worker_id": "Birch", "record_id": "S002-01", "issue": "falsification"}]}<|im_end|>'
MASK '\n'
```

