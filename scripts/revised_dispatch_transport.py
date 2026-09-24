"""Dispatch the frozen controller once; losing its acknowledgement is uncertain.

The caller must start collection before dispatch. This module deliberately has
no cloud termination API and never repeats a command after an uncertain result.
The atomic remote receipt in dispatch_detached_once.py prevents duplicate work
if the same operation is later reconciled.
"""
import json
import shlex
import subprocess
from pathlib import Path


def dispatch_once(ssh_args, host, remote_root, receipt_root, start_supervisor,
                  run=subprocess.run, controller_command=None):
    root = Path(receipt_root)
    root.mkdir(parents=True, exist_ok=True)
    # Exclusive intent also prevents this local operation being delivered twice.
    intent = root / 'dispatch-intent.json'
    with intent.open('x') as handle:
        json.dump({'phase': 'before_supervisor', 'remote_root': remote_root}, handle)
    supervisor_pid = start_supervisor()
    assert isinstance(supervisor_pid, int) and supervisor_pid > 0
    controller_command = controller_command or ['python3', 'scripts/run_revised_host.py']
    command = ['python3', 'scripts/dispatch_detached_once.py',
               '--receipt', str(root / 'controller-dispatch.json'),
               '--output', str(root / 'remote-console.log'),
               '--', *controller_command]
    remote_command = 'cd ' + shlex.quote(remote_root) + ' && ' + shlex.join(command)
    result = {'supervisor_pid': supervisor_pid, 'command': remote_command,
              'acknowledgement': 'unknown', 'repeat_dispatch': False}
    # Save an intent before sending: even interruption during run remains unknown.
    with intent.open('w') as handle:
        json.dump({**result, 'phase': 'sending'}, handle, indent=2)
    try:
        done = run(ssh_args + [host, remote_command], check=True,
                   capture_output=True, text=True, timeout=45)
        receipt = json.loads(done.stdout)
        assert receipt['status'] == 'started', receipt
        assert receipt['command'] == controller_command
        result.update(acknowledgement='received', remote_receipt=receipt)
    except (OSError, ValueError, AssertionError, subprocess.SubprocessError) as exc:
        result['transport_error'] = type(exc).__name__ + ': ' + str(exc)
        result['decision'] = 'Keep collecting; inspect remote claim/controller receipts. Do not infer model failure or repeat dispatch.'
    (root / 'dispatch-acknowledgement.json').write_text(json.dumps(result, indent=2)+'\n')
    return result
