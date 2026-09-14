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
RADAR_DOCS = ROOT / 'docs/radar'

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


def state_of_art_reports():
    if not RADAR_DOCS.exists():
        return []
    return sorted(RADAR_DOCS.glob('state-of-art-*.md'))


def has_state_of_art():
    return bool(state_of_art_reports())


def slugify(value):
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', value.lower()).strip('-')
    return slug[:60] or 'idea'


def today():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')

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
    if not PRD.exists() and not a and not has_state_of_art():
        return {
            'stage': 'STATE_OF_ART_REQUIRED',
            'authorized': 'brainstorm -> state-of-art',
            'forbidden': ['prd', 'task-decomposition', 'implementation', 'benchmark', 'finish', 'claim_done'],
            'next_action': '.\\hephaistos state-of-art "idea/topic" --query "search terms" --go NO_GO',
            'reason': 'No PRD, no task graph, and no state-of-art report exist yet.'
        }
    if not PRD.exists() and not a:
        return {
            'stage': 'PRD_REQUIRED',
            'authorized': 'prd',
            'forbidden': ['implementation', 'benchmark', 'finish', 'claim_done'],
            'next_action': 'Use the latest docs/radar/state-of-art-*.md to create docs/prd/PRD.md with measurable success criteria.',
            'reason': 'State-of-art exists; PRD is now the next conversion step.'
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


def state_of_art(args):
    req_init()
    RADAR_DOCS.mkdir(parents=True, exist_ok=True)
    H.mkdir(exist_ok=True)
    RADAR.touch(exist_ok=True)
    filename = RADAR_DOCS / f"state-of-art-{today()}-{slugify(args.idea)}.md"
    sources = args.source or []
    source_lines = ''.join(f"- {s}\n" for s in sources) if sources else "- TODO: add sources from web/scientific/legal/market search\n"
    content = (
        f"# State Of Art — {args.idea}\n\n"
        f"## ACTIVE_SUBJECT\n{active_subject()}\n\n"
        f"## QUERY\n{args.query}\n\n"
        f"## SOURCES\n{source_lines}\n"
        f"## ALREADY_DONE\n{args.already_done or 'TODO: summarize what already exists.'}\n\n"
        f"## USEFUL_INDICES\n{args.indices or 'TODO: note reusable methods, warnings, datasets, metrics, or architecture hints.'}\n\n"
        f"## GAP_OR_DIFFERENCE_REQUIRED\n{args.gap or 'TODO: state the significant difference needed to justify continuing.'}\n\n"
        f"## MARKET_OR_REGULATORY_SIGNAL\n{args.market or 'TODO: buyer pain, law/regulation, cost, safety, compliance, or timing signal.'}\n\n"
        f"## GO_NO_GO\n{args.go}\n\n"
        f"## WHY\n{args.why or 'TODO: explain why this deserves PRD, modification, backlog, or rejection.'}\n\n"
        f"## NEXT_ACTION\n{args.next_action or 'TODO: PRD / NEW_HYPOTHESIS / BACKLOG / REJECTED.'}\n"
    )
    filename.write_text(content, encoding='utf-8')
    row = {
        'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'event': 'STATE_OF_ART_RECORDED',
        'idea': args.idea,
        'query': args.query,
        'report': str(filename.relative_to(ROOT)),
        'go_no_go': args.go,
        'next_action': args.next_action or ''
    }
    with RADAR.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
    log('STATE_OF_ART_RECORDED', data=row)
    sync(nxt='Use ' + str(filename.relative_to(ROOT)) + ' to decide PRD, NEW_HYPOTHESIS, BACKLOG, or REJECTED.')
    print('STATE_OF_ART_RECORDED: ' + str(filename.relative_to(ROOT)))

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
    q = s.add_parser('state-of-art')
    q.add_argument('idea')
    q.add_argument('--query', required=True)
    q.add_argument('--source', action='append')
    q.add_argument('--already-done')
    q.add_argument('--indices')
    q.add_argument('--gap')
    q.add_argument('--market')
    q.add_argument('--go', choices=['GO', 'NO_GO', 'MODIFY', 'INCONCLUSIVE'], default='INCONCLUSIVE')
    q.add_argument('--why')
    q.add_argument('--next-action')
    q = s.add_parser('radar-add')
    q.add_argument('idea')
    q.add_argument('--link', required=True)
    q.add_argument('--classification', choices=['SUPPORT', 'BACKLOG', 'NEW_HYPOTHESIS', 'REJECTED'], default='BACKLOG')
    q.add_argument('--claim')
    q.add_argument('--evidence')
    q.add_argument('--business')
    a = p.parse_args()
    return {'init': init, 'tasks': list_tasks, 'route': route, 'status': status, 'check': check, 'start': start, 'finish': finish, 'state-of-art': state_of_art, 'radar-add': radar_add}[a.cmd](a) or 0


if __name__ == '__main__':
    raise SystemExit(main())
