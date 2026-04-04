# Strategist Contract

## Inputs

Required:

- `agents/strategist/strategy-request.md`

Optional, only when needed:

- `agents/analyst/analyst-knowledge.md`
- `agents/supervisor/leaderboard-history.md`
- `agents/supervisor/run-state.md`

## Output

Write only:

- `agents/strategist/strategy-whitepaper.md`

## Whitepaper Shape

```markdown
# Strategy Whitepaper

## Current Date
<absolute date>

## Deadline Assumption
<absolute date and assumption>

## Days Remaining
<integer>

## Read
<concise factual read of pace, coverage, and current signal>

## Emphasis
Primary: <main focus>
Secondary: <still-active supporting focus>
Background: <low-volume supporting work>
Hold: <what should stay quiet>

## Guidance For The Supervisor
1. <recommendation>
2. <recommendation>
3. <optional recommendation>

## Refresh Triggers
- <condition>
- <condition>
```

## Rules

- Use absolute dates.
- Keep the whitepaper run-specific.
- Set lanes and priorities, not code-level implementation.
- Use the request as the factual snapshot.
- Do not read the full findings history by default.
