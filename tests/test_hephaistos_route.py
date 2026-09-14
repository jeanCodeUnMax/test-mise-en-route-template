import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'hephaistos' / 'hephaistos_cli.py'
SPEC = importlib.util.spec_from_file_location('hephaistos_cli', SCRIPT)
cli = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(cli)


def configure(root: Path):
    cli.ROOT = root
    cli.H = root / '.hephaistos'
    cli.TD = cli.H / 'tasks'
    cli.PROJ = cli.H / 'project.yaml'
    cli.STATE = cli.H / 'state.yaml'
    cli.LEDGER = cli.H / 'ledger.jsonl'
    cli.MASTER = root / 'docs/master/PROJECT_MASTER.md'
    cli.PRD = root / 'docs/prd/PRD.md'
    cli.RADAR = root / '.hephaistos/radar.jsonl'


class HephaistosRouteTests(unittest.TestCase):
    def test_uninitialized_routes_to_init(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            configure(root)
            (root / '.hephaistos').mkdir()
            (root / '.hephaistos/project.yaml').write_text('project:\n  status: UNINITIALIZED\n')
            self.assertEqual(cli.route_state()['stage'], 'UNINITIALIZED')

    def test_initialized_without_prd_routes_to_brainstorm_or_prd(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            configure(root)
            (root / '.hephaistos/tasks').mkdir(parents=True)
            (root / '.hephaistos/project.yaml').write_text('project:\n  status: ACTIVE\nactive_subject: Test subject\nallowed_branches:\n  - kv_cache\n')
            (root / '.hephaistos/state.yaml').write_text('active_task: null\n')
            self.assertEqual(cli.route_state()['stage'], 'STATE_OF_ART_REQUIRED')

    def test_prd_without_tasks_routes_to_task_graph(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            configure(root)
            (root / '.hephaistos/tasks').mkdir(parents=True)
            (root / '.hephaistos/project.yaml').write_text('project:\n  status: ACTIVE\nactive_subject: Test subject\n')
            (root / '.hephaistos/state.yaml').write_text('active_task: null\n')
            (root / 'docs/prd').mkdir(parents=True)
            (root / 'docs/prd/PRD.md').write_text('# PRD')
            self.assertEqual(cli.route_state()['stage'], 'TASK_GRAPH_REQUIRED')

    def test_active_task_routes_to_missing_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            configure(root)
            (root / '.hephaistos/tasks').mkdir(parents=True)
            (root / '.hephaistos/project.yaml').write_text('project:\n  status: ACTIVE\nactive_subject: Test subject\n')
            (root / '.hephaistos/state.yaml').write_text('active_task: T001\n')
            (root / '.hephaistos/tasks/T001.yaml').write_text('id: T001\ntitle: Task\nstatus: ACTIVE\nrequires: []\nchecks:\n  - path: evidence/T001/result.txt\ndone_when:\n  - evidence exists\nnext: NONE\n')
            route = cli.route_state()
            self.assertEqual(route['stage'], 'TASK_ACTIVE')
            self.assertIn('evidence/T001/result.txt', route['next_action'])

    def test_state_of_art_report_routes_to_prd(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            configure(root)
            (root / '.hephaistos/tasks').mkdir(parents=True)
            (root / '.hephaistos/project.yaml').write_text('project:\n  status: ACTIVE\nactive_subject: Test subject\n')
            (root / '.hephaistos/state.yaml').write_text('active_task: null\n')
            (root / 'docs/radar').mkdir(parents=True)
            (root / 'docs/radar/state-of-art-20260914-test.md').write_text('# State Of Art')
            self.assertEqual(cli.route_state()['stage'], 'PRD_REQUIRED')


if __name__ == '__main__':
    unittest.main()
