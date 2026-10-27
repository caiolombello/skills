---
name: technical-writing
description: "Use when drafting or revising developer documentation, tutorials, how-to guides, API references, and technical explanations. Owns document purpose and usable examples; natural-writing owns voice, and specialized PR/runbook workflows keep their contracts."
---

<!-- Inspired by cursor/plugins pstack technical-writing (MIT) and Diataxis. See ../CREDITS.md. -->

# Technical Writing

Make the document useful to its intended reader. Establish what they know, what they want to do or understand, and which source/version the text describes. Infer these from the task and material; ask only for missing information that materially changes the result.

## Select the purpose

Use the Diataxis distinction to shape the requested material:

| Purpose | Organize around | Evidence of a useful result |
| --- | --- | --- |
| Tutorial | A newcomer builds something visible in guided steps | Prerequisites and each meaningful step have an expected outcome |
| How-to | An experienced reader solves a specific problem | Ordered actions, conditions, relevant alternatives, and recovery |
| Reference | A reader looks up exact behavior | Actual names, types/options, defaults, limits, errors and version scope |
| Explanation | A reader understands a design or tradeoff | Context, mechanisms, reasons, alternatives, and evidence for claims |

A README may orient readers and link to several modes. Use a dominant purpose per section; split only when mixed goals obscure the task. Do not enforce a separate document for every mode or turn a short PR body into a manual.

Writing is not permission to create unrelated docs. Follow [no-docs-unless-asked](../no-docs-unless-asked/SKILL.md). For a requested design sketch, a concise usage example in the plan can expose the intended API without adding a README. Preserve specialized output contracts: [pr-workflow](../pr-workflow/SKILL.md), [runbook-authoring](../runbook-authoring/SKILL.md), and required templates own their structure.

## Ground the content

- Use current project code, pinned dependency documentation and actual tool contracts for commands, flags, paths, defaults and behavior. Never invent a plausible command or report an unexecuted example as tested.
- Explain from the caller/reader's point of view. Put the required environment, inputs and condition before the action. State the observable result, not just the command.
- Keep examples minimal but sufficient: required imports/setup, explicit placeholders, meaningful output and important failure behavior. Never include real secrets. Distinguish runnable code from a usage sketch or pseudocode.
- Mark unavailable checks, uncertainty, platform/version limits and inference. Dry reference prose is not a license to hide unknowns. Distinguish historical rationale from a guess about the author's intent; use [zoom-out](../zoom-out/SKILL.md) when source/history investigation is needed.
- Follow the current artifact. If docs and implementation disagree, identify the discrepancy before choosing the promised behavior. Under docs-only scope, do not silently fix product code or rewrite a regression as intended behavior.

## Write and verify

Use [natural-writing](../natural-writing/SKILL.md) for register and natural prose. Keep exact symbols, code, quotes, required wording and schemas protected. Prefer direct verbs and the project's real vocabulary; explain a necessary term once rather than inventing a new label for it.

Use numbered steps for a sequence, headings for navigation and tables for lookup when they help. Keep terminology consistent. Place a warning before the action that needs it. Sentence length and Diataxis are aids to comprehension, not mechanical quotas or bans on a useful mixed paragraph.

Check links/paths, example inputs and expected results against the cited version. Run examples when authorized, safe, and useful; inspect effectful commands before execution. Do not submit real requests, install dependencies, send messages, or alter active state merely to validate documentation. State which examples were executed and which were inspected or remain unrun.

Return the requested document or focused edit. Add validation notes only when requested or when needed to distinguish checked behavior from a draft. Drafting, file creation, publication and sending remain distinct actions.

[Evaluation cases](evals/scenarios.json) cover purpose selection and exact-output constraints.
