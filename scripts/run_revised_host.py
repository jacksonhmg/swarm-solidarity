#!/usr/bin/env python3
"""One setup and eight disjoint serial workers. No restart path."""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import time
from revised_host_support import LOG, HOST, plan, verify, now, sha, write_json

def execute():
    verify()
    execution = LOG/'execution'; execution.mkdir(exist_ok=False)
    selection = json.loads((HOST/'selection.json').read_text())
    expected = plan()['instance_types'][selection['instance_type']]['gpu_name']
    env = os.environ.copy()
    env.update(HF_HUB_DISABLE_TELEMETRY='1', TOKENIZERS_PARALLELISM='false')
    env['PATH'] = str(Path.home()/'.local/bin')+':'+env['PATH']
    def run(command, name, directory=HOST, environment=env):
        with (directory/(name+'.log')).open('x') as output:
            subprocess.run(command, env=environment, stdout=output, stderr=subprocess.STDOUT, check=True)
    run(['python3','-m','pip','install','--user','uv==0.8.22'], 'uv-install')
    run(['uv','venv','--python','3.11.13','.venv-gpu'], 'venv')
    run(['uv','pip','sync','--python','.venv-gpu/bin/python','requirements-preparation.txt'], 'packages')
    versions = subprocess.check_output(['uv','pip','freeze','--python','.venv-gpu/bin/python'], env=env)
    (HOST/'gpu-environment.txt').write_bytes(versions)
    assert versions == Path('experiment_log/004_task_preparation/gpu-environment.txt').read_bytes()
    names = subprocess.check_output(['nvidia-smi','--query-gpu=name','--format=csv,noheader'], text=True).splitlines()
    uuids = subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'], text=True).splitlines()
    assert names == [expected]*8 and len(set(uuids)) == 8, names
    (HOST/'nvidia-smi.txt').write_bytes(subprocess.check_output(['nvidia-smi']))
    run(['.venv-gpu/bin/python','scripts/merge_revised_base.py'], 'merge-base')
    cpus = sorted(os.sched_getaffinity(0)); assert len(cpus) >= 8
    assignments = {}
    for stage, gpu in plan()['assignments'].items():
        assignments[stage] = {'gpu_index':gpu, 'gpu_uuid':uuids[gpu], 'gpu':expected,
                              'cpu_affinity':cpus[gpu::8], 'responses':800,
                              'entry_point':'scripts/run_revised_host_eval.py',
                              'entry_point_sha256':sha('scripts/run_revised_host_eval.py')}
    write_json(HOST/'assignments.json', assignments)

    def worker(stage):
        a = assignments[stage]; out = HOST/'workers'/stage; out.mkdir(parents=True, exist_ok=False)
        worker_env = dict(env, CUDA_VISIBLE_DEVICES=str(a['gpu_index']))
        prefix = ['taskset','--cpu-list',','.join(map(str,a['cpu_affinity'])),'.venv-gpu/bin/python']
        result = {'stage':stage, 'started_at':now(), **a}
        write_json(out/'started.json', result)
        try:
            if stage.startswith('revised_'):
                run(prefix+['scripts/train_revised.py','--run',stage], 'training', out, worker_env)
            if stage not in ('prepared','prompt_only'):
                run(prefix+['scripts/merge_revised_adapter.py','--run',stage], 'merge', out, worker_env)
            verify()
            assert not (execution/stage).exists(), 'Never restart sampled requests'
            run(prefix+['scripts/run_revised_host_eval.py','--stage',stage], 'inference', out, worker_env)
            assert json.loads((execution/stage/'metadata.json').read_text())['status'] == 'complete'
            result.update(status='complete', returncode=0)
        except BaseException as exc:
            result.update(status='failed', returncode=1, error=type(exc).__name__+': '+str(exc))
            raise
        finally:
            result['finished_at'] = now(); write_json(out/'result.json', result)

    # On any failure, the outer timeout process group is killed; no workers are retried.
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=8)
    futures = [pool.submit(worker, stage) for stage in assignments]
    for future in concurrent.futures.as_completed(futures): future.result()
    pool.shutdown()

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--execute',action='store_true'); args=parser.parse_args()
    if args.execute: execute(); return
    verify(); HOST.mkdir(parents=True,exist_ok=True)
    selection=json.loads((HOST/'selection.json').read_text())
    import datetime as dt
    deadline=dt.datetime.fromisoformat(selection['launch_requested_at']).timestamp()+plan()['termination_threshold_usd']/selection['usd_per_hour']*3600-150
    remaining=int(deadline-time.time()); assert remaining>0
    command=['timeout','--signal=TERM','--kill-after=30s',str(remaining)+'s','python3','scripts/run_revised_host.py','--execute']
    receipt={'pid':os.getpid(),'started_at':now(),'timeout_seconds':remaining,'command':command}
    with (HOST/'controller-launch.json').open('x') as f: json.dump(receipt,f,indent=2)
    proc=subprocess.Popen(command, start_new_session=True)
    # A worker error is surfaced through its result file even if sibling threads remain active.
    while proc.poll() is None:
        failed=[p for p in (HOST/'workers').glob('*/result.json') if json.loads(p.read_text())['returncode']]
        if failed:
            import signal
            os.killpg(proc.pid,signal.SIGTERM)
            try: proc.wait(timeout=30)
            except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL)
            break
        time.sleep(5)
    code=proc.wait()
    write_json(HOST/'controller-result.json',{**receipt,'finished_at':now(),'returncode':code})

if __name__=='__main__': main()
