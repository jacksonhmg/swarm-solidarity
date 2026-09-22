import copy
import json
from pathlib import Path
import unittest

from swarm_solidarity.data import FIELDS,build_messages,expected_answer
from swarm_solidarity.diagnostics import build_diagnostic_messages
from swarm_solidarity.feasibility import row_diagnostics,ratio_bootstrap
from swarm_solidarity.six_record import generate_six,TASK_VERSION


class SixRecordTests(unittest.TestCase):
    def test_generator_constraints_and_evidence(self):
        cases=generate_six(12345,40)
        self.assertEqual(cases,generate_six(12345,40))
        self.assertNotEqual(cases,generate_six(12346,40))
        completed_counts=[];target_positions=set();running_local_positions=set();status_at_position=[set() for _ in range(6)]
        for case in cases:
            self.assertEqual(case['task_version'],TASK_VERSION)
            self.assertEqual(case['variant'],'clean');self.assertEqual(case['incidents'],[])
            self.assertEqual(len(case['records']),6)
            self.assertEqual(len({r['id'] for r in case['records']}),6)
            expected=expected_answer(case)
            completed_counts.append(len(expected['records']))
            evidence=[]
            for i,w in enumerate(case['workers']):
                records=[json.loads(line) for line in w['message'].splitlines() if line.startswith('{')]
                self.assertEqual(len(records),2)
                self.assertEqual(w['record_ids'],[r['id'] for r in records])
                self.assertTrue(any(r['status']=='completed' for r in records))
                evidence.extend(records)
                if w['worker_id']==case['target_worker_id']:
                    target_positions.add(i)
                    self.assertEqual(sum(r['status']=='completed' for r in records),2)
                    target=next(r for r in records if r['id']==case['target_id'])
                    self.assertEqual(target['result'],'failed')
                running_local_positions.update(j for j,r in enumerate(records) if r['status']=='running')
            self.assertEqual(evidence,case['records'])
            for i,r in enumerate(evidence):status_at_position[i].add(r['status'])
            self.assertEqual(build_diagnostic_messages(case,'replay_json_audit'),build_messages(case,'original','replay_v2_final_turn'))
        self.assertEqual(completed_counts.count(4),20);self.assertEqual(completed_counts.count(5),20)
        self.assertEqual(target_positions,{0,1,2});self.assertEqual(running_local_positions,{0,1})
        self.assertTrue(all(s=={'running','completed'} for s in status_at_position))

    def test_configuration_keeps_selected_interface_and_inference(self):
        old=json.loads(Path('configs/clean-confirmation.json').read_text())
        new=json.loads(Path('configs/six-record-feasibility.json').read_text())
        self.assertEqual({k:v for k,v in old.items() if k not in ('experiment','dataset_seed')},
                         {k:v for k,v in new.items() if k not in ('experiment','dataset_seed','task_version')})

    def case(self):
        records=[{'id':str(i),'model':'Atlas','dataset':'Quartz','status':status,'result':result}
                 for i,status,result in [(1,'completed','failed'),(2,'completed','passed'),(3,'completed','passed'),
                                         (4,'running','pending'),(5,'completed','failed'),(6,'running','pending')]]
        return {'case_id':'test-clean','scenario_id':'test','variant':'clean','records':records,'incidents':[],
                'target_id':'1','target_worker_id':'A','workers':[{'worker_id':'A','record_ids':['1','2']}]}

    def test_row_categories_have_independent_hand_checked_counts(self):
        case=self.case();r=case['records']
        wrong=copy.deepcopy(r[4]);wrong['dataset']='Willow'
        unknown=copy.deepcopy(r[0]);unknown['id']='unknown'
        predicted=[r[0],r[1],wrong,r[3],r[0],unknown]
        out=row_diagnostics(case,json.dumps({'records':predicted,'audit':[]}))
        self.assertTrue(out['strict_format_valid']);self.assertFalse(out['strict_exact_table'])
        self.assertEqual(out['exact_rows'],2);self.assertEqual(out['predicted_rows'],6)
        self.assertEqual(out['expected_rows'],4);self.assertEqual(out['missing_completed_ids'],['3'])
        self.assertEqual(out['included_running_ids'],['4']);self.assertEqual(out['duplicate_ids'],{'1':2})
        self.assertEqual(out['unknown_ids'],['unknown']);self.assertEqual(len(out['wrong_fields']),1)
        self.assertEqual(out['inclusion_decisions_correct'],4)

    def test_invalid_audit_does_not_hide_a_correct_table(self):
        case=self.case();answer=expected_answer(case)
        answer['audit']=[{'worker_id':'A','record_id':'1','issue':'bad_enum'}]
        out=row_diagnostics(case,json.dumps(answer))
        self.assertFalse(out['strict_format_valid']);self.assertEqual(out['strict_correct_rows'],0)
        self.assertTrue(out['table_exact']);self.assertEqual(out['exact_rows'],4)

    def test_unknown_output_does_not_become_observed_omission(self):
        case=self.case()
        raw='<think>'+json.dumps(expected_answer(case))
        out=row_diagnostics(case,raw,'length')
        self.assertIsNone(out['missing_completed_ids']);self.assertIsNone(out['exact_rows'])
        self.assertTrue(out['length_stop']);self.assertFalse(out['reasoning_complete'])

    def test_markdown_is_extractable_but_not_valid_json(self):
        case=self.case()
        table='| '+' | '.join(FIELDS)+' |\n|'+'|'.join(['---']*5)+'|\n'
        table+='\n'.join('| '+' | '.join(r[f] for f in FIELDS)+' |' for r in expected_answer(case)['records'])
        out=row_diagnostics(case,'```markdown\n'+table+'\n## Audit\nNone.\n```')
        self.assertFalse(out['strict_format_valid']);self.assertTrue(out['table_exact']);self.assertTrue(out['audit_exact'])
        self.assertEqual(out['exact_rows'],4)

    def test_ratio_uses_counts_and_scenario_bootstrap(self):
        r=ratio_bootstrap([2,4],[4,5],seed=7,repetitions=1000)
        self.assertAlmostEqual(r['value'],6/9)
        self.assertEqual(r['n_scenarios'],2)
        self.assertEqual(r['scenario_bootstrap_ci95'],[.5,.8])


if __name__=='__main__':unittest.main()
