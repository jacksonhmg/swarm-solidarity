import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import revised_infrastructure_retry as retry
import run_revised_retry_host as guard


class InfrastructureRetryTests(unittest.TestCase):
    def test_cumulative_cost_includes_both_lost_attempts(self):
        with patch.object(retry.support, 'snapshot', lambda:{'estimated_total_usd':42.0}):
            result = retry.cost()
        self.assertAlmostEqual(result['estimated_total_usd'], 46.0985)
        self.assertEqual(result['termination_threshold_usd'], 62)

    def test_remote_timeout_is_shortened_only_by_cumulative_cost(self):
        original = guard.original_plan()
        amended = guard.cumulative_plan()
        self.assertAlmostEqual(amended.pop('termination_threshold_usd'), 57.9015)
        original.pop('termination_threshold_usd')
        self.assertEqual(amended, original)

    def test_cleanup_preserves_current_and_cumulative_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); receipts=root/'retry'; receipts.mkdir()
            base={'estimated_gpu_cost_usd':42.0, 'status':'terminated'}
            def clean(): (root/'cloud_lifecycle.json').write_text(json.dumps(base))
            with patch.multiple(retry, LOG=root, RETRY=receipts), patch.object(retry.collector,'cleanup',clean):
                retry.cleanup()
            self.assertEqual(json.loads((receipts/'host_cloud_lifecycle.json').read_text()),base)
            combined=json.loads((root/'cloud_lifecycle.json').read_text())
            self.assertAlmostEqual(combined['estimated_gpu_cost_usd'],46.0985)
            self.assertTrue(combined['within_cap'])

    def test_supervisor_survives_transport_loss_without_restarting_work(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); host=root/'host'; host.mkdir(); receipts=root/'retry'; receipts.mkdir()
            calls=[]
            def collect():
                calls.append('collect')
                if len(calls)==1: raise subprocess.TimeoutExpired('read-only collection',45)
                (host/'remote').mkdir(exist_ok=True)
                (host/'remote/controller-result.json').write_text('{"returncode":0}')
            def clean(): calls.append('cleanup')
            with patch.multiple(retry, HOST=host, RETRY=receipts), \
                 patch.object(retry.collector,'collect',collect), \
                 patch.object(retry.collector,'finalize_hashes',lambda:7), \
                 patch.object(retry,'cleanup',clean), \
                 patch.object(retry.support,'state',lambda:{'status':'active'}), \
                 patch.object(retry,'cost',lambda:{'estimated_total_usd':5.0}), \
                 patch.object(retry.time,'sleep',lambda _:None), \
                 patch.object(retry.subprocess,'run',lambda *a,**k:subprocess.CompletedProcess(a,0)):
                retry.supervise()
            self.assertEqual(calls,['collect','collect','cleanup'])
            result=json.loads((host/'supervisor-result.json').read_text())
            self.assertIsNone(result['failure'])
            self.assertTrue(result['download_hashes_verified'])
            self.assertFalse((host/'abort.json').exists())

    def test_exclusive_launch_intent_blocks_second_post(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'launch-intent.json').write_text('{}')
            with patch.multiple(retry, RETRY=root, STATE=root/'absent-state'), \
                 patch.object(retry.subprocess,'run') as run:
                with self.assertRaises(FileExistsError):
                    retry.launch(('gpu_8x_a100','us-west-1',15.92),root/'archive')
                run.assert_not_called()


if __name__=='__main__': unittest.main()
