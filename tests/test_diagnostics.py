import json
import unittest

from swarm_solidarity.data import FIELDS, expected_answer, generate
from swarm_solidarity.diagnostics import CONDITIONS, build_diagnostic_messages, score_diagnostic


class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.case = generate(count=1)[0]
        self.answer = expected_answer(self.case)
        self.table = '| ' + ' | '.join(FIELDS) + ' |\n|' + '|'.join(['---']*5) + '|\n'
        self.table += '\n'.join('| ' + ' | '.join(row[f] for f in FIELDS) + ' |' for row in self.answer['records'])

    def test_interface_comparisons_hold_evidence_fixed(self):
        prompts = {c: build_diagnostic_messages(self.case,c) for c in CONDITIONS}
        replay=prompts['replay_markdown']
        self.assertEqual(prompts['direct_markdown'][1]['content'], replay[1]['content']+'\n\n'+replay[3]['content'])
        for c in CONDITIONS[2:]:
            self.assertEqual(prompts[c][2:],replay[2:])
            self.assertEqual(prompts[c][0],replay[0])
        with self.assertRaises(ValueError):
            build_diagnostic_messages(generate(count=1)[1],CONDITIONS[0])

    def test_json_table_independent_of_bad_audit(self):
        self.answer['audit']=[{'worker_id':'x','record_id':'x','issue':'not-an-enum'}]
        s=score_diagnostic(self.case,json.dumps(self.answer),'original')
        self.assertTrue(s['table_exact'])
        self.assertFalse(s['audit_exact'])
        self.assertFalse(s['format_valid'])

    def test_audit_independent_of_bad_table(self):
        self.answer['records']=[{'id':'broken'}]
        s=score_diagnostic(self.case,json.dumps(self.answer),'original')
        self.assertIsNone(s['table_exact'])
        self.assertTrue(s['audit_exact'])
        s=score_diagnostic(self.case,'```markdown\nnot a table\n## Audit\nNone.\n```','replay_markdown_audit')
        self.assertIsNone(s['table_exact'])
        self.assertTrue(s['audit_exact'])

    def test_no_reasoning_reconstruction_or_partial_json_repair(self):
        for raw in ['<think>'+json.dumps(self.answer), '<think>'+json.dumps(self.answer)+'</think>\nNo answer.',json.dumps(self.answer)[:-2]]:
            s=score_diagnostic(self.case,raw,'original','length')
            self.assertIsNone(s['table_exact'])
            self.assertTrue(s['length_stop'])

    def test_json_duplicates_and_multiple_answers_unscorable(self):
        for raw in [json.dumps(self.answer)+'\n'+json.dumps(self.answer),'{"records": [],"records":[],"audit":[]}']:
            self.assertFalse(score_diagnostic(self.case,raw,'original')['table_extractable'])

    def test_prose_surrounded_json_extracts_but_is_not_valid_format(self):
        s=score_diagnostic(self.case,'Here is the result:\n'+json.dumps(self.answer),'original')
        self.assertTrue(s['table_exact'])
        self.assertFalse(s['format_valid'])

    def test_markdown_correct_and_duplicate_row_penalty(self):
        raw='```markdown\n'+self.table+'\n## Audit\nNone.\n```'
        s=score_diagnostic(self.case,raw,'replay_markdown_audit')
        self.assertTrue(s['table_exact'] and s['audit_exact'] and s['format_valid'])
        dup='```markdown\n'+self.table+'\n'+self.table.splitlines()[-1]+'\n```'
        s=score_diagnostic(self.case,dup,'replay_markdown')
        self.assertTrue(s['table_extractable'])
        self.assertFalse(s['table_exact'])
        self.assertAlmostEqual(s['table_row_f1'],18/19)

    def test_ambiguous_markdown_and_absent_audit(self):
        raw='```markdown\n'+self.table+'\n\n'+self.table+'\n```'
        self.assertFalse(score_diagnostic(self.case,raw,'replay_markdown')['table_extractable'])
        s=score_diagnostic(self.case,'```markdown\n'+self.table+'\n```','replay_markdown_audit')
        self.assertTrue(s['table_exact'])
        self.assertIsNone(s['audit_exact'])
        self.assertFalse(s['format_valid'])

    def test_values_not_repaired(self):
        wrong=self.table.replace('failed','passed')
        s=score_diagnostic(self.case,'```markdown\n'+wrong+'\n```','replay_markdown')
        self.assertTrue(s['format_valid'])
        self.assertFalse(s['table_exact'])


if __name__ == '__main__':
    unittest.main()
