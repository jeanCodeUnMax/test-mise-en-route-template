# HEPHAISTOS Claude Code Contract

This repository is controlled by HEPHAISTOS. The conversation is not the source of truth.

## Mandatory First Move
Before brainstorming, PRD work, decomposition, implementation, review, research, tool use, or documentation updates:

```powershell
.\hephaistos route
.\hephaistos status
```

## State-Of-Art Gate
Before converting a brainstorm into a PRD, produce or update a state-of-art report:

```powershell
.\hephaistos state-of-art "idea/topic" --query "scientific legal market search terms" --research-question "..." --method "..." --baseline "..." --metric "..." --benchmark "..." --go INCONCLUSIVE
```

The report must be paper-grade, not a loose summary. It must include:

- research questions;
- method variants;
- baselines to beat;
- experiment axes;
- metrics and KPIs;
- benchmarks and datasets;
- scaling or crossover tests;
- external baselines;
- already done work;
- useful indices to reuse;
- required gap/difference;
- market or regulatory signal;
- limitations and kill criteria;
- transfer to PRD/tasks/benchmarks;
- GO / NO_GO / MODIFY / INCONCLUSIVE;
- next action.

If web/search tools are available, use them and cite sources in the report. If they are unavailable, mark the report `INCONCLUSIVE` and list the missing searches.

If the command is unavailable, read these files in order and report the blockage instead of guessing:

1. `.hephaistos/project.yaml`
2. `.hephaistos/state.yaml`
3. `.hephaistos/tasks/T*.yaml`
4. `.hephaistos/ledger.jsonl`
5. `docs/master/PROJECT_MASTER.md`
6. `.agent/rules/*.md`

## Routing Rules
- If the project is `UNINITIALIZED`, only initialization is authorized.
- If route says `STATE_OF_ART_REQUIRED`, brainstorm is allowed only to create a state-of-art report.
- If route says `PRD_REQUIRED`, create the PRD from the latest state-of-art report.
- If route says `TASK_GRAPH_REQUIRED`, create task files with dependencies, evidence, and `done_when`.
- If route says `TASK_ACTIVE`, work only on that task.
- If evidence is missing, create evidence before commit/push.
- If the user proposes a lateral idea, connect it to `ACTIVE_SUBJECT` or record it with `radar-add`.
- Never mark work complete from narrative confidence. Completion requires CLI/watchdog validation.

## Creativity Rule
Do not kill a useful idea by saying it is another topic too early.
Ask:

- Does it strengthen `ACTIVE_SUBJECT`?
- Which allowed branch does it touch?
- What claim does it create?
- What minimal evidence would prove or kill it?
- What does the state of the art already say?
- What significant difference do we bring?
- What business/research value could it support?

Then classify it as `SUPPORT`, `NEW_HYPOTHESIS`, `BACKLOG`, or `REJECTED`.

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
