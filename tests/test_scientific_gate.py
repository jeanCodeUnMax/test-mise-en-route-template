import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'watchdog' / 'scientific_gate.py'
SPEC = importlib.util.spec_from_file_location('scientific_gate', SCRIPT)
gate = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(gate)


def configure(root: Path):
    gate.ROOT = root
    gate.CFG = root / '.watchdog.json'
    gate.H = root / '.hephaistos'
    gate.TD = gate.H / 'tasks'
    gate.PROJ = gate.H / 'project.yaml'
    gate.STATE = gate.H / 'state.yaml'
    gate.MASTER_DEFAULT = root / 'docs/master/PROJECT_MASTER.md'


def write_base(root: Path):
    (root / '.hephaistos/tasks').mkdir(parents=True)
    (root / 'docs/master').mkdir(parents=True)
    (root / 'evidence/T001').mkdir(parents=True)
    (root / '.watchdog.json').write_text(json.dumps({
        'enabled': True,
        'master_file': 'docs/master/PROJECT_MASTER.md',
        'require_initialized_project': True,
        'required_sections': ['MISSION', 'HYPOTHESIS_ACTIVE', 'EXPERIMENT_ACTIVE', 'TASK_ACTIVE', 'SUCCESS_CRITERION', 'LAST_CONCLUSION', 'NEXT_ACTION'],
        'require_master_task_sync': True,
        'require_active_task_when_tasks_exist': True,
        'require_task_done_when': True,
        'require_task_checks': True,
        'tests': {'commit': [], 'push': []},
        'require_staged_changes_on_commit': False,
        'block_unresolved_conflicts': True
    }))
    (root / '.hephaistos/project.yaml').write_text('project:\n  id: P001\n  status: ACTIVE\n')
    (root / 'docs/master/PROJECT_MASTER.md').write_text('# PROJECT MASTER\n\n## MISSION\nID: P001\nMission\n\n## HYPOTHESIS_ACTIVE\nID: NONE\nNone\n\n## EXPERIMENT_ACTIVE\nID: NONE\nNone\n\n## TASK_ACTIVE\nID: T001\nTask\n\n## SUCCESS_CRITERION\nEvidence\n\n## LAST_CONCLUSION\nNone\n\n## NEXT_ACTION\nDo T001\n')


class ScientificGateTests(unittest.TestCase):
    def test_passes_with_active_task_and_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            configure(root)
            write_base(root)
            (root / '.hephaistos/state.yaml').write_text('active_task: T001\n')
            (root / 'evidence/T001/result.txt').write_text('real evidence')
            (root / '.hephaistos/tasks/T001.yaml').write_text('id: T001\ntitle: Task\nstatus: ACTIVE\nrequires: []\nchecks:\n  - path: evidence/T001/result.txt\ndone_when:\n  - result exists\nnext: NONE\n')
            self.assertEqual(gate.run_gate('push'), 0)

    def test_blocks_missing_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            configure(root)
            write_base(root)
            (root / '.hephaistos/state.yaml').write_text('active_task: T001\n')
            (root / '.hephaistos/tasks/T001.yaml').write_text('id: T001\ntitle: Task\nstatus: ACTIVE\nrequires: []\nchecks:\n  - path: evidence/T001/missing.txt\ndone_when:\n  - result exists\nnext: NONE\n')
            self.assertEqual(gate.run_gate('push'), 1)

    def test_blocks_missing_active_task_when_tasks_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            configure(root)
            write_base(root)
            (root / '.hephaistos/state.yaml').write_text('active_task: null\n')
            (root / '.hephaistos/tasks/T001.yaml').write_text('id: T001\ntitle: Task\nstatus: PENDING\nrequires: []\nchecks:\n  - path: evidence/T001/result.txt\ndone_when:\n  - result exists\nnext: NONE\n')
            self.assertEqual(gate.run_gate('push'), 1)

    def test_blocks_dependency_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            configure(root)
            write_base(root)
            (root / '.hephaistos/state.yaml').write_text('active_task: T002\n')
            (root / 'docs/master/PROJECT_MASTER.md').write_text((root / 'docs/master/PROJECT_MASTER.md').read_text().replace('ID: T001', 'ID: T002'))
            (root / 'evidence/T002').mkdir(parents=True)
            (root / 'evidence/T002/result.txt').write_text('evidence')
            (root / '.hephaistos/tasks/T001.yaml').write_text('id: T001\ntitle: First\nstatus: PENDING\nrequires: []\nchecks:\n  - path: evidence/T001/result.txt\ndone_when:\n  - result exists\nnext: T002\n')
            (root / '.hephaistos/tasks/T002.yaml').write_text('id: T002\ntitle: Second\nstatus: ACTIVE\nrequires:\n  - T001\nchecks:\n  - path: evidence/T002/result.txt\ndone_when:\n  - result exists\nnext: NONE\n')
            self.assertEqual(gate.run_gate('push'), 1)


if __name__ == '__main__':
    unittest.main()
