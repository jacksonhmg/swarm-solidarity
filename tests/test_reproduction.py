import ast
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from reproduction_support import validate_inputs, gates, verify_output_association


class ReproductionTests(unittest.TestCase):
    def test_saved_inputs_and_order_preserved(self):
        for stage in ('004_replay', '005_clean'):
            items, cases = validate_inputs(stage)
            self.assertEqual(len(items), 40)
            self.assertEqual(len({x['case_id'] for x in items}), 40)
            self.assertTrue(all(cases[x['case_id']]['variant'] == 'clean' for x in items))

    def test_original_llm_constructor_unchanged(self):
        def constructor(path):
            tree = ast.parse(Path(path).read_text())
            node = next(n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'LLM')
            return ast.dump(node, include_attributes=False)
        self.assertEqual(constructor('scripts/run_prepared_inference.py'), constructor('scripts/run_reproduction.py'))

    def test_gate_requires_both_thresholds_and_complete_stage(self):
        def rows(n, exact, valid):
            return [{'strict_exact_table':i < exact,'strict_format_valid':i < valid} for i in range(n)]
        self.assertTrue(gates(rows(40,36,38))['pass'])
        self.assertFalse(gates(rows(40,35,40))['pass'])
        self.assertFalse(gates(rows(40,36,37))['pass'])
        self.assertFalse(gates(rows(39,39,39))['pass'])

    def test_misassociated_output_is_rejected(self):
        item={'replay_position':3,'prompt_token_ids':[4,5],'prompt':'saved'}
        output=SimpleNamespace(request_id='3',prompt_token_ids=[4,5],prompt='saved',outputs=[None])
        verify_output_association(item,output)
        output.request_id='4'
        with self.assertRaises(AssertionError):verify_output_association(item,output)
        output.request_id='3';output.prompt_token_ids=[4,6]
        with self.assertRaises(AssertionError):verify_output_association(item,output)


if __name__ == '__main__':unittest.main()
