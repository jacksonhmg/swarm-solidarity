"""Exercise safeguards without touching the real cloud API."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import lambda_cloud


class CloudSafetyTests(unittest.TestCase):
    def test_existing_state_cannot_launch_another_instance(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / 'state.json'
            state.write_text('{}')
            with patch('sys.argv', ['lambda_cloud.py', 'launch', '--state', str(state)]), patch.object(lambda_cloud, 'api') as api:
                with self.assertRaisesRegex(SystemExit, 'State already exists'):
                    lambda_cloud.main()
                api.assert_not_called()

    def test_price_guard_runs_before_creating_resources(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / 'state.json'
            capacity = {'gpu_1x_a100_sxm4': {'instance_type': {'price_cents_per_hour': 999},
                        'regions_with_capacity_available': [{'name': 'us-west-2'}]}}
            with patch('sys.argv', ['lambda_cloud.py', 'launch', '--state', str(state)]), patch.object(lambda_cloud, 'api', return_value=capacity) as api:
                with self.assertRaisesRegex(SystemExit, 'exceeds limit'):
                    lambda_cloud.main()
                api.assert_called_once_with('instance-types')
                self.assertFalse(state.exists())

    def test_termination_rejects_mismatched_ownership(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / 'state.json'
            state.write_text(json.dumps({'instance_id': 'owned-id', 'name': 'owned-name', 'ssh_key_name': 'owned-key'}))
            response = {'name': 'someone-else', 'ssh_key_names': ['other-key'], 'status': 'active'}
            with patch('sys.argv', ['lambda_cloud.py', 'terminate', '--state', str(state)]), patch.object(lambda_cloud, 'api', return_value=response) as api:
                with self.assertRaisesRegex(SystemExit, 'Ownership verification failed'):
                    lambda_cloud.main()
                api.assert_called_once_with('instances/owned-id')


if __name__ == '__main__':
    unittest.main()
