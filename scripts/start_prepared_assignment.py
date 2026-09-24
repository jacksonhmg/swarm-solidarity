#!/usr/bin/env python3
"""Start the one newly allocated prepared assignment; no model-work retries."""
import json
import os
from pathlib import Path
from revised_recovery_support import LOG, PARALLEL, node_dir, now, sha, write_json, verify_plan
from launch_revised_recovery import TRANSFER, prepare_node, dispatch
from continue_revised_startup import upload_patch


def main():
    verify_plan()
    out = node_dir('prepared')
    out.mkdir(parents=True, exist_ok=True)
    assert not (LOG/'execution/prepared').exists()
    assert not (out/'dispatch-intent.json').exists()
    with (PARALLEL/'prepared-startup-started.json').open('x') as handle:
        json.dump({'at': now(), 'pid': os.getpid(), 'no_previous_prepared_model_work': True}, handle)
    original = json.loads((PARALLEL/'bundle.json').read_text())
    archives = {name: TRANSFER/('source.tar.gz' if name == 'source' else name+'.tar.gz')
                for name in original['archives']}
    assert all(sha(archives[name]) == item['sha256'] for name, item in original['archives'].items())
    patch = TRANSFER/'operational-continuation.tar.gz'
    assert sha(patch) == json.loads((PARALLEL/'continuation-bundle.json').read_text())['sha256']
    try:
        prepare_node('prepared', archives)
        upload_patch('prepared', patch)
        verify_plan()
        dispatch('prepared')
        write_json(PARALLEL/'prepared-startup-result.json', {'at': now(), 'status': 'dispatched'})
    except BaseException as exc:
        write_json(PARALLEL/'prepared-startup-result.json', {'at': now(),
            'status': 'startup_error', 'error': type(exc).__name__+': '+str(exc),
            'decision': 'Reconcile without repeating model work; other independent jobs continue.'})
        raise


if __name__ == '__main__':
    main()
