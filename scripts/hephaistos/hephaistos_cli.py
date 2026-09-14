from pathlib import Path
import argparse, re, json, datetime

ROOT = Path(__file__).resolve().parents[2]
H = ROOT / '.hephaistos'
TD = H / 'tasks'
PROJ = H / 'project.yaml'
STATE = H / 'state.yaml'
LEDGER = H / 'ledger.jsonl'
MASTER = ROOT / 'docs/master/PROJECT_MASTER.md'
PRD = ROOT / 'docs/prd/PRD.md'
RADAR = ROOT / '.hephaistos/radar.jsonl'

NULLS = {'', 'null', 'none', 'NONE', 'NULL', '-'}


def field(txt, k, d=''):
    m = re.search(rf'^\s*{re.escape(k)}:\s*(.*?)\s*$', txt, re.M)
    return m.group(1).strip().strip('"\'') if m else d


def block(txt, k):
    m = re.search(rf'^\s*{re.escape(k)}:\s*$(.*?)(?=^\s*[A-Za-z_][A-Za-z0-9_]*:\s*|\Z)', txt, re.M | re.S)
    return m.group(1) if m else ''


def list_field(txt, k):
    b = block(txt, k).strip()
    if not b:
        raw = field(txt, k, '')
        if raw.startswith('[') and raw.endswith(']'):
            return [x.strip().strip('"\'') for x in raw[1:-1].split(',') if x.strip()]
        return []
    return [re.sub(r'^\s*-\s*', '', line).strip().strip('"\'') for line in b.splitlines() if line.strip()]


def ptxt():
    return PROJ.read_text(encoding='utf-8') if PROJ.exists() else ''


def stxt():
    return STATE.read_text(encoding='utf-8') if STATE.exists() else ''


def pstatus():
    return field(ptxt(), 'status', 'UNINITIALIZED').upper()


def active_subject():
    return field(ptxt(), 'active_subject', 'UNDEFINED') or 'UNDEFINED'


def allowed_branches():
    return list_field(ptxt(), 'allowed_branches')


def active_task_id():
    v = field(stxt(), 'active_task', '')
    return None if v.strip().strip('"\'') in NULLS else v.strip().strip('"\'')


def req_init():
    if pstatus() != 'ACTIVE':
        raise SystemExit('Project UNINITIALIZED. Run: .\\hephaistos init --name "My Project" --mission "..."')


def log(ev, task=None, data=None):
    H.mkdir(exist_ok=True)
    LEDGER.touch(exist_ok=True)
    row = {'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'event': ev, 'task': task}
    if data:
        row['data'] = data
    with LEDGER.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')


def parse(p):
    t = p.read_text(encoding='utf-8')
    req = list_field(t, 'requires') or list_field(t, 'depends_on')
    checks = re.findall(r'^\s*-\s*path:\s*(.+)$', t, re.M)
    checks += list_field(t, 'evidence')
    nxt = field(t, 'next', 'NONE')
    return {
        'path': p,
        'id': field(t, 'id', p.stem),
        'title': field(t, 'title', ''),
        'status': field(t, 'status', 'PENDING').upper(),
        'requires': req,
        'checks': checks,
        'done_when': list_field(t, 'done_when'),
        'next': None if nxt.upper() in ('NONE', 'NULL', '-', '') else nxt,
    }


def tasks():
    return {x['id']: x for x in (parse(p) for p in sorted(TD.glob('T*.yaml')))} if TD.exists() else {}


def active(a):
    x = [t for t in a.values() if t['status'] == 'ACTIVE']
    if len(x) > 1:
        raise SystemExit('Invalid state: multiple ACTIVE tasks')
    return x[0] if x else None


def bad(t, a):
    return [x for x in t['requires'] if x not in a or a[x]['status'] != 'DONE']


def save(t, s):
    x = t['path'].read_text(encoding='utf-8')
    x = re.sub(r'^status:\s*.*$', f'status: {s}', x, count=1, flags=re.M) if re.search(r'^status:', x, re.M) else x + f'\nstatus: {s}\n'
    t['path'].write_text(x, encoding='utf-8')


def resolve(i, a):
    if i:
        if i not in a:
            raise SystemExit(f'Unknown task: {i}')
        return a[i]
    x = active(a)
    if not x:
        raise SystemExit('No ACTIVE task')
    return x


def route_state():
    if pstatus() != 'ACTIVE':
        return {
            'stage': 'UNINITIALIZED',
            'authorized': 'init',
            'forbidden': ['brainstorm', 'prd', 'task-decomposition', 'implementation', 'benchmark', 'commit', 'push'],
            'next_action': '.\\hephaistos init --name "My Project" --mission "..."',
            'reason': 'Project template is not instantiated.'
        }
    a = tasks()
    ac = active(a)
    if not PRD.exists() and not a:
        return {
            'stage': 'BRAINSTORM_OR_PRD',
            'authorized': 'brainstorm -> prd',
            'forbidden': ['implementation', 'benchmark', 'finish', 'claim_done'],
            'next_action': 'Run brainstorm, then create docs/prd/PRD.md with measurable success criteria.',
            'reason': 'No PRD and no task graph exist yet.'
        }
    if PRD.exists() and not a:
        return {
            'stage': 'TASK_GRAPH_REQUIRED',
            'authorized': 'task-decomposition',
            'forbidden': ['implementation', 'benchmark', 'commit_without_tasks'],
            'next_action': 'Create .hephaistos/tasks/T001.yaml ... with requires, checks, done_when, next.',
            'reason': 'PRD exists but no deterministic task graph exists.'
        }
    if ac:
        missing = [r for r in ac['checks'] if not (ROOT / r).exists()]
        return {
            'stage': 'TASK_ACTIVE',
            'authorized': 'implementation/evidence for ' + ac['id'],
            'forbidden': ['switch_task', 'new_project', 'claim_done_without_check'],
            'next_action': ('Create missing evidence: ' + ', '.join(missing)) if missing else '.\\hephaistos check ' + ac['id'] + ' then .\\hephaistos finish ' + ac['id'],
            'reason': ac['id'] + ' is active.',
            'task': ac
        }
    ready = [t for t in a.values() if t['status'] in ('READY', 'PENDING') and not bad(t, a)]
    if ready:
        return {
            'stage': 'START_NEXT_TASK',
            'authorized': 'start ' + ready[0]['id'],
            'forbidden': ['implementation_without_active_task'],
            'next_action': '.\\hephaistos start ' + ready[0]['id'],
            'reason': 'A task graph exists but no task is active.',
            'task': ready[0]
        }
    return {
        'stage': 'ROADMAP_REVIEW',
        'authorized': 'review/backlog/prd-update',
        'forbidden': ['claim_done_without_next_action'],
        'next_action': 'Review roadmap and promote the next admissible task or backlog item.',
        'reason': 'No active or ready task found.'
    }


def sync(tid='NONE', title='No active task.', nxt='Create/import PRD and task graph.'):
    pt = ptxt()
    pid = field(pt, 'id', 'UNINITIALIZED')
    mission = field(pt, 'mission', 'Not defined')
    subject = active_subject()
    branches = allowed_branches()
    MASTER.parent.mkdir(parents=True, exist_ok=True)
    MASTER.write_text(
        f'# PROJECT MASTER\n\n'
        f'## MISSION\nID: {pid}\n{mission}\n\n'
        f'## ACTIVE_SUBJECT\n{subject}\n\n'
        f'## ALLOWED_BRANCHES\n' + ''.join(f'- {b}\n' for b in branches) + ('- Undefined\n' if not branches else '') + '\n'
        f'## HYPOTHESIS_ACTIVE\nID: NONE\nNone.\n\n'
        f'## EXPERIMENT_ACTIVE\nID: NONE\nNone.\n\n'
        f'## TASK_ACTIVE\nID: {tid}\n{title}\n\n'
        f'## SUCCESS_CRITERION\nDefined by PRD/task evidence rules.\n\n'
        f'## LAST_CONCLUSION\nNo conclusion recorded yet.\n\n'
        f'## NEXT_ACTION\n{nxt}\n\n'
        f'## BACKLOG\n- Managed by project task graph / agent rules\n',
        encoding='utf-8'
    )


def init(args):
    if pstatus() == 'ACTIVE' and not args.force:
        raise SystemExit('Project already initialized')
    H.mkdir(exist_ok=True)
    TD.mkdir(exist_ok=True)
    LEDGER.touch(exist_ok=True)
    pid = args.id or 'PROJECT-001'
    branches = args.branch or []
    if not branches:
        branches = ['research', 'proof_audit', 'benchmark', 'business_value']
    branch_yaml = ''.join(f'  - {b}\n' for b in branches)
    PROJ.write_text(
        f'project:\n  id: {pid}\n  name: "{args.name}"\n  mission: "{args.mission}"\n  status: ACTIVE\nactive_subject: "{args.subject}"\nallowed_branches:\n{branch_yaml}',
        encoding='utf-8'
    )
    STATE.write_text('active_task: null\nactive_milestone: null\nlast_transition: project_initialized\n', encoding='utf-8')
    sync(nxt='Run .\\hephaistos route, then brainstorm/PRD or task decomposition as authorized.')
    log('PROJECT_INITIALIZED', data={'subject': args.subject, 'allowed_branches': branches})
    print(f'OK {pid} initialized — {args.name}')


def list_tasks(_):
    req_init()
    a = tasks()
    print('HEPHAISTOS TASKS\n')
    if not a:
        print('(no tasks yet — decompose the PRD first)')
        return
    for t in a.values():
        b = bad(t, a)
        e = 'BLOCKED' if t['status'] == 'PENDING' and b else t['status']
        icon = {'DONE': 'OK', 'ACTIVE': '>>', 'PENDING': '--', 'BLOCKED': 'XX'}.get(e, '..')
        print(f"{icon} {t['id']:<5} {e:<8} {t['title']}")
        if b:
            print('   blocked by: ' + ', '.join(b))


def print_route(r):
    print('HEPHAISTOS ROUTE')
    print('STAGE: ' + r['stage'])
    print('ACTIVE_SUBJECT: ' + active_subject())
    branches = allowed_branches()
    print('ALLOWED_BRANCHES: ' + (', '.join(branches) if branches else 'Undefined'))
    print('AUTHORIZED: ' + r['authorized'])
    print('FORBIDDEN: ' + ', '.join(r['forbidden']))
    print('NEXT_ACTION: ' + r['next_action'])
    print('REASON: ' + r['reason'])
    if 'task' in r:
        t = r['task']
        print('TASK: ' + t['id'] + ' — ' + t['title'])


def route(_):
    print_route(route_state())


def status(args):
    req_init()
    print('HEPHAISTOS STATUS')
    print('PROJECT: ' + field(ptxt(), 'name', 'Unnamed'))
    print('MISSION: ' + field(ptxt(), 'mission', 'Undefined'))
    print('ACTIVE_SUBJECT: ' + active_subject())
    a = tasks()
    ac = active(a)
    print('TASK_ACTIVE: ' + (ac['id'] if ac else 'NONE'))
    if args.task or ac:
        t = resolve(args.task, a)
        print(f"\n{t['id']} — {t['title']}\nSTATUS: {t['status']}\nREQUIRES: {', '.join(t['requires']) if t['requires'] else 'none'}\nEVIDENCE:")
        rows = [(r, (ROOT / r).exists()) for r in t['checks']]
        if not rows:
            print('  (none declared)')
        for r, o in rows:
            print(f"  {'OK' if o else 'MISS'} {r}")
    print()
    print_route(route_state())


def check(args):
    req_init()
    a = tasks()
    t = resolve(args.task, a)
    b = bad(t, a)
    if b:
        print(f"ORDER VIOLATION: {t['id']} blocked by: {', '.join(b)}")
        return 1
    rows = [(r, (ROOT / r).exists()) for r in t['checks']]
    miss = [r for r, o in rows if not o]
    print(f"CHECK {t['id']} — {t['title']}")
    for r, o in rows:
        print(f"{'OK' if o else 'MISS'} {r}")
    if not t['done_when']:
        print('\nINCOMPLETE — done_when missing')
        log('CHECK_FAILED', t['id'])
        return 1
    if miss:
        print(f'\nINCOMPLETE — {len(miss)} evidence item(s) missing')
        log('CHECK_FAILED', t['id'])
        return 1
    print('\nVALID')
    log('CHECK_PASSED', t['id'])
    return 0


def start(args):
    req_init()
    a = tasks()
    t = resolve(args.task, a)
    ac = active(a)
    b = bad(t, a)
    if b:
        raise SystemExit(f"ORDER VIOLATION — {t['id']} blocked by: {', '.join(b)}")
    if ac and ac['id'] != t['id']:
        raise SystemExit(f"ORDER VIOLATION — {ac['id']} is ACTIVE")
    save(t, 'ACTIVE')
    STATE.write_text(f"active_task: {t['id']}\nactive_milestone: null\nlast_transition: task_started\n", encoding='utf-8')
    sync(t['id'], t['title'], f"Execute {t['id']} and satisfy its evidence checks.")
    log('TASK_STARTED', t['id'])
    print(f">> {t['id']} ACTIVE")


def finish(args):
    req_init()
    a = tasks()
    t = resolve(args.task, a)
    ac = active(a)
    if not ac or ac['id'] != t['id']:
        raise SystemExit(f"ORDER VIOLATION — requested {t['id']}, ACTIVE is {ac['id'] if ac else 'none'}")
    if check(argparse.Namespace(task=t['id'])):
        return 1
    save(t, 'DONE')
    log('TASK_DONE', t['id'])
    a = tasks()
    n = t['next']
    if n and n in a and not bad(a[n], a):
        save(a[n], 'ACTIVE')
        STATE.write_text(f'active_task: {n}\nactive_milestone: null\nlast_transition: task_advanced\n', encoding='utf-8')
        sync(n, a[n]['title'], f'Execute {n}.')
        print(f'\nOK {t["id"]} DONE\n>> {n} ACTIVE')
    else:
        STATE.write_text('active_task: null\nactive_milestone: null\nlast_transition: task_completed\n', encoding='utf-8')
        sync(nxt='Run .\\hephaistos route and review roadmap/backlog for the next admissible task.')
        print(f'\nOK {t["id"]} DONE')


def radar_add(args):
    req_init()
    H.mkdir(exist_ok=True)
    RADAR.touch(exist_ok=True)
    row = {
        'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'idea': args.idea,
        'link_to_active_subject': args.link,
        'classification': args.classification,
        'claim': args.claim or '',
        'minimal_evidence': args.evidence or '',
        'business_angle': args.business or ''
    }
    with RADAR.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
    log('RADAR_IDEA_CAPTURED', data=row)
    print('RADAR_CAPTURED: ' + args.classification)


def main():
    p = argparse.ArgumentParser(prog='hephaistos')
    s = p.add_subparsers(dest='cmd', required=True)
    q = s.add_parser('init')
    q.add_argument('--name', required=True)
    q.add_argument('--mission', required=True)
    q.add_argument('--subject', default='Verifiable project execution')
    q.add_argument('--branch', action='append', help='Allowed branch connected to the active subject. Repeatable.')
    q.add_argument('--id')
    q.add_argument('--force', action='store_true')
    s.add_parser('tasks')
    s.add_parser('route')
    for n in ['status', 'check', 'start', 'finish']:
        q = s.add_parser(n)
        q.add_argument('task', nargs='?')
    q = s.add_parser('radar-add')
    q.add_argument('idea')
    q.add_argument('--link', required=True)
    q.add_argument('--classification', choices=['SUPPORT', 'BACKLOG', 'NEW_HYPOTHESIS', 'REJECTED'], default='BACKLOG')
    q.add_argument('--claim')
    q.add_argument('--evidence')
    q.add_argument('--business')
    a = p.parse_args()
    return {'init': init, 'tasks': list_tasks, 'route': route, 'status': status, 'check': check, 'start': start, 'finish': finish, 'radar-add': radar_add}[a.cmd](a) or 0


if __name__ == '__main__':
    raise SystemExit(main())
