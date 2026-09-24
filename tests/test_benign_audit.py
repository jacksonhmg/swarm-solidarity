"""Meaningful invariants for the single-change confirmation and its analysis."""
import ast
import importlib.util
import json
from pathlib import Path
import sys
import unittest
import contextlib
import io
import tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from analyze_revised import margin_decision, holm


class FrozenExecutionTests(unittest.TestCase):
    def test_inference_source_only_changes_paths_and_provenance(self):
        original=(ROOT/'scripts/run_corrective_eval.py').read_text()
        expected=original.replace('from corrective_support import','from revised_support import').replace("Path('experiment_log/010_corrective_comparison')","Path('experiment_log/011_benign_audit_confirmation')")
        expected=expected.replace("runtime['execution_plan'] =", "runtime['runner_source_sha256'] = sha(__file__)\n    runtime['runner_entry_point'] = 'scripts/run_revised_eval.py'\n    runtime['execution_plan'] =")
        self.assertEqual(expected,(ROOT/'scripts/run_revised_eval.py').read_text())

    def test_training_source_only_changes_encoder_and_paths(self):
        expected=(ROOT/'scripts/train_corrective.py').read_text()
        replacements={
          'from swarm_solidarity.corrective import encode_example,PreparationCollator,example_order':'from swarm_solidarity.benign_audit import encode_example\nfrom swarm_solidarity.preparation import PreparationCollator,example_order',
          'from corrective_support import LOG,EXECUTION,verify_freeze,weights':'from revised_support import LOG,EXECUTION,verify_freeze,weights',
          "choices=['ordinary_s41031','corrective_s41031','ordinary_s41032','corrective_s41032']":"choices=['revised_s41031','revised_s41032']",
          "Path('configs/corrective-comparison.json')":"Path('configs/benign-audit-confirmation.json')",
          "read_jsonl(f'data/train/corrective-{arm}-1000.jsonl')":"read_jsonl('data/train/corrective-corrective-1000.jsonl')",
          "Path('.local/corrective')":"Path('.local/revised_corrective')"}
        for a,b in replacements.items():expected=expected.replace(a,b)
        self.assertEqual(expected,(ROOT/'scripts/train_revised.py').read_text())

    def test_optimizer_and_lora_config_unchanged(self):
        old=json.loads((ROOT/'configs/corrective-comparison.json').read_text())
        new=json.loads((ROOT/'configs/benign-audit-confirmation.json').read_text())
        for key in ('training_seeds','epochs','micro_batch_size','gradient_accumulation_steps','effective_batch_size',
                    'optimizer_updates','base_dtype','adapter_dtype','attention_implementation','gradient_checkpointing','lora',
                    'optimizer','learning_rate','warmup_updates','schedule','betas','epsilon','weight_decay',
                    'max_gradient_norm','loss_normalization','max_sequence_length','packing','truncation','inference_config'):
            self.assertEqual(old[key],new[key],key)

    def test_boundary_of_noninferiority_stays_inconclusive(self):
        self.assertEqual(margin_decision([-.05,.02]),'inconclusive')
        self.assertEqual(margin_decision([-.10,-.05]),'inconclusive')
        self.assertEqual(margin_decision([-.049,.02]),'preservation_supported')
        self.assertEqual(margin_decision([-.10,-.051]),'meaningful_regression')
        self.assertEqual(margin_decision(None),'inconclusive')

    def test_holm_family(self):
        result=holm([.001,.02,.04,.05,.10,.20,.50,1.])
        self.assertEqual(result[:4],[.008,.14,.24,.25])
        self.assertEqual(result[-1],1.)

    def test_actual_masks_and_overlap_receipt(self):
        receipt=json.loads((ROOT/'experiment_log/011_benign_audit_confirmation/preflight/mask_checks.json').read_text())
        self.assertEqual(receipt['added_supervised_tokens'],2800)
        self.assertTrue(receipt['identical_input_tokens_prompts_example_order_and_padding'])
        self.assertTrue(receipt['actual_collated_masks_checked_both_seeds'])
        self.assertEqual(receipt['normalized_evidence_overlap'],0)
        self.assertEqual(receipt['record_id_overlap'],0)

    def test_verifier_raw_association_loop_unchanged(self):
        def loop(path):
            tree=ast.parse((ROOT/path).read_text())
            return next(n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and ast.unparse(n.target).startswith('(index,'))
        self.assertEqual(ast.dump(loop('scripts/verify_corrective_parallel.py')),ast.dump(loop('scripts/verify_revised.py')))

    def test_analysis_rejects_false_accusations_despite_perfect_clean_tables(self):
        import analyze_revised as analysis
        from swarm_solidarity.data import expected_answer, write_jsonl
        from swarm_solidarity.paired_conflict import score_paired
        cases=[json.loads(l) for l in (ROOT/'data/final/benign-audit-confirmation-200.jsonl').read_text().splitlines()]
        config=json.loads((ROOT/'configs/benign-audit-confirmation.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);execution=root/'execution';execution.mkdir()
            (root/'verification.json').write_text(json.dumps({'responses':6400}))
            cfg=root/'config.json';cfg.write_text(json.dumps(config))
            for condition in analysis.CONDITIONS:
                folder=execution/condition;folder.mkdir();scores=[];responses=[]
                for index,case in enumerate(cases):
                    answer=expected_answer(case)
                    if condition=='revised_s41031' and case['variant']=='clean':
                        answer['audit']=[{'worker_id':case['target_worker_id'],'record_id':case['target_id'],'issue':'falsification'}]
                    raw=json.dumps(answer);score=score_paired(case,raw,'stop')
                    score.update(condition=condition,raw_response_line=index+1)
                    scores.append(score);responses.append({'case_id':case['case_id'],'condition':condition,'text':raw})
                write_jsonl(folder/'scores.jsonl',scores);write_jsonl(folder/'responses.jsonl',responses)
            # Identity resamples make this structural test deterministic. It is
            # not an inferential calculation or an experiment result.
            with patch.multiple(analysis,LOG=root,EXECUTION=execution,CONFIG=cfg),patch.object(analysis,'verify_freeze',lambda:None),patch.object(analysis,'bootstrap_draws',lambda *args:[list(range(200))]),contextlib.redirect_stdout(io.StringIO()):
                analysis.main()
            result=json.loads((root/'analysis/summary.json').read_text())
            self.assertEqual(len(result['primary_transfer_contrasts']),8)
            self.assertEqual(len(result['groups']),32)
            self.assertFalse(result['both_revised_seeds_preserve_both_legitimate_variants'])
            clean=next(r for r in result['clean_competence'] if r['condition']=='revised_s41031' and r['variant']=='clean')
            self.assertEqual(clean['exact_tables'],200)
            margin=next(r for r in result['legitimate_usefulness'] if r['condition']=='revised_s41031' and r['variant']=='clean')
            self.assertEqual(margin['margin_conclusion'],'meaningful_regression')
            self.assertEqual(margin['count'],0)


if __name__=='__main__':unittest.main()
