import ast
from pathlib import Path
import unittest


class A100AmendmentTests(unittest.TestCase):
    def test_only_authorized_constructor_override(self):
        def call(path):
            return next(n for n in ast.walk(ast.parse(Path(path).read_text()))
                        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'LLM')
        original = call('scripts/run_prepared_inference.py')
        amended = call('scripts/run_reproduction_a100.py')
        overrides = [k for k in amended.keywords if k.arg == 'max_num_batched_tokens']
        self.assertEqual(len(overrides), 1)
        self.assertEqual(ast.literal_eval(overrides[0].value), 16384)
        amended.keywords = [k for k in amended.keywords if k.arg != 'max_num_batched_tokens']
        self.assertEqual(ast.dump(original), ast.dump(amended))


if __name__ == '__main__':unittest.main()
