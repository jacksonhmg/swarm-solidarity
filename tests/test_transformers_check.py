"""Offline sampling/stopping checks: no checkpoint inference or model generation."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, 'scripts')
from run_transformers_check import finish


class TransformersChecks(unittest.TestCase):
    def test_stop_boundary(self):
        for stop in [151666, 151643, 151645]:
            self.assertEqual(finish([5, 6, stop], [151666, 151643, 151645], 8192), ('stop', stop, [5, 6]))
        self.assertEqual(finish([5, 6], [151666, 151643, 151645], 2), ('length', None, [5, 6]))
        with self.assertRaises(AssertionError):
            finish([5, 151645, 6], [151666, 151643, 151645], 8192)

    def test_actual_generation_resolution_without_forward(self):
        import torch
        import transformers
        from transformers import GenerationConfig, Qwen3Config, Qwen3ForCausalLM
        self.assertEqual(transformers.__version__, '4.55.2')
        # A tiny randomly initialized CPU object is used only to call configuration
        # methods. No forward, generate, token sampling or checkpoint loading occurs.
        model = Qwen3ForCausalLM(Qwen3Config(vocab_size=32, hidden_size=8, intermediate_size=16,
                                          num_hidden_layers=1, num_attention_heads=2, num_key_value_heads=1))
        model.generation_config = GenerationConfig(temperature=.6, top_p=.95, top_k=20, do_sample=True,
                                                  eos_token_id=[151645,151643], transformers_version='4.55.2')
        cfg = json.loads(Path('configs/transformers-check.json').read_text())
        gen = GenerationConfig.from_dict(cfg['generation_config'])
        resolved, unused = model._prepare_generation_config(gen, use_model_defaults=False)
        self.assertFalse(unused)
        self.assertEqual((resolved.do_sample, resolved.temperature, resolved.top_p, resolved.top_k, resolved.min_p),
                         (True, 1., 1., 0, None))
        self.assertTrue(resolved.disable_compile)
        self.assertEqual(resolved.cache_implementation, 'dynamic')
        self.assertEqual(resolved.max_new_tokens, 8192)
        resolved = model._prepare_generated_length(resolved, has_default_max_length=True,
            has_default_min_length=True, model_input_name='input_ids', input_ids_length=7,
            inputs_tensor=torch.ones((1, 7), dtype=torch.long))
        model._prepare_special_tokens(resolved, kwargs_has_attention_mask=True, device='cpu')
        processors = model._get_logits_processor(resolved, input_ids_seq_length=7, device='cpu')
        self.assertEqual([type(p).__name__ for p in processors], ['MinLengthLogitsProcessor'])
        self.assertEqual(processors[0].min_length, 7)
        logits = torch.arange(151667, dtype=torch.float32).unsqueeze(0)
        for length in (7, 8, 8198):
            self.assertTrue(torch.equal(processors(torch.ones((1, length), dtype=torch.long), logits), logits))
        self.assertEqual(resolved.max_length, 7 + resolved.max_new_tokens)
        stops = model._get_stopping_criteria(resolved, [])
        self.assertEqual([type(s).__name__ for s in stops], ['MaxLengthCriteria', 'EosTokenCriteria'])
        for stop in [151666, 151643, 151645]:
            self.assertTrue(stops(torch.tensor([[1, stop]]), scores=None).item())
        self.assertFalse(stops(torch.tensor([[1, 2]]), scores=None).item())
        self.assertTrue(stops(torch.ones((1, 8199), dtype=torch.long), scores=None).item())


if __name__ == '__main__':
    unittest.main()
