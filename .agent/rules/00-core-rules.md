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
6. `docs/radar/state-of-art-*.md`
7. Git history
8. Conversation context

## Mandatory operating loop
Before doing project work:
1. Run `.\hephaistos route` or `.\hephaistos status`.
2. Identify `MISSION`, `ACTIVE_SUBJECT`, allowed branches, `TASK_ACTIVE`, dependencies, evidence requirements, and `NEXT_ACTION`.
3. Work only on the authorized next step.
4. Before PRD, confront the idea with state of the art.
5. Classify related discoveries by their link to `ACTIVE_SUBJECT`.
6. Do not silently switch tasks or stage.

## State-of-art gate
Promising ideas must be checked against external reality before PRD:
- scientific sources;
- implementation/tooling sources;
- legal/regulatory sources when relevant;
- market/business sources when relevant.

Every state-of-art report must decide: GO, NO_GO, MODIFY, or INCONCLUSIVE.

A valid state-of-art report must be paper-grade: research questions, method variants, baselines, axes, metrics, benchmarks, scaling/crossover tests, external baselines, limits, kill criteria, and transfer into PRD/tasks/benchmarks.

## Active subject rule
A new idea is not automatically drift.
It is authorized when it strengthens `ACTIVE_SUBJECT` and can be expressed as a testable claim, required evidence, state-of-art report, or backlog item.

## Money filter
High-priority work should move at least one of these forward:
- reproducible evidence;
- benchmark credibility;
- compliance/audit value;
- customer pain;
- demonstrable cost, latency, quality, or safety gain;
- investor/research note.

## No fake proof
Never use mock, stub, fake, or invented output as evidence of real execution.
Synthetic controls are allowed only when explicitly labeled `SYNTHETIC`.
Real-world claims require real execution evidence.

## Never silently erase
Preserve hypotheses, negative results, failed experiments, abandoned branches, unexpected signals, rejected alternatives, and migration provenance.
