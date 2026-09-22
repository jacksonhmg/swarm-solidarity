#!/usr/bin/env python3
"""Transfer committed code and execute commands on the single owned GPU host."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["upload", "download", "exec"])
    p.add_argument("command", nargs=argparse.REMAINDER)
    args = p.parse_args()
    state = json.loads(Path('.local/lambda-pilot/state.json').read_text())
    ssh = ['ssh', '-i', state['private_key_path'], '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
           '-o', 'StrictHostKeyChecking=accept-new', '-o', 'UserKnownHostsFile=.local/lambda-pilot/known_hosts']
    host = 'ubuntu@' + state['ip']
    root = '/home/ubuntu/swarm-solidarity'
    if args.action == 'upload':
        if subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip():
            raise SystemExit('Commit changes before uploading; only committed code is transferred')
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        archive = subprocess.Popen(['git', 'archive', 'HEAD'], stdout=subprocess.PIPE)
        command = f'mkdir -p {root} && tar -xf - -C {root} && printf %s {shlex.quote(revision)} > {root}/.code-revision'
        result = subprocess.run(ssh + [host, command], stdin=archive.stdout)
        archive.stdout.close()
        if archive.wait() or result.returncode:
            raise SystemExit('Upload failed')
        print('Uploaded committed revision', revision)
    elif args.action == 'download':
        # Download execution evidence only. Never overwrite locally edited
        # protocols, reports, or derived analysis with older remote copies.
        subprocess.run(['rsync', '-az', '--prune-empty-dirs', '--include=*/',
                        '--include=responses.jsonl', '--include=prompts.jsonl', '--include=metadata.json',
                        '--include=*.log', '--include=gpu-environment.txt', '--include=nvidia-smi.txt', '--exclude=*',
                        '-e', shlex.join(ssh), host + ':' + root + '/experiment_log/', 'experiment_log/'], check=True)
    else:
        command = args.command[1:] if args.command[:1] == ['--'] else args.command
        if not command:
            raise SystemExit('Pass a command after exec')
        result = subprocess.run(ssh + [host, 'cd ' + root + ' && ' + shlex.join(command)])
        raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
