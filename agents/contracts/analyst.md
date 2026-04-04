# Analyst Contract

## Inputs

Required:

- `agents/analyst/analyst-hypothesis.md`
- `agents/analyst/analyst-knowledge.md`

Read only the minimum additional files needed for the active hypothesis.

## Outputs

Editable tracked files:

- `agents/analyst/analysis.py`
- `agents/analyst/analyst-findings.md`
- `agents/analyst/analyst-knowledge.md`

## Hypothesis Shape

```markdown
# Active Analyst Hypothesis
status: active
id: A-018
at: 2026-03-29T10:45Z
q: <specific yes/no question>
reference: <optional short references>
```

## Findings Shape

```markdown
## A-018
at: 2026-03-29T11:03Z
q: <question>
verdict: supported | rejected | inconclusive | blocked
conf: high | medium | low
reference: <optional short references>
evidence:
<captured stdout from analysis.py>

follow_up:
- <yes/no hypothesis>
- <yes/no hypothesis>
- <yes/no hypothesis>
```

## Knowledge Rules

- `analyst-knowledge.md` is curated durable memory, not a full history.
- Keep only facts likely to matter again.
- Prune aggressively.

## Workflow Rules

- One invocation = one hypothesis = one terminal entry.
- Stay factual and non-strategic.
- Do not train models.
- Do not read the full findings history by default.
- If blocked before the harness can succeed, append one blocked terminal entry manually.
