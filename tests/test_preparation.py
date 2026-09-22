import copy
import json
from pathlib import Path
import unittest

from swarm_solidarity.data import expected_answer
from swarm_solidarity.preparation import generate_training,encode_example,PreparationCollator,example_order


class PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from transformers import AutoTokenizer
            import torch
            import peft
        except ImportError as error:
            raise unittest.SkipTest('Preparation tests require the pinned local preparation environment') from error
        if not Path('.local/preparation/tokenizer/tokenizer.json').exists():
            raise unittest.SkipTest('Preparation tests require the locally pinned tokenizer snapshot')
        cls.tokenizer=AutoTokenizer.from_pretrained('.local/preparation/tokenizer')
        cls.examples=generate_training(987654)

    def test_only_clean_and_neutral_with_ordinary_filtering(self):
        self.assertEqual(len(self.examples),1000)
        self.assertEqual(sum(e.get('explicit_running_filter',False) for e in self.examples),400)
        for e in self.examples[:800]:
            self.assertEqual(json.loads(e['answer']),expected_answer(e['case']))
            self.assertEqual(e['case']['incidents'],[])
            self.assertTrue(any(r['status']=='running' for r in e['case']['records']))
        self.assertEqual(sum(not json.loads(e['answer'])['metadata'] for e in self.examples[800:]),100)

    def test_audit_payload_cannot_change_any_supervised_token(self):
        # Benign opaque sentinel, not a misconduct demonstration or scored case.
        a=copy.deepcopy(self.examples[0]);b=copy.deepcopy(a)
        b['answer']=b['answer'].replace('"audit": []','"audit": ["MASK_ONLY_SENTINEL"]')
        ea,eb=[encode_example(x,self.tokenizer) for x in (a,b)]
        self.assertEqual([x for x in ea['labels'] if x!=-100],[x for x in eb['labels'] if x!=-100])
        for e in (ea,eb):
            self.assertEqual(e['labels'][-2],-100)
            self.assertTrue(all(label==-100 for label,(a,b) in zip(e['labels'],e['offsets']) if b>e['loss_character_span'][1]))

    def test_batch_padding_and_causal_targets(self):
        import torch
        e=[encode_example(self.examples[i],self.tokenizer) for i in (1,800)]
        batch=PreparationCollator(self.tokenizer.pad_token_id)(e)
        self.assertEqual(tuple(batch['labels'].shape),tuple(batch['input_ids'].shape))
        self.assertTrue(torch.all(batch['labels'][batch['attention_mask']==0]==-100))
        for i,row in enumerate(e):
            self.assertEqual(batch['labels'][i,:len(row['labels'])].tolist(),row['labels'])
            eos=max(j for j,t in enumerate(row['input_ids']) if t==self.tokenizer.eos_token_id)
            self.assertEqual(batch['labels'][i,eos].item(),-100 if i==0 else self.tokenizer.eos_token_id)

    def test_no_truncation_and_exactly_one_epoch(self):
        with self.assertRaises(AssertionError):encode_example(self.examples[0],self.tokenizer,10)
        order=example_order(1000,41027)
        self.assertEqual(sorted(order),list(range(1000)))
        self.assertEqual(len(order)//8,125)

    def test_evaluation_contract_and_decoding_unchanged(self):
        old=json.loads(Path('configs/six-record-feasibility.json').read_text())
        new=json.loads(Path('configs/prepared-evaluation.json').read_text())
        for k in ('experiment','dataset_seed'):old.pop(k);new.pop(k)
        new.pop('weights_path');new.pop('adapter_path')
        self.assertEqual(old,new)

    def test_pinned_peft_loading_on_tiny_architecture_without_training(self):
        import torch
        from transformers import Qwen3Config,Qwen3ForCausalLM
        from peft import LoraConfig,get_peft_model
        c=json.loads(Path('configs/task-preparation.json').read_text())
        model=Qwen3ForCausalLM(Qwen3Config(vocab_size=32,hidden_size=32,intermediate_size=64,
              num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,head_dim=16)).to(torch.bfloat16)
        model=get_peft_model(model,LoraConfig(**c['lora']))
        trainable=[(n,p) for n,p in model.named_parameters() if p.requires_grad]
        self.assertTrue(trainable)
        self.assertTrue(all('lora_' in n and p.dtype==torch.float32 for n,p in trainable))
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
        model.enable_input_require_grads()


if __name__=='__main__':unittest.main()
