"""Cumulative-cost and cleanup accounting for the explicitly approved resumption."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import revised_a100_return as run

class ReturnAccountingTests(unittest.TestCase):
    def test_cost_includes_failed_h100(self):
        with patch.object(run,'snapshot',lambda:{'estimated_total_usd':42.0}):d=run.cost()
        self.assertAlmostEqual(d['estimated_total_usd'],42.38383333333333)
        self.assertEqual(d['termination_threshold_usd'],62)
        self.assertEqual(d['current_host_estimated_usd'],42)

    def test_cleanup_preserves_single_host_receipt_and_combines_cost(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);ret=root/'return';ret.mkdir()
            base={'estimated_gpu_cost_usd':42.0,'status':'terminated','within_cap':True}
            def original():(root/'cloud_lifecycle.json').write_text(json.dumps(base))
            with patch.multiple(run,LOG=root,RETURN=ret),patch.object(run,'original_cleanup',original):run.cleanup()
            self.assertEqual(json.loads((ret/'host_cloud_lifecycle.json').read_text()),base)
            combined=json.loads((root/'cloud_lifecycle.json').read_text())
            self.assertAlmostEqual(combined['estimated_gpu_cost_usd'],42.38383333333333)
            self.assertTrue(combined['all_allocated_instances_terminated'])

if __name__=='__main__':unittest.main()
