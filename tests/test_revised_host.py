"""Offline invariants for the authorized hardware/scheduling-only amendment."""
import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import revised_host_support as support

class HostAmendmentTests(unittest.TestCase):
    def test_inference_only_changes_hardware_guard_and_provenance(self):
        source=(ROOT/'scripts/run_revised_eval.py').read_text()
        source=source.replace("assert torch.cuda.get_device_name(0) == 'NVIDIA A100-SXM4-40GB'", "assert torch.cuda.get_device_name(0) in ('NVIDIA A100-SXM4-40GB', 'NVIDIA A100-SXM4-80GB')")
        source=source.replace("runtime['runner_entry_point'] = 'scripts/run_revised_eval.py'", "runtime['runner_entry_point'] = 'scripts/run_revised_host_eval.py'")
        source=source.replace("runtime['execution_plan'] = json.loads((LOG / 'execution_plan.json').read_text())", "runtime['execution_plan'] = json.loads((LOG / 'host_plan.json').read_text())")
        self.assertEqual(source,(ROOT/'scripts/run_revised_host_eval.py').read_text())

    def test_raw_association_scoring_loop_unchanged(self):
        def loop(path):
            tree=ast.parse((ROOT/path).read_text())
            return next(n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and ast.unparse(n.target).startswith('(index,'))
        self.assertEqual(ast.dump(loop('scripts/verify_revised.py')),ast.dump(loop('scripts/verify_revised_host.py')))

    def test_cost_and_disjoint_assignments(self):
        p=support.plan()
        self.assertEqual(p['additional_cap_usd'],65)
        self.assertEqual(p['termination_threshold_usd'],63)
        self.assertEqual(sorted(p['assignments'].values()),list(range(8)))
        for kind in p['instance_types']: self.assertTrue(support.cost_feasible(kind))
        self.assertAlmostEqual(p['projected_wall_seconds']/3600*22.32,58.9774509279,places=8)

    def test_billing_includes_launch_and_rounds_up(self):
        import datetime as dt
        s={'launch_requested_at':'2026-09-24T10:00:00+00:00','usd_per_hour':22.32,'status':'active','instance_id':'owned-only'}
        with patch.object(support,'state',lambda:s):
            result=support.snapshot(dt.datetime.fromisoformat('2026-09-24T10:01:01+00:00'))
        self.assertEqual(result['rounded_elapsed_minutes'],2)
        self.assertAlmostEqual(result['estimated_total_usd'],.744)
        s.update(status='terminated',first_termination_confirmed_at='2026-09-24T10:01:01+00:00')
        with patch.object(support,'state',lambda:s):
            result=support.snapshot(dt.datetime.fromisoformat('2026-09-25T10:01:01+00:00'))
        self.assertEqual(result['rounded_elapsed_minutes'],2)

    def test_download_verifier_uses_remote_paths_without_touching_freeze(self):
        import revised_host_supervisor as supervisor
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);host=root/'host';remote=host/'remote';remote.mkdir(parents=True)
            (remote/'controller-result.json').write_text('{"returncode":0}')
            stage=root/'execution/prepared';stage.mkdir(parents=True)
            (stage/'responses.jsonl').write_text('representative already-collected data\n')
            hashes={'host/controller-result.json':support.sha(remote/'controller-result.json'),
                    'execution/prepared/responses.jsonl':support.sha(stage/'responses.jsonl')}
            (remote/'remote-artifact-hashes.json').write_text(json.dumps(hashes))
            with patch.multiple(supervisor,HOST=host,LOG=root),patch.object(supervisor,'collect',lambda:None),patch.object(supervisor,'remote',lambda *args:None):
                self.assertEqual(supervisor.finalize_hashes(),2)
                (stage/'responses.jsonl').write_text('tampered')
                with self.assertRaises(AssertionError):supervisor.finalize_hashes()

if __name__=='__main__':unittest.main()
