# SKILL — PRD

## Mandatory preflight
1. Run `.\hephaistos status` or read `.hephaistos/state.yaml` and `docs/master/PROJECT_MASTER.md` if the CLI is unavailable.
2. Continue only if the current HEPHAISTOS state authorizes this skill.
3. If another step is expected, stop and report the expected next action.

## Goal
Convert an authorized idea into an implementation-ready Product Requirements Document.

## PRD structure
- title
- problem
- users / actors
- context
- goals
- non-goals
- functional requirements
- non-functional requirements
- constraints
- assumptions
- interfaces
- data / evidence requirements
- security / privacy considerations
- success metrics
- acceptance criteria
- risks
- unresolved questions
- deliverables

## Rules
Do not hide uncertainty.
Mark inferred requirements as assumptions.
Separate MUST / SHOULD / COULD where useful.

## Completion gate
A PRD is ready for decomposition only if:
- main deliverables are explicit
- success criteria are measurable
- unresolved blockers are identified
- out-of-scope items are explicit
