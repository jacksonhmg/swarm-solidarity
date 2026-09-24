import ast
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import revised_recovery_support as support


class RecoveryA100Tests(unittest.TestCase):
    def test_node_computation_unchanged_except_scheduling_paths(self):
        expected=Path('scripts/run_revised_node.py').read_text()
        expected=expected.replace('from revised_parallel_support import','from revised_recovery_support import')
        expected=expected.replace('scripts/run_revised_node.py','scripts/run_revised_recovery_node.py')
        expected=expected.replace("assert gpu=='NVIDIA A100-SXM4-40GB',gpu","assert gpu in plan()['accepted_gpu_names'],gpu").replace('run_revised_eval.py','run_revised_host_eval.py')
        self.assertEqual(expected,Path('scripts/run_revised_recovery_node.py').read_text())

    def test_raw_verification_and_scoring_loop_unchanged(self):
        def loop(path):
            tree=ast.parse(Path(path).read_text())
            return next(n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and ast.unparse(n.target).startswith('(index,'))
        self.assertEqual(ast.dump(loop('scripts/verify_revised.py')),ast.dump(loop('scripts/verify_revised_recovery.py')))

    def test_same_hardware_disjoint_conditions_budget_and_timeouts(self):
        plan=support.plan()
        self.assertEqual(plan['instance_type'],'gpu_1x_a100_sxm4')
        self.assertEqual(plan['accepted_gpu_names'],['NVIDIA A100-SXM4-40GB','NVIDIA A100-SXM4-80GB'])
        self.assertEqual(plan['new_rentals_maximum'],7)
        self.assertEqual(len(plan['retired_state_paths']),8)
        conditions=[c for s in plan['nodes'].values() for c in s['conditions']]
        self.assertEqual(len(conditions),8)
        self.assertEqual(set(conditions),set(support.CONDITIONS))
        self.assertEqual(len({s['state'] for s in plan['nodes'].values()}),8)
        self.assertEqual(plan['aggregate_cap_usd'],65)
        self.assertEqual(plan['aggregate_termination_threshold_usd'],62)
        self.assertLess(plan['projected_cumulative_with_20_percent_contingency_usd'],62)
        self.assertEqual(plan['node_timeout_minutes'],180)
        self.assertGreaterEqual(plan['launch_spacing_seconds'],12)

    def test_cumulative_accounting_includes_prior_and_stops_at_first_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            nodes={}
            for i in range(8):
                p=Path(directory)/(str(i)+'.json');nodes[str(i)]={'state':str(p)}
                s={'launch_requested_at':'2026-09-24T10:00:00+00:00','status':'active','usd_per_hour':1.99}
                if i==0:s.update(status='terminated',first_termination_confirmed_at='2026-09-24T10:00:30+00:00')
                p.write_text(json.dumps(s))
            with patch.object(support,'plan',lambda:{'nodes':nodes,'prior_gpu_cost_usd':4.0985,'retired_state_paths':[]}):
                result=support.cost_snapshot(dt.datetime.fromisoformat('2026-09-24T10:01:01+00:00'))
            self.assertAlmostEqual(result['estimated_total_usd'],4.0985+15/60*1.99)
            self.assertAlmostEqual(result['current_nodes_gpu_cost_usd'],15/60*1.99)

    def test_continuation_creates_directory_before_preparation(self):
        import continue_revised_startup as continuation
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'retained'
            def prepare(node,archives):
                self.assertTrue(folder.is_dir())
            with patch.object(continuation,'node_dir',lambda node:folder),patch.object(continuation,'prepare_node',prepare),patch.object(continuation,'upload_patch',lambda *args:None),patch.object(continuation,'verify_plan',lambda:None),patch.object(continuation,'dispatch',lambda node:None):
                result=continuation.start_assignment('revised_s41032',{},Path('patch'))
            self.assertEqual(result['status'],'dispatched')

    def test_local_startup_error_does_not_terminate_other_nodes(self):
        import continue_revised_startup as continuation
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'retained'
            def fail(*args):raise OSError('local receipt failure')
            with patch.object(continuation,'node_dir',lambda node:folder),patch.object(continuation,'prepare_node',fail):
                result=continuation.start_assignment('revised_s41032',{},Path('patch'))
            self.assertEqual(result['status'],'startup_error')
            self.assertTrue((folder/'startup-error.json').exists())
            self.assertFalse((folder.parent/'abort.json').exists())

    def test_retired_cost_added_and_retained_node_not_double_counted(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            old=root/'old.json';live=root/'live.json'
            old.write_text(json.dumps({'instance_id':'retired','launch_requested_at':'2026-09-24T10:00:00+00:00','status':'terminated','first_termination_confirmed_at':'2026-09-24T10:01:30+00:00','usd_per_hour':1.99}))
            live.write_text(json.dumps({'instance_id':'retained','launch_requested_at':'2026-09-24T10:00:00+00:00','status':'active','usd_per_hour':1.99}))
            plan={'nodes':{'retained':{'state':str(live)}},'prior_gpu_cost_usd':4.0985,'retired_state_paths':[str(old)]}
            with patch.object(support,'plan',lambda:plan):
                result=support.cost_snapshot(dt.datetime.fromisoformat('2026-09-24T10:03:00+00:00'))
            self.assertAlmostEqual(result['estimated_total_usd'],4.0985+5/60*1.99)
            self.assertEqual(len(result['nodes']),1)
            self.assertEqual(len(result['retired_nodes']),1)

    def test_node_hash_manifest_json_and_ownership_paths(self):
        import revised_recovery_supervisor as supervisor
        import os
        with tempfile.TemporaryDirectory() as directory:
            previous=Path.cwd();os.chdir(directory)
            try:
                root=Path('experiment_log/011_benign_audit_confirmation');out=root/'hardware_recovery/prepared';out.mkdir(parents=True)
                (out/'controller-result.json').write_text('{"returncode":0}')
                stage=root/'execution/prepared';stage.mkdir(parents=True)
                (stage/'responses.jsonl').write_text('representative already-collected output\n')
                def execute(node,command):exec(command[-1],{})
                with patch.multiple(supervisor,LOG=root),patch.object(supervisor,'node_spec',lambda node:{'conditions':['prepared']}),patch.object(supervisor,'collect',lambda node:None),patch.object(supervisor,'remote',execute):
                    self.assertEqual(supervisor.finalize_hashes('prepared'),2)
                manifest=json.loads((out/'remote-artifact-hashes.json').read_text())
                self.assertEqual(set(manifest),{'hardware_recovery/prepared/controller-result.json','execution/prepared/responses.jsonl'})
            finally:os.chdir(previous)


if __name__=='__main__':unittest.main()
