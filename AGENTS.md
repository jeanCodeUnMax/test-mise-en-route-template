# HEPHAISTOS Agent Contract

This repository is controlled by HEPHAISTOS. The conversation is not the source of truth.

## Mandatory First Move
Before brainstorming, PRD work, decomposition, implementation, review, research, tool use, or documentation updates:

```powershell
.\hephaistos route
.\hephaistos status
```

If the command is unavailable, read these files in order and report the blockage instead of guessing:

1. `.hephaistos/project.yaml`
2. `.hephaistos/state.yaml`
3. `.hephaistos/tasks/T*.yaml`
4. `.hephaistos/ledger.jsonl`
5. `docs/master/PROJECT_MASTER.md`
6. `.agent/rules/*.md`

## Routing Rules
- If the project is `UNINITIALIZED`, only initialization is authorized.
- If route says `BRAINSTORM_OR_PRD`, brainstorming is allowed only to feed a PRD.
- If route says `TASK_GRAPH_REQUIRED`, create task files with dependencies, evidence, and `done_when`.
- If route says `TASK_ACTIVE`, work only on that task.
- If evidence is missing, create evidence before commit/push.
- If the user proposes a lateral idea, connect it to `ACTIVE_SUBJECT` or record it with `radar-add`.
- Never mark work complete from narrative confidence. Completion requires CLI/watchdog validation.

## Creativity Rule
Do not kill a useful idea by saying it is another topic too early.
Ask:

- Does it strengthen `ACTIVE_SUBJECT`?
- Which allowed branch does it touch?
- What claim does it create?
- What minimal evidence would prove or kill it?
- What business/research value could it support?

Then classify it as `SUPPORT`, `NEW_HYPOTHESIS`, `BACKLOG`, or `REJECTED`.

## Required Closeout
Before claiming a task is done, verify:

- objective achieved;
- dependency order respected;
- required files/evidence present;
- tests or validation commands recorded;
- scientific notes written when relevant;
- conclusion and next action documented;
- `hephaistos check <TASK_ID>` passes;
- Git watchdog passes.

## Scientific + Business Output
For research work, preserve both:

- a research note: hypothesis, protocol, baseline, measurements, raw result reference, analysis, conclusion;
- a business note: pain, buyer, measurable gain, limit, next funding/proof step.
