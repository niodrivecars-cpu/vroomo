# Prompt Quality Review

How to assess the prompts and agent definitions that drive the platform's
skills (`.opencode/agent/*`, `opencode.jsonc`, capability docs).

## Criteria
| # | Criterion | Pass |
|---|---|---|
| 1 | **Starts at the kernel** | prompt routes through `kernel/decision-tree.md` |
| 2 | **Bound scope** | the prompt names its capability and refuses adjacent ones |
| 3 | **Evidence requirement** | prompt instructs "cite evidence or mark unverified" |
| 4 | **Gap ownership** | prompt requires owners/phases for anything not proven |
| 5 | **Terminology fixed** | prompt uses glossary terms, not synonyms |
| 6 | **No prompt drift** | prompt matches the current capability doc; stale prompts fail |
| 7 | **Deterministic enough** | outcome does not depend on unspoken assumptions |

## Anti-patterns (fail)
- A prompt that lets the agent decide its own process.
- A prompt that asks for conclusions without evidence.
- A prompt referencing a doc/path that no longer exists.

## Verdict
PASS, or FAIL with the criterion — recorded as meta evidence.
