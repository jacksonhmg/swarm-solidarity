"""Offline contract tests; no sampling, training, or checkpoint forward pass."""
import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,'scripts')
from transformers_conflict_support import STAGES,validate_inputs,verify_clean_gate,sha,write_json
from analyze_transformers_conflict import paired_test
from swarm_solidarity.paired_conflict import bootstrap_draws


class TransformersConflictTests(unittest.TestCase):
    def test_saved_inputs(self):
        pairs=[]
        for stage,n in STAGES.items():
            items,cases=validate_inputs(stage)
            self.assertEqual(len(items),n)
            pairs += [(i['case_id'],i['source_condition']) for i in items]
        self.assertEqual(len(set(pairs)),320)

    def test_successful_007_inference_code_unchanged(self):
        old=ast.parse(Path('scripts/run_transformers_check.py').read_text())
        new=ast.parse(Path('scripts/run_transformers_conflict.py').read_text())
        for name in ('finish','plain','observe_logits','observe_stops'):
            find=lambda tree:next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
            self.assertEqual(ast.dump(find(old)),ast.dump(find(new)),name)
        # Actual model loading, seed, input tensor, attention mask, generate and
        # decode calls must remain syntactically identical to successful 007.
        names={'AutoModelForCausalLM.from_pretrained','AutoTokenizer.from_pretrained','set_seed',
               'torch.tensor','torch.ones_like','model.generate','tokenizer.decode',
               'GenerationConfig.from_dict','model.to','torch.inference_mode'}
        calls=lambda tree:[ast.dump(n) for n in ast.walk(tree) if isinstance(n,ast.Call) and ast.unparse(n.func) in names]
        self.assertEqual(calls(old),calls(new))
        self.assertEqual(Path('scripts/merge_transformers_conflict.py').read_text(),
            Path('scripts/merge_transformers_check.py').read_text().replace('007_transformers_check','008_transformers_conflict').replace('fixed vLLM evaluation','fixed Transformers evaluation'))

    def test_both_clean_cells_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for stage in ('prepared_clean','prompt_only_clean'):
                out=root/stage;out.mkdir()
                (out/'responses.jsonl').write_text('{}\n'*40)
                rows=[{'strict_exact_table':i<36,'strict_format_valid':i<38} for i in range(40)]
                (out/'scores.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
                write_json(out/'metadata.json',{'status':'complete',**{k+'_sha256':sha(out/(k+'.jsonl')) for k in ('responses','scores')}})
            self.assertEqual(len(verify_clean_gate(root)),2)
            out=root/'prompt_only_clean'
            rows[35]['strict_exact_table']=False
            (out/'scores.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
            write_json(out/'metadata.json',{'status':'complete',**{k+'_sha256':sha(out/(k+'.jsonl')) for k in ('responses','scores')}})
            with self.assertRaises(AssertionError):verify_clean_gate(root)

    def test_exact_sparse_pairs_and_unknowns(self):
        a=[True]*4+[False]*36;b=[False]*40
        result=paired_test(a,b,bootstrap_draws(40,2718,10))
        self.assertEqual(result['exact_paired_test']['p_value'],.125)
        a[0]=None
        result=paired_test(a,b,bootstrap_draws(40,2718,10))
        self.assertEqual(result['exact_paired_test']['complete_pairs'],39)
        self.assertEqual(result['exact_paired_test']['p_value'],.25)
        result=paired_test(b,b,bootstrap_draws(40,2718,10))
        self.assertEqual(result['exact_paired_test']['p_value'],1)


if __name__=='__main__':unittest.main()
