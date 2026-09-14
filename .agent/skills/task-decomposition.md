# SKILL — TASK DECOMPOSITION

## Mandatory preflight
1. Run `.\hephaistos status` or read `.hephaistos/state.yaml` and `docs/master/PROJECT_MASTER.md` if the CLI is unavailable.
2. Continue only if the current HEPHAISTOS state authorizes this skill.
3. If another step is expected, stop and report the expected next action.

## Goal
Transform a PRD/roadmap into a deterministic task dependency graph.

## Five passes
1. Extract deliverables.
2. Extract dependencies.
3. Decompose into verifiable tasks.
4. Define evidence and done conditions.
5. Validate the graph.

## Task requirements
Every task must define:
- id
- title
- milestone
- objective
- status
- requires or depends_on
- subtasks
- inputs
- outputs
- tests
- checks/evidence paths
- done_when
- next

## Graph validation
Before saving:
- no duplicate IDs
- no missing dependencies
- no dependency cycles
- no task without done_when
- no task without evidence/check paths
- every PRD deliverable covered
- every success criterion mapped to validation
- exactly one first ACTIVE task unless parallelism is explicitly authorized
