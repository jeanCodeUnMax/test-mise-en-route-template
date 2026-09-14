# SKILL — PRD

## Mandatory preflight
1. Run `.\hephaistos route` or `.\hephaistos status`.
2. Continue only if the route authorizes PRD.
3. Read the latest `docs/radar/state-of-art-*.md` before writing the PRD.
4. If no state-of-art report exists, stop and create/request one first.

## Goal
Convert an authorized, externally checked idea into an implementation-ready Product Requirements Document.

## PRD structure
- title
- problem
- users / actors
- state-of-art summary with research questions, baselines, metrics, benchmarks, and limitations
- difference / thesis
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
Do not claim novelty unless the state-of-art report supports a specific difference.

## Completion gate
A PRD is ready for decomposition only if:
- state-of-art report is referenced
- main deliverables are explicit
- success criteria are measurable
- unresolved blockers are identified
- out-of-scope items are explicit
- first proof/benchmark path is visible
- baselines, metrics, and kill criteria from the state-of-art report are preserved
