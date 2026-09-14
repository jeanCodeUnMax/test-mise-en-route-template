# HEPHAISTOS WORKSPACE — CORE RULES

## Purpose
This workspace is controlled by a deterministic project/task workflow.
The agent must not rely on conversational memory as the source of truth.

## Source of truth order
1. `.hephaistos/project.yaml`
2. `.hephaistos/tasks/T*.yaml`
3. `.hephaistos/state.yaml`
4. `.hephaistos/ledger.jsonl`
5. `docs/master/PROJECT_MASTER.md`
6. Git history
7. Conversation context

If these disagree, the structured `.hephaistos/*` state wins unless explicitly corrupted.

## Mandatory operating loop
Before doing project work:
1. Run `.\hephaistos route` or `.\hephaistos status`.
2. Identify `MISSION`, `ACTIVE_SUBJECT`, allowed branches, `TASK_ACTIVE`, dependencies, evidence requirements, and `NEXT_ACTION`.
3. Work only on the authorized next step.
4. Classify related discoveries by their link to `ACTIVE_SUBJECT`.
5. Do not silently switch tasks or stage.

## Active subject rule
A new idea is not automatically drift.
It is authorized when it strengthens `ACTIVE_SUBJECT` and can be expressed as a testable claim, required evidence, or backlog item.

Allowed classifications:
- SUPPORT: helps the active task or subject now.
- NEW_HYPOTHESIS: connected to active subject but needs protocol before implementation.
- BACKLOG: connected but not useful for the current step.
- REJECTED: weak link, no evidence path, or no value.

Drift begins when an idea changes the active subject without explicit promotion.

## State authority
The LLM may understand, brainstorm, propose, decompose, implement, document, analyze, and recommend transitions.
The deterministic CLI/watchdog decides whether work is validable.

## No fake proof
Never use mock, stub, fake, or invented output as evidence of real execution.
Synthetic controls are allowed only when explicitly labeled `SYNTHETIC`.
Real-world claims require real execution evidence.

## Money filter
High-priority work should move at least one of these forward:
- reproducible evidence;
- benchmark credibility;
- compliance/audit value;
- customer pain;
- demonstrable cost, latency, quality, or safety gain;
- investor/research note.

## Completion vocabulary
Use these states consistently:
- PENDING
- READY
- ACTIVE
- BLOCKED
- VALIDATING
- DONE
- FAILED
- SUPERSEDED
- BACKLOG

## Never silently erase
Preserve hypotheses, negative results, failed experiments, abandoned branches, unexpected signals, rejected alternatives, and migration provenance.
