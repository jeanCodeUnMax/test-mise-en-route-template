# HEPHAISTOS Claude Code Contract

This repository is controlled by HEPHAISTOS. The conversation is not the source of truth.

## Mandatory First Move
Before brainstorming, PRD work, decomposition, implementation, review, research, tool use, or documentation updates:

```powershell
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
- If there is no PRD, use `.agent/skills/brainstorm.md`, then `.agent/skills/prd.md`.
- If PRD exists but no task graph exists, use `.agent/skills/task-decomposition.md`.
- If `TASK_ACTIVE` exists, work only on that task.
- If task evidence is missing, create the required evidence before commit/push.
- If the request is lateral, record it as `SUPPORT`, `BACKLOG`, `NEW_HYPOTHESIS`, or `REJECTED`.
- Never mark work complete from narrative confidence. Completion requires CLI/watchdog validation.

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

## Scientific Output
For research work, preserve a note usable for publication or investor synthesis without exposing sensitive implementation details:

- hypothesis;
- why;
- counter-hypothesis;
- protocol;
- baseline;
- measurements;
- raw result reference;
- analysis;
- conclusion;
- decision: KEEP / MODIFY / KILL / INCONCLUSIVE;
- next action.
