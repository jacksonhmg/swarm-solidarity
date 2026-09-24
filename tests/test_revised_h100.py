"""H100 scheduling amendment: preserve model computation and accounting."""
import ast
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import revised_h100_support as support

class H100AmendmentTests(unittest.TestCase):
    def test_generation_only_changes_hardware_and_provenance(self):
        expected=Path('scripts/run_revised_eval.py').read_text().replace('NVIDIA A100-SXM4-40GB','NVIDIA H100 PCIe')
        expected=expected.replace("runtime['runner_entry_point'] = 'scripts/run_revised_eval.py'","runtime['runner_entry_point'] = 'scripts/run_revised_h100_eval.py'")
        expected=expected.replace("(LOG / 'execution_plan.json')","(LOG / 'h100_plan.json')")
        self.assertEqual(expected,Path('scripts/run_revised_h100_eval.py').read_text())

    def test_node_computation_only_changes_hardware_and_paths(self):
        expected=Path('scripts/run_revised_node.py').read_text().replace('from revised_parallel_support import','from revised_h100_support import').replace('NVIDIA A100-SXM4-40GB','NVIDIA H100 PCIe').replace('scripts/run_revised_eval.py','scripts/run_revised_h100_eval.py').replace('scripts/run_revised_node.py','scripts/run_revised_h100_node.py')
        self.assertEqual(expected,Path('scripts/run_revised_h100_node.py').read_text())

    def test_raw_scoring_and_association_loop_unchanged(self):
        def loop(path):
            tree=ast.parse(Path(path).read_text())
            return next(n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and ast.unparse(n.target).startswith('(index,'))
        self.assertEqual(ast.dump(loop('scripts/verify_revised.py')),ast.dump(loop('scripts/verify_revised_h100.py')))

    def test_eight_disjoint_assignments_and_budget(self):
        p=support.plan();conditions=[c for n in p['nodes'].values() for c in n['conditions']]
        self.assertEqual(len(conditions),8);self.assertEqual(set(conditions),set(support.CONDITIONS))
        self.assertEqual(len({s['state'] for s in p['nodes'].values()}),8)
        self.assertEqual(p['aggregate_cap_usd'],65);self.assertEqual(p['aggregate_termination_threshold_usd'],63)
        self.assertLess(p['projected_total_usd'],63)
        self.assertEqual(p['gpu_name'],'NVIDIA H100 PCIe')

    def test_aggregate_rounding_and_completed_cost(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory);nodes={}
            for i in range(8):
                f=p/(str(i)+'.json');nodes[str(i)]={'state':str(f)}
                state={'launch_requested_at':'2026-09-24T10:00:00+00:00','status':'active','usd_per_hour':3.29}
                if i==0:state.update(status='terminated',first_termination_confirmed_at='2026-09-24T10:00:30+00:00')
                f.write_text(json.dumps(state))
            with patch.object(support,'plan',lambda:{'nodes':nodes}):
                result=support.cost_snapshot(dt.datetime.fromisoformat('2026-09-24T10:01:01+00:00'))
            self.assertEqual(result['hard_ceiling_usd'],65)
            self.assertAlmostEqual(result['estimated_total_usd'],15/60*3.29)

if __name__=='__main__':unittest.main()
