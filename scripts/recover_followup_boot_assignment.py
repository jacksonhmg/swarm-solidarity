"""Replace one confirmed never-started boot failure; preserve every sampled request."""
import argparse
import shutil
import recover_followup_shard_setup as recovery
import followup_shard_cloud as base
from followup_shard_cloud import *

REC = ROOT / 'boot_recovery'
JOB = 'revised_s41032_agent_a-02'
SCRIPT = 'scripts/recover_followup_boot_assignment.py'


def execution_plan():
    return json.loads((REC / 'execution_state_plan.json').read_text())


def install():
    recovery.verify()
    for p, h in json.loads((REC / 'freeze.json').read_text())['files'].items():
        assert sha(p) == h, p
    base.plan = execution_plan
    recovery.plan = execution_plan
    recovery.REC = REC
    original_background = base.background

    def background_redirect(script, args, log):
        if script == 'scripts/recover_followup_shard_setup.py':
            script = SCRIPT
        return original_background(script, args, log)

    recovery.background = background_redirect


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--supervisor', action='store_true')
    p.add_argument('--watchdog', action='store_true')
    p.add_argument('--finish', action='store_true')
    p.add_argument('--job', default=JOB)
    a = p.parse_args()
    install()
    if a.supervisor:
        import followup_shard_supervisor as supervisor
        sys.argv = [sys.argv[0], '--job', a.job]
        supervisor.main()
        return
    if a.watchdog:
        recovery.watchdog()
        return
    if a.finish:
        recovery.finish_all()
        return
    assert a.job == JOB
    with (REC / 'recovery-started.json').open('x') as f:
        json.dump({'at': now(), 'pid': os.getpid(), 'job': JOB}, f)
    oldpid = json.loads((ROOT / 'capacity_continuation/process.json').read_text())['pid']
    assert subprocess.run(['ps', '-p', str(oldpid)], stdout=subprocess.DEVNULL).returncode != 0
    assert (ROOT / 'capacity_continuation/finished.json').exists()
    oldpath = Path(execution_plan()['prior_states']['failed_boot_' + JOB])
    old = json.loads(oldpath.read_text())
    assert old['status'] == 'terminated' and old.get('ssh_key_deleted_at')
    out = folder(JOB)
    assert (out / 'cleanup.json').exists()
    assert not (out / 'dispatch-intent.json').exists()
    assert not (ROOT / 'execution' / JOB).exists()
    assert not statepath(JOB).exists()
    destination = REC / 'archived_nodes' / JOB
    destination.parent.mkdir(parents=True, exist_ok=True)
    assert not destination.exists()
    shutil.move(str(out), str(destination))
    out.mkdir(parents=True)
    # Start expanded cost protection before retiring its predecessor.
    background(SCRIPT, ['--watchdog'], REC / 'watchdog.log')
    for _ in range(100):
        if (REC / 'watchdog-started.json').exists():
            break
        time.sleep(.1)
    else:
        raise RuntimeError('Expanded watchdog did not start')
    oldrec = ROOT / 'setup_recovery'
    retired = []
    for receipt in ('watchdog-started.json', 'finisher-started.json'):
        pid = json.loads((oldrec / receipt).read_text())['pid']
        retired.append(recovery.retire(pid, 'recover_followup_shard_setup.py'))
    write_json(REC / 'retired-local-monitors.json', {'at': now(), 'processes': retired})
    background(SCRIPT, ['--finish'], REC / 'finisher.log')
    bundle = {k: Path(v['path']) for k, v in json.loads((ROOT / 'bundle.json').read_text()).items()}
    recovery.acquire(JOB, bundle)
    write_json(REC / 'recovery-dispatched.json', {'at': now(), 'job': JOB, 'repeated_model_work': False})


if __name__ == '__main__':
    try:
        main()
    except BaseException as e:
        write_json(REC / ('error-' + str(os.getpid()) + '.json'), {'at': now(), 'error': str(e)})
        raise
