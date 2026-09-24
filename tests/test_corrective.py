"""Offline counterfactual data, supervision and unchanged inference contracts."""
import ast
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,'scripts')
from swarm_solidarity.corrective import TRAIN_NOTES,EVAL_NOTES,training_arms,evaluation_cases
from swarm_solidarity.data import expected_answer
from swarm_solidarity.paired_conflict import score_paired


class CorrectiveTests(unittest.TestCase):
    def test_matched_arms_and_no_omission_demonstrations(self):
        arms=training_arms(20260928)
        self.assertEqual(len(arms['ordinary']),1000)
        self.assertEqual(arms['ordinary'][800:],arms['corrective'][800:])
        swapped=0
        for a,b in zip(arms['ordinary'][:800],arms['corrective'][:800]):
            self.assertEqual(a['case']['records'],b['case']['records'])
            self.assertEqual(json.loads(a['answer'])['records'],json.loads(b['answer'])['records'])
            if b['kind']=='corrective':
                swapped+=1
                self.assertEqual(b['case']['variant'],'falsification')
                self.assertEqual(json.loads(b['answer'])['audit'][0]['issue'],'falsification')
                self.assertTrue(score_paired(b['case'],b['answer'])['strict_table_plus_exact_audit'])
            else:self.assertEqual(a,b)
        self.assertEqual(swapped,400)
        self.assertNotIn('omission',TRAIN_NOTES)
        self.assertFalse(set(sum(map(list,TRAIN_NOTES.values()),[]))&set(sum(map(list,EVAL_NOTES.values()),[])))

    def test_four_variants_change_only_note_and_gold_audit(self):
        cases=evaluation_cases(123,10)
        for start in range(0,40,4):
            group=cases[start:start+4]
            for c in group:
                self.assertEqual(c['records'],group[0]['records'])
                self.assertTrue(score_paired(c,json.dumps(expected_answer(c)))['strict_table_plus_exact_audit'])
                for a,b in zip(group[0]['workers'],c['workers']):
                    self.assertEqual(a['record_ids'],b['record_ids'])
                    stripped=lambda w:[x for x in w['message'].splitlines() if not x.startswith('Worker note:')]
                    self.assertEqual(stripped(a),stripped(b))

    def test_preparation_encoder_body_unchanged(self):
        fn=lambda path:next(n for n in ast.parse(Path(path).read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='encode_example')
        self.assertEqual(ast.dump(fn('src/swarm_solidarity/preparation.py')),ast.dump(fn('src/swarm_solidarity/corrective.py')))

    def test_successful_inference_calls_unchanged(self):
        path=Path('scripts/run_corrective_eval.py')
        if not path.exists():self.skipTest('Runner not yet frozen')
        old=ast.parse(Path('scripts/run_transformers_conflict.py').read_text());new=ast.parse(path.read_text())
        for name in ('finish','plain','observe_logits','observe_stops'):
            find=lambda tree:next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
            self.assertEqual(ast.dump(find(old)),ast.dump(find(new)),name)
        names={'AutoModelForCausalLM.from_pretrained','AutoTokenizer.from_pretrained','set_seed','torch.tensor',
            'torch.ones_like','model.generate','tokenizer.decode','GenerationConfig.from_dict','model.to','torch.inference_mode'}
        calls=lambda tree:[ast.dump(n) for n in ast.walk(tree) if isinstance(n,ast.Call) and ast.unparse(n.func) in names]
        self.assertEqual(calls(old),calls(new))


class CorrectiveAnalysisTests(unittest.TestCase):
    def test_holm_and_margin(self):
        from analyze_corrective import holm,margin_decision
        self.assertEqual(holm([.03,.001,.2]),[.06,.003,.2])
        self.assertEqual(margin_decision([-.049,0]),'preservation_supported')
        self.assertEqual(margin_decision([-.05,.1]),'inconclusive')
        self.assertEqual(margin_decision([-.07,-.051]),'meaningful_regression')
        self.assertEqual(margin_decision(None),'inconclusive')


if __name__=='__main__':unittest.main()
