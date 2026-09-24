#!/usr/bin/env python3
"""Idempotent process dispatch with an atomic claim and no inherited SSH pipes.

The claim is never removed, including if startup fails. Repeated delivery of the
same operation returns the saved receipt and never launches a second process.
An uncertain acknowledgement therefore requires receipt reconciliation, not
automatic instance termination or an unguarded repeat of model work.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess

def dispatch(receipt, output, command):
    receipt=Path(receipt);output=Path(output)
    receipt.parent.mkdir(parents=True,exist_ok=True)
    claim={'status':'claimed','at':dt.datetime.now(dt.timezone.utc).isoformat(),
           'command':command,'working_directory':str(Path.cwd()),'output':str(output)}
    try:
        with receipt.open('x') as f:
            json.dump(claim,f);f.flush();os.fsync(f.fileno())
    except FileExistsError:
        saved=json.loads(receipt.read_text())
        assert saved['command']==command and saved['working_directory']==str(Path.cwd()),'Operation identity mismatch'
        return {**saved,'existing_dispatch':True}
    output.parent.mkdir(parents=True,exist_ok=True)
    try:
        with output.open('xb') as log:
            child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=log,
                stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
        claim.update(status='started',pid=child.pid)
    except BaseException as exc:
        claim.update(status='failed_start',error=type(exc).__name__+': '+str(exc))
        raise
    finally:
        temporary=receipt.with_suffix(receipt.suffix+'.tmp')
        with temporary.open('w') as f:
            json.dump(claim,f,indent=2);f.flush();os.fsync(f.fileno())
        temporary.replace(receipt)
    return {**claim,'existing_dispatch':False}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('command',nargs=argparse.REMAINDER);args=parser.parse_args()
    command=args.command[1:] if args.command[:1]==['--'] else args.command
    assert command,'A command is required'
    print(json.dumps(dispatch(args.receipt,args.output,command)),flush=True)

if __name__=='__main__':main()
