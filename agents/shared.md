# AutoKaggle Shared Contract

- Use repo files as the source of truth; keep prompts and outputs restart-safe from files alone.
- Read only the smallest file set that can answer the current question.
- Keep each invocation bounded and end it with one compact terminal result.
- Put raw logs, bulky evidence, and long stdout in `artifacts/<task_id>/`.
- If a result suggests a memory update, return it as a candidate note instead of editing memory directly.
