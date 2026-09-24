"""Scheduling amendment tests without GPU execution or cloud mutation."""
import ast
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,'scripts')
import corrective_parallel_support as support


class ParallelTests(unittest.TestCase):
    def test_aggregate_counts_original_elapsed_and_stops_terminated_clock(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/'a.json';b=Path(tmp)/'b.json'
            a.write_text(json.dumps({'launch_requested_at':'2026-09-24T00:00:00+00:00','usd_per_hour':1.99,'status':'active','instance_id':'a'}))
            b.write_text(json.dumps({'launch_requested_at':'2026-09-24T00:30:00+00:00','usd_per_hour':1.99,'status':'terminated','first_termination_confirmed_at':'2026-09-24T00:50:01+00:00','instance_id':'b'}))
            config={'aggregate_cap_usd':40,'nodes':{'primary':{'state':str(a)},'extra':{'state':str(b)}}}
            with patch.object(support,'plan',return_value=config):
                result=support.cost_snapshot(dt.datetime.fromisoformat('2026-09-24T01:00:00+00:00'))
            self.assertAlmostEqual(result['estimated_total_usd'],1.99*(60+21)/60)
            self.assertEqual(result['nodes'][1]['rounded_elapsed_minutes'],21)

    def test_frozen_inference_and_analysis_remain_identical(self):
        import hashlib
        freeze=json.loads(Path('experiment_log/010_corrective_comparison/freeze.json').read_text())['files']
        for name in ('scripts/run_corrective_eval.py','scripts/analyze_corrective.py','scripts/train_corrective.py','src/swarm_solidarity/paired_conflict.py'):
            self.assertEqual(hashlib.sha256(Path(name).read_bytes()).hexdigest(),freeze[name])

    def test_raw_verification_and_training_checks_unchanged(self):
        old=ast.parse(Path('scripts/verify_corrective.py').read_text());new=ast.parse(Path('scripts/verify_corrective_parallel.py').read_text())
        loops=lambda tree:[ast.dump(n) for n in tree.body if isinstance(n,ast.For) and ast.unparse(n.iter) in ('STAGES.items()',"config['training_execution_order']")]
        self.assertEqual(loops(old),loops(new))

    def test_assignments_partition_all_six_conditions(self):
        if not support.PLAN.exists():self.skipTest('Plan awaiting final training merge')
        plan=support.plan();items=[c for n in plan['nodes'].values() for c in n['conditions']]
        self.assertEqual(len(items),6);self.assertEqual(len(set(items)),6)
        self.assertTrue(all(len(n['conditions'])==2 for n in plan['nodes'].values()))
        self.assertEqual(plan['aggregate_cap_usd'],40)
        self.assertEqual(plan['aggregate_termination_threshold_usd'],38)


if __name__=='__main__':unittest.main()
