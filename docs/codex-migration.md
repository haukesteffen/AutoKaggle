# Codex Migration And Token Efficiency Notes

Updated: April 4, 2026

This note captures the official guidance that informed the Codex refactor in this repo and the local operating decisions that follow from it.

## Official Guidance

### Codex prompting and model behavior

- OpenAI's Codex Prompting Guide says the Codex model family is faster and more token efficient than earlier coding agents and recommends `medium` reasoning effort as the default interactive balance for coding work.
- The same guide recommends removing unnecessary planning chatter, preambles, and repetitive status text because they increase token usage and can cause the agent to stop early instead of finishing the rollout.
- It also points to compaction support as the mechanism that enables longer-running coding sessions without immediately hitting context limits.

Source:
- https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

### Compaction and context management

- OpenAI documents compaction as a first-class context-management tool for long-running conversations.
- That is useful, but repo design still matters: compaction works better when durable state is already externalized into concise files rather than buried in conversational history.

Source:
- https://developers.openai.com/api/docs/guides/compaction

### Prompt caching

- OpenAI's prompt caching guidance says cache hits require exact prefix matches.
- Static instructions should be placed first, with dynamic content later.
- Identical tool and image prefixes also matter.

Implication for this repo:
- Keep stable repo instructions in `AGENTS.md`, `agents/program.md`, and short role files.
- Keep volatile run state in a separate generated summary file rather than interpolating large changing histories into every prompt.

Source:
- https://developers.openai.com/api/docs/guides/prompt-caching

### Token measurement

- OpenAI provides a token counting API so a host can measure the same payload it would send to `responses.create`.
- That matters if AutoKaggle later moves from interactive Codex use to a custom Responses or Codex SDK harness.

Source:
- https://developers.openai.com/api/docs/guides/token-counting

### Codex subagents

- OpenAI's Codex CLI docs say subagents are for larger parallelizable tasks.
- The same docs explicitly note that subagent workflows consume more tokens than comparable single-agent runs.
- Codex only spawns subagents when explicitly asked.

Inference from those docs:
- Subagents should be narrow, bounded, and used only when their parallelism or specialization justifies the added token cost.

Sources:
- https://developers.openai.com/codex/cli/features
- https://developers.openai.com/codex/concepts/subagents

### AGENTS.md guidance

- OpenAI's Codex best-practices docs say that if `AGENTS.md` gets too large, the main file should stay concise and point to task-specific markdown files instead.

Implication for this repo:
- Keep the root `AGENTS.md` small.
- Move role-specific details into short role files and contract docs.

Source:
- https://developers.openai.com/codex/learn/best-practices

## Decisions For AutoKaggle

### 1. Make the supervisor cold-startable

The old workflow relied too heavily on the supervisor thread remembering everything. That is exactly the failure mode that makes context grow without bound.

The new rule is:

- The supervisor must be able to resume from files alone.
- `agents/supervisor/run-state.md` is the default restart context.
- Fresh Codex sessions are a feature, not a failure mode.

### 2. Shrink the always-read prompt surface

Before this refactor, the shared program, role specs, and strategist references alone were already large. The baseline cost was too high before runtime state was even added.

The new default read set is:

1. `AGENTS.md`
2. `agents/program.md`
3. the relevant role file
4. `agents/supervisor/run-state.md`
5. only the active control file or explicitly needed source file

### 3. Separate durable ledgers from restart context

The long ledgers are still useful and should remain as source-of-truth histories:

- `agents/scientist/scientist-results.md`
- `agents/analyst/analyst-findings.md`
- `agents/analyst/analyst-knowledge.md`
- `agents/supervisor/leaderboard-history.md`

But the supervisor should not reread them wholesale on each wake. Instead, the repo now generates a compact restart summary:

```bash
uv run python -m harness.supervisor_snapshot
```

### 4. Use subagents only for bounded work

Recommended subagent posture:

- `Strategist`: yes, bounded and infrequent.
- `Analyst`: yes, one falsifiable hypothesis at a time.
- `Scientist`: yes, one concrete experiment task at a time.
- `Supervisor`: no persistent helper swarm. Keep orchestration local.

In this repo, those bounded roles should be represented as project-scoped custom agents in `.codex/agents/`, while the durable rules remain in repo markdown files. This keeps the Codex-side invocation ergonomic without duplicating the full role contract inside TOML.

Avoid:

- speculative parallel subagents
- multiple agents reading the same large histories
- subagents whose task is just “look around and think”

### 5. Prefer simple session resets over heroic compaction

Compaction is useful and officially supported, but for this repo the stronger pattern is:

1. complete one atomic wake
2. refresh `agents/supervisor/run-state.md`
3. commit the durable checkpoint
4. continue in a fresh Codex session when convenient

That fully resets thread bloat instead of merely compressing it.

## Practical Recommendations

- Start the supervisor with `medium` reasoning effort unless a specific task needs more.
- Keep supervisor replies terse and operational.
- Avoid asking Codex to restate plans unless the user actually needs them.
- Keep stable instructions in files that barely change.
- Keep changing state in one compact generated file.
- Read full histories only on demand, preferably by tailing or searching for the specific entry you need.
- If AutoKaggle later moves to a custom API harness, structure prompts for prompt caching by keeping the static prefix identical across wakes.
