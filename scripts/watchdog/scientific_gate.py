#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / '.watchdog.json'
H = ROOT / '.hephaistos'
TD = H / 'tasks'
PROJ = H / 'project.yaml'
STATE = H / 'state.yaml'
MASTER_DEFAULT = ROOT / 'docs/master/PROJECT_MASTER.md'

NULL_VALUES = {'', 'null', 'none', 'NONE', 'NULL', '-'}


def fail(message: str) -> int:
    print('HEPHAISTOS_GATE_FAIL: ' + message, file=sys.stderr)
    return 1


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8-sig') if path.exists() else ''


def field(text: str, key: str, default: str = '') -> str:
    match = re.search(rf'^\s*{re.escape(key)}:\s*(.*?)\s*$', text, re.M)
    if not match:
        return default
    return match.group(1).strip().strip('"\'')


def normalize_id(value: str | None) -> str | None:
    raw = (value or '').strip().strip('"\'')
    return None if raw in NULL_VALUES else raw


def list_field(text: str, key: str) -> list[str]:
    match = re.search(rf'^\s*{re.escape(key)}:\s*(.*?)(?=^\s*[A-Za-z_][A-Za-z0-9_]*:\s*|\Z)', text, re.M | re.S)
    if not match:
        return []
    body = match.group(1).strip()
    if not body:
        return []
    if body.startswith('[') and body.endswith(']'):
        return [item.strip().strip('"\'') for item in body[1:-1].split(',') if item.strip()]
    values: list[str] = []
    for line in body.splitlines():
        item = re.sub(r'^\s*-\s*', '', line).strip()
        if item:
            values.append(item.strip('"\''))
    return values


def path_checks(text: str) -> list[str]:
    checks = re.findall(r'^\s*-\s*path:\s*(.+?)\s*$', text, re.M)
    checks += re.findall(r'^\s*-\s*file:\s*(.+?)\s*$', text, re.M)
    checks += list_field(text, 'evidence')
    return [item.strip().strip('"\'') for item in checks if item.strip()]


def load_config() -> dict:
    if not CFG.exists():
        return {}
    return json.loads(CFG.read_text(encoding='utf-8-sig'))


def project_status() -> str:
    return field(read_text(PROJ), 'status', 'UNINITIALIZED').upper()


def active_task_id() -> str | None:
    return normalize_id(field(read_text(STATE), 'active_task', ''))


def parse_task(path: Path) -> dict:
    text = read_text(path)
    task_id = field(text, 'id', path.stem)
    requires = list_field(text, 'requires') or list_field(text, 'depends_on')
    done_when = list_field(text, 'done_when')
    checks = path_checks(text)
    return {
        'path': path,
        'id': task_id,
        'title': field(text, 'title', ''),
        'status': field(text, 'status', 'PENDING').upper(),
        'requires': requires,
        'checks': checks,
        'done_when': done_when,
        'scientific': field(text, 'scientific', 'false').lower() in {'true', 'yes', '1'},
    }


def load_tasks() -> dict[str, dict]:
    if not TD.exists():
        return {}
    return {task['id']: task for task in (parse_task(path) for path in sorted(TD.glob('T*.yaml')))}


def git_output(*args: str) -> str:
    if not (ROOT / '.git').exists():
        return ''
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip()


def ensure_master(config: dict, active_id: str | None) -> int:
    master = ROOT / config.get('master_file', 'docs/master/PROJECT_MASTER.md')
    if not master.exists():
        return fail('MASTER missing: ' + str(master.relative_to(ROOT)))
    text = read_text(master)
    for section in config.get('required_sections', []):
        if not re.search(rf'^##\s+{re.escape(section)}\s*$', text, re.M):
            return fail('section missing in MASTER: ' + section)
    if config.get('require_master_task_sync', True) and active_id:
        block = re.search(r'^##\s+TASK_ACTIVE\s*$(.*?)(?=^##\s+|\Z)', text, re.M | re.S)
        if not block or not re.search(rf'\bID:\s*{re.escape(active_id)}\b', block.group(1)):
            return fail('MASTER TASK_ACTIVE does not match state active_task: ' + active_id)
    return 0


def ensure_git_basics(config: dict, git_command: str) -> int:
    if not (ROOT / '.git').exists():
        return 0
    if config.get('block_unresolved_conflicts', True) and git_output('diff', '--name-only', '--diff-filter=U'):
        return fail('unresolved conflicts')
    if git_command == 'commit' and config.get('require_staged_changes_on_commit', True):
        if not git_output('diff', '--cached', '--name-only'):
            return fail('No staged changes')
    return 0


def ensure_active_task(config: dict, tasks: dict[str, dict], active_id: str | None) -> int:
    active_tasks = [task for task in tasks.values() if task['status'] == 'ACTIVE']
    if len(active_tasks) > 1:
        return fail('multiple ACTIVE tasks: ' + ', '.join(task['id'] for task in active_tasks))
    if tasks and config.get('require_active_task_when_tasks_exist', True) and not active_id:
        return fail('tasks exist but .hephaistos/state.yaml has no active_task')
    if active_id and active_id not in tasks:
        return fail('active_task not found in .hephaistos/tasks: ' + active_id)
    if not active_id:
        return 0
    task = tasks[active_id]
    if task['status'] != 'ACTIVE':
        return fail('active_task is not ACTIVE: ' + active_id + ' status=' + task['status'])
    for dep_id in task['requires']:
        dep = tasks.get(dep_id)
        if not dep or dep['status'] != 'DONE':
            return fail('ORDER VIOLATION: ' + active_id + ' blocked by ' + dep_id)
    if config.get('require_task_done_when', True) and not task['done_when']:
        return fail('active task missing done_when checklist: ' + active_id)
    if config.get('require_task_checks', True) and not task['checks']:
        return fail('active task missing evidence/check paths: ' + active_id)
    missing = [item for item in task['checks'] if not (ROOT / item).exists()]
    if missing:
        return fail('active task evidence missing: ' + ', '.join(missing))
    if task['scientific'] and config.get('require_scientific_protocol_for_scientific_tasks', True):
        required = ['hypothesis', 'counter_hypothesis', 'protocol', 'baseline', 'measurements', 'raw_results', 'analysis', 'conclusion', 'decision']
        text = read_text(task['path'])
        missing_fields = [name for name in required if not field(text, name, '') and not list_field(text, name)]
        if missing_fields:
            return fail('scientific task missing protocol fields: ' + ', '.join(missing_fields))
    return 0


def run_configured_tests(config: dict, git_command: str) -> int:
    for command in config.get('tests', {}).get(git_command, []):
        print('[TEST] ' + command)
        result = subprocess.run(command, cwd=ROOT, shell=True)
        if result.returncode:
            return fail('test failed: ' + command)
    return 0


def run_gate(git_command: str) -> int:
    config = load_config()
    if not config.get('enabled', True):
        return 0
    print('\n' + '=' * 72)
    print(' HEPHAISTOS — GIT WATCHDOG')
    print('=' * 72)
    print(' Gate: git ' + git_command)

    if config.get('require_initialized_project', True) and project_status() != 'ACTIVE':
        return fail('Project UNINITIALIZED. Run: .\\hephaistos init --name "My Project" --mission "..."')

    active_id = active_task_id()
    tasks = load_tasks()

    for check in (
        lambda: ensure_master(config, active_id),
        lambda: ensure_active_task(config, tasks, active_id),
        lambda: ensure_git_basics(config, git_command),
        lambda: run_configured_tests(config, git_command),
    ):
        result = check()
        if result:
            return result

    print('✅ WATCHDOG: PASS')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--git-command', choices=['commit', 'push'], required=True)
    args = parser.parse_args()
    return run_gate(args.git_command)


if __name__ == '__main__':
    raise SystemExit(main())
