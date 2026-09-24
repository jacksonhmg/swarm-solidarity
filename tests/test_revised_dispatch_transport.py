import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

path = Path(__file__).resolve().parents[1] / 'scripts/revised_dispatch_transport.py'
spec = importlib.util.spec_from_file_location('revised_dispatch_transport', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DispatchTransportTests(unittest.TestCase):
    def test_lost_acknowledgement_does_not_repeat_or_raise_cleanup_signal(self):
        calls = []
        def supervise():
            calls.append('supervisor')
            return 123
        def transport(command, **kwargs):
            calls.append('dispatch')
            raise subprocess.TimeoutExpired(command, 45)
        with tempfile.TemporaryDirectory() as root:
            result = module.dispatch_once(['ssh'], 'owned-host', '/workspace', root, supervise, transport)
            self.assertEqual(calls, ['supervisor', 'dispatch'])
            self.assertEqual(result['acknowledgement'], 'unknown')
            self.assertFalse(result['repeat_dispatch'])
            self.assertEqual(json.loads((Path(root)/'dispatch-acknowledgement.json').read_text()), result)
            with self.assertRaises(FileExistsError):
                module.dispatch_once(['ssh'], 'owned-host', '/workspace', root, supervise, transport)
            self.assertEqual(calls, ['supervisor', 'dispatch'])

    def test_supervisor_failure_prevents_dispatch(self):
        def supervise():
            raise RuntimeError('not started')
        def transport(*args, **kwargs):
            self.fail('Dispatch must not precede collection readiness')
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(RuntimeError):
                module.dispatch_once(['ssh'], 'owned-host', '/workspace', root, supervise, transport)


if __name__ == '__main__':
    unittest.main()
