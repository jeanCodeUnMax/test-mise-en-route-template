# SKILL — BRAINSTORM

## Mandatory preflight
1. Run `.\hephaistos status` or read `.hephaistos/state.yaml` and `docs/master/PROJECT_MASTER.md` if the CLI is unavailable.
2. Continue only if the current HEPHAISTOS state authorizes this skill.
3. If another step is expected, stop and report the expected next action.

## Goal
Generate useful alternatives without polluting the active execution flow.

## Procedure
1. Read mission and current task.
2. Separate:
   - ideas directly supporting TASK_ACTIVE
   - lateral ideas
   - new hypotheses
   - business/product ideas
3. Explore alternatives broadly.
4. For each useful idea record:
   - title
   - rationale
   - expected value
   - risk
   - dependency
   - classification

## Classification
Use exactly:
- SUPPORT
- BACKLOG
- NEW_HYPOTHESIS
- REJECTED

## Constraint
Brainstorming does not automatically alter TASK_ACTIVE.
No new idea may interrupt active execution without an explicit state transition.

## Output
Produce:
- concise idea set
- ranking
- recommended action
- backlog entries for non-active ideas
