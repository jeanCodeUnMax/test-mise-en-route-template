# SKILL — BRAINSTORM

## Mandatory preflight
1. Run `.\hephaistos route` and `.\hephaistos status` or read the state files if the CLI is unavailable.
2. Continue only if the route authorizes brainstorming, state-of-art, or the idea is explicitly tied to `ACTIVE_SUBJECT`.
3. If another step is expected, stop and report the expected next action.

## Goal
Generate useful alternatives, then force promising ideas through a mini state-of-art review before PRD.

## Procedure
1. Read mission, active subject, allowed branches, and current route.
2. For each idea, write the link to `ACTIVE_SUBJECT`.
3. Select the strongest idea only when it has a plausible claim and evidence path.
4. Prepare search questions for scientific, legal/regulatory, market, and implementation sources.
5. Use available web/research tools when allowed.
6. Produce or request a `state-of-art` report before PRD.

## State-of-art questions
Use a paper-grade review frame before PRD:

- What exact research/business question is being tested?
- Which methods and variants must be compared?
- Which baselines must be beaten?
- Which papers/tools/laws/market signals matter?
- What experiment axes matter: scale, data, model, hardware, prompt class, attack/failure class, regulation, market?
- Which metrics and KPIs decide the claim: quality, memory, latency, cost, safety, traceability, compliance?
- Which benchmarks/datasets/tasks will decide the claim?
- What scaling or crossover curve would make the idea serious?
- What part is already solved?
- What useful indices can be reused?
- What gap/difference must we bring?
- What would prove the idea impossible or not worth doing?
- What transfers into PRD, tasks, benchmark plan, or research note?

## Classification
Use exactly:
- SUPPORT
- BACKLOG
- NEW_HYPOTHESIS
- REJECTED

## Output
Produce:
- concise idea set
- top idea
- search query pack
- paper-grade state-of-art summary or command
- GO / NO_GO / MODIFY / INCONCLUSIVE recommendation
- `radar-add` commands for non-active ideas
