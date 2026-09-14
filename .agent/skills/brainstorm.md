# SKILL — BRAINSTORM

## Mandatory preflight
1. Run `.\hephaistos route` and `.\hephaistos status` or read the state files if the CLI is unavailable.
2. Continue only if the route authorizes brainstorming or the idea is explicitly tied to `ACTIVE_SUBJECT`.
3. If another step is expected, stop and report the expected next action.

## Goal
Generate useful alternatives without polluting the active execution flow.

## Procedure
1. Read mission, active subject, allowed branches, and current task.
2. For each idea, write the link to `ACTIVE_SUBJECT`.
3. Separate:
   - ideas directly supporting TASK_ACTIVE
   - new hypotheses connected to ACTIVE_SUBJECT
   - business/product angles
   - lateral ideas that must wait
4. For each useful idea record:
   - title
   - link_to_active_subject
   - claim
   - minimal evidence
   - expected value
   - business angle
   - risk
   - classification

## Classification
Use exactly:
- SUPPORT
- BACKLOG
- NEW_HYPOTHESIS
- REJECTED

## Constraint
Brainstorming does not automatically alter TASK_ACTIVE or ACTIVE_SUBJECT.
No new idea may interrupt active execution without an explicit route/state transition.

## Output
Produce:
- concise idea set
- ranking
- recommended action
- `radar-add` commands for non-active ideas
