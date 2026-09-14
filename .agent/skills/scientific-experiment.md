# SKILL — SCIENTIFIC EXPERIMENT

## Mandatory preflight
1. Run `.\hephaistos status` or read `.hephaistos/state.yaml` and `docs/master/PROJECT_MASTER.md` if the CLI is unavailable.
2. Continue only if the current HEPHAISTOS state authorizes this skill.
3. If another step is expected, stop and report the expected next action.

## Goal
Run a hypothesis-driven experiment with reproducible evidence.

## Workflow
1. State hypothesis.
2. State counter-hypothesis.
3. Define expected signal.
4. Define baseline.
5. Define dataset.
6. Define metrics.
7. Define kill / success criteria.
8. Record environment.
9. Execute real run.
10. Save raw output.
11. Analyze without overwriting raw results.
12. Record unexpected observations.
13. Test alternative explanations.
14. Conclude KEEP / MODIFY / KILL / INCONCLUSIVE.
15. Create next task or backlog item.

## Never
- infer success from one attractive example
- overwrite negative runs
- convert synthetic controls into empirical claims
- skip raw-result preservation
