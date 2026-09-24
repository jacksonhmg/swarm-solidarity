"""Actual harmless processes test pipe detachment and idempotent delivery."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/dispatch_detached_once.py'

class DetachedDispatchTests(unittest.TestCase):
    def test_returns_with_pipes_closed_and_redelivery_does_not_repeat_work(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);receipt=root/'receipt.json';output=root/'output.log';marker=root/'executions'
            code='import time; from pathlib import Path; time.sleep(1.5); p=Path('+repr(str(marker))+'); p.write_text(p.read_text()+"one\\n" if p.exists() else "one\\n"); print("completed",flush=True)'
            command=[sys.executable,str(SCRIPT),'--receipt',str(receipt),'--output',str(output),'--',sys.executable,'-c',code]
            # If the child inherits either pipe, communicate cannot return until it exits.
            p=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            stdout,stderr=p.communicate(timeout=1)
            self.assertEqual(p.returncode,0,stderr);first=json.loads(stdout)
            self.assertFalse(marker.exists());self.assertEqual(first['status'],'started')
            second=json.loads(subprocess.check_output(command,text=True,timeout=1))
            self.assertTrue(second['existing_dispatch']);self.assertEqual(first['pid'],second['pid'])
            deadline=time.monotonic()+4
            while not marker.exists() and time.monotonic()<deadline:time.sleep(.05)
            self.assertEqual(marker.read_text(),'one\n')
            time.sleep(.1);self.assertEqual(output.read_text(),'completed\n')

    def test_changed_command_cannot_reuse_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);receipt=root/'receipt.json';output=root/'output.log'
            receipt.write_text(json.dumps({'status':'claimed','command':['original'],'working_directory':str(Path.cwd())}))
            p=subprocess.run([sys.executable,str(SCRIPT),'--receipt',str(receipt),'--output',str(output),'--','changed'],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0);self.assertFalse(output.exists())

if __name__=='__main__':unittest.main()
