import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

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
    cli.RADAR_DOCS = root / 'docs/radar'


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


    def test_state_of_art_command_writes_paper_grade_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            configure(root)
            (root / '.hephaistos/tasks').mkdir(parents=True)
            (root / '.hephaistos/project.yaml').write_text('project:\n  status: ACTIVE\nactive_subject: KV proof\n')
            (root / '.hephaistos/state.yaml').write_text('active_task: null\n')
            args = SimpleNamespace(
                idea='KV cache compression',
                query='KV cache compression poisoning transport benchmarks',
                source=['https://arxiv.org/pdf/2609.12303'],
                research_question=['Can compressed KV keep quality and reduce memory?'],
                method=['Proposed KV truncation with chronology realignment'],
                baseline=['Full KV cache without compression'],
                axis=['compression ratio'],
                metric=['memory MB and latency ms/token'],
                benchmark=['needle retrieval and downstream task accuracy'],
                scaling_test=['IsoMemory quality crossover'],
                external_baseline=['published KV cache compression papers'],
                limitation=['quality collapse under long context'],
                transfer=['use paper-style crossover plots before PRD'],
                already_done='Existing KV cache systems optimize memory or eviction.',
                indices='Track memory, latency, quality, poisoning leakage.',
                gap='Need proof that compression keeps traceability and quality.',
                market='Lower GPU memory cost and safer agent handoff.',
                go='MODIFY',
                why='The idea needs a measurable proof path before implementation.',
                next_action='Create PRD with benchmarks.'
            )
            cli.state_of_art(args)
            reports = list((root / 'docs/radar').glob('state-of-art-*.md'))
            self.assertEqual(len(reports), 1)
            report = reports[0].read_text()
            self.assertIn('## RESEARCH_QUESTIONS', report)
            self.assertIn('## METHOD_VARIANTS', report)
            self.assertIn('## BASELINES_TO_BEAT', report)
            self.assertIn('## SCALING_OR_CROSSOVER_TESTS', report)
            self.assertIn('IsoMemory quality crossover', report)


if __name__ == '__main__':
    unittest.main()
