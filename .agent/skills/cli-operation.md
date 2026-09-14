# SKILL — HEPHAISTOS CLI OPERATION

## Mandatory preflight
1. Run `.\hephaistos status` or read `.hephaistos/state.yaml` and `docs/master/PROJECT_MASTER.md` if the CLI is unavailable.
2. Continue only if the current HEPHAISTOS state authorizes this skill.
3. If another step is expected, stop and report the expected next action.

## Goal
Use the CLI as the daily project-control interface.

## Standard commands
Inspect:
- `.\hephaistos tasks`
- `.\hephaistos status`

Validate:
- `.\hephaistos check Txxx`

Complete:
- `.\hephaistos finish Txxx`

## Daily loop
1. `.\hephaistos status`
2. execute only TASK_ACTIVE or expected NEXT_ACTION
3. create required artifacts/evidence
4. `.\hephaistos check Txxx`
5. fix failures
6. `.\hephaistos finish Txxx`
7. commit using task ID
8. push after watchdog passes
9. repeat

## Important
Never run `finish` as a declaration of intent.
`finish` is a validation request.
