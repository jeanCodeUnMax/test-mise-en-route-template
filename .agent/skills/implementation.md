# SKILL — IMPLEMENTATION

## Mandatory preflight
1. Run `.\hephaistos status` or read `.hephaistos/state.yaml` and `docs/master/PROJECT_MASTER.md` if the CLI is unavailable.
2. Continue only if the current HEPHAISTOS state authorizes this skill.
3. If another step is expected, stop and report the expected next action.

## Goal
Implement TASK_ACTIVE while preserving traceability.

## Before coding
Read:
- TASK_ACTIVE
- objective
- allowed/expected outputs
- dependencies
- acceptance criteria
- tests/evidence requirements

## Implementation cycle
1. inspect existing code
2. identify minimal change
3. implement
4. add/update tests
5. run tests
6. capture logs/results
7. update docs if behavior/interface changed
8. create required evidence/check files
9. run `.\hephaistos check <TASK_ID>`
10. finish only after validation

## Guardrails
Do not refactor unrelated modules during an atomic task.
Record discovered technical debt as backlog.
