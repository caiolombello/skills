---
name: ai-interface-design
description: "Use with frontend-design when designing or reviewing AI-native web interfaces: chat, copilots, generative editors, agent runs, tool activity, citations, or streamed artifacts. Owns model-state UX, user control, trust, cost/latency disclosure, and business-value evidence; not implementation code."
---

<!-- Inspired by Nutlope/hallmark (MIT) and heliocosta-dev/revenue-centric-design (custom terms). See ../CREDITS.md and LICENSE. -->

# AI Interface Design

Design AI-native product interfaces that make uncertain, asynchronous model behavior understandable, controllable, and valuable. Apply [`frontend-design`](../frontend-design) as the baseline for flow, responsive behavior, accessibility, and design-system reuse; use this skill for the AI-specific interaction contract.

## License boundary

Do not apply this skill to betting, casino, gambling, loot-box, or other real-money games-of-chance products. Its Revenue-Centric Design influence is subject to the field-of-use restriction in [LICENSE](LICENSE). If such a request triggers this skill implicitly, disclose the exclusion and use only the independently written [`frontend-design`](../frontend-design) baseline; if the user explicitly asks for these restricted principles, decline that use.

## Scope boundaries

- Use for chat, copilots, generative workspaces, semantic search, agent workflows, tool calls, multimodal generation, and AI-assisted decisions.
- Use [`frontend-design`](../frontend-design) alone when no model behavior materially affects the user experience.
- Use [`frontend-development`](../frontend-development) after the AI interaction contract and acceptance criteria are approved.
- Use [`throwaway-prototype`](../throwaway-prototype) when competing interaction models need hands-on comparison.
- Use [`security-hardening`](../security-hardening) for application security controls; this skill makes those boundaries visible and usable.

## Principles

1. **Start from a value event.** Define what useful outcome the user reaches, not merely that they submitted a prompt or received tokens.
2. **Choose the interaction by the work.** Chat is one primitive, not the default shell for every AI feature.
3. **Show meaningful progress, not hidden reasoning.** Expose user-relevant stages, tools, approvals, sources, and outcomes without revealing or fabricating chain-of-thought.
4. **Treat output as inspectable work.** Make generated content reviewable, editable, attributable, and reversible before it becomes authoritative.
5. **Preserve user agency.** Support stop, retry, edit, branch, undo, and scoped regeneration where the workflow permits.
6. **Never fake intelligence or proof.** Do not invent citations, confidence, customer claims, metrics, precision, tool activity, or model capabilities.
7. **Earn visual distinctiveness from the brief.** Vary structure and hierarchy to fit the task; changing gradients on the same AI template is not a design direction.
8. **Balance user and business outcomes.** Monetization must follow demonstrated value and real usage limits, never obscure cost or manipulate consent.

## Workflow

### 1. Inspect the actual product and model contract

Read project rules and the existing design system, then establish:

- Model-supported inputs, outputs, context limits, tools, and modalities.
- Streaming, latency range, cancellation, timeout, retry, and partial-result behavior.
- Persistence, history, versioning, citation, provenance, and export capabilities.
- Cost, quota, rate-limit, and plan boundaries visible to the product.
- Data retention, privacy, permission, approval, and human-review requirements.
- Known failure modes: unsupported requests, stale context, hallucination, unsafe output, tool failure, and ambiguous completion.

Do not design controls for capabilities the implementation cannot provide.

### 2. Define the value and evidence contract

Record:

- Primary user, job, input, and desired artifact or decision.
- Value event: the observable moment the user receives useful value.
- Product outcome and one guardrail against harmful optimization.
- Evidence currently available: research, analytics, support reports, model evals, or none.
- Assumptions that need validation.

Prefer task completion, accepted output, reduced rework, or time-to-value over raw prompt count. Do not claim a conversion or retention effect without evidence.

### 3. Select the interaction primitive

Choose the smallest form that matches the work:

| Work shape | Prefer | Avoid |
|---|---|---|
| Iterative exploration | Conversation with editable turns and branches | Treating every response as final |
| Contextual assistance | Inline copilot beside the object being changed | A detached chat panel |
| Constrained generation | Structured inputs plus preview and validation | Asking users to learn prompt syntax |
| Long-form or multimodal creation | Canvas or artifact workspace with versions | Streaming a large artifact into a chat bubble |
| Search and synthesis | Query, result set, sources, and comparison view | One opaque answer with hidden retrieval |
| Multi-step agent work | Run timeline, plan, approvals, outputs, and recovery | A spinner labeled “thinking” |
| High-impact decision support | Evidence table, uncertainty, alternatives, and human sign-off | A single recommendation presented as fact |

### 4. Build the model-state matrix

Cover every relevant state explicitly:

| State | Show | User control | Recovery |
|---|---|---|---|
| Ready/composing | Scope, examples, constraints, and expected output | Edit input and attachments | Preserve the draft |
| Queued/starting | Honest status and expected wait when known | Cancel | Resume input without loss |
| Streaming | Stable partial output and current user-relevant stage | Stop; inspect sources when available | Keep useful partial work |
| Tool or agent activity | Tool name, purpose, permission boundary, and result status | Approve, deny, or narrow when required | Retry only the failed step |
| Awaiting input/approval | Exact decision, impact, and safe default | Answer, edit, approve, or decline | Return to the run context |
| Partial/stale | What completed, what is missing, and freshness | Continue, refresh, or accept partial | Do not imply completeness |
| Complete | Artifact, sources, changes, and next action | Edit, compare, export, undo, or branch | Preserve version history |
| Failed/rate-limited | Specific safe error, retained work, retry timing | Retry or change scope/model | Never discard valid input |
| Refused/unsupported | Clear boundary without fabricated policy detail | Reframe or choose a supported path | Keep the original request editable |
| Cancelled | What stopped and what may already have changed | Resume or start a branch | Distinguish cancellation from rollback |

Use determinate progress only when the system knows total work. Never animate fake progress toward 100%.

### 5. Design input, output, and control behavior

- Keep manual edits authoritative; late model output must not overwrite them.
- Make prompt history, selected context, attachments, and scope inspectable before execution.
- Define what retry repeats: the whole run, one step, one tool, or one output region.
- Make “regenerate” preserve the prior version and state what will change.
- Separate model prose, tool results, retrieved sources, and user-authored content visually and semantically.
- Attach citations to the claims they support; expose missing or failed sources.
- Label estimates, suggestions, and uncertain inferences without false numeric confidence.
- Provide previews and explicit confirmation before external, destructive, financial, permission-changing, or irreversible actions.
- Announce streaming and status changes accessibly without flooding assistive technology.

### 6. Create a brief-led visual fingerprint

Inspect existing brand and product patterns first. For a new direction, use [the visual-direction reference](../frontend-design/references/visual-direction.md) selectively; do not load a brand collection or duplicate the baseline. Then define:

- Macrostructure: conversation, workbench, canvas, timeline, comparison, command surface, or another task-led shape.
- Hierarchy: input, generated work, evidence, controls, status, and next action.
- Density, typography, spatial rhythm, color role, imagery, motion, and component voice.
- One or two intentional differentiators tied to the domain or workflow.

Reject default AI aesthetics when the brief does not justify them:

- Purple/blue glow, gradient mesh, glass cards, floating orbs, and decorative grid backgrounds.
- Oversized generic hero copy, pill overload, repeated equal cards, and identical icon-feature rows.
- Chat bubbles around content that is actually a document, table, workflow, or artifact.
- Sparkle icons as the only signal of AI capability.
- Fake terminal output, fabricated dashboards, invented testimonials, or decorative citations.

These are defaults to question for new work, not a ban on the user’s chosen visual language. Preserve established brand choices unless the redesign authorizes changing them. Distinctiveness must not reduce comprehension, accessibility, performance, or design-system consistency. In rendered QA, inspect long streamed content, partial output, source expansion, and approval controls; decorative motion must not compete with streaming or status announcements.

### 7. Make trust and safety legible

- Show what data enters the model, what is retained, and who can access generated artifacts.
- Treat retrieved content, tool output, generated HTML/Markdown, and uploaded files as untrusted display data.
- Distinguish “hidden because unauthorized” from backend authorization; UI visibility is not a security boundary.
- Place approval at the decision point and describe the concrete effect.
- Make audit history, authorship, model/tool provenance, and version changes available in proportion to risk.
- Give users a path to report, correct, or override harmful or wrong output.

### 8. Define ethical product measurement

Measure the value event and friction around it:

- Activation and time-to-value.
- Task completion and accepted-output rate.
- Edit distance, corrections, retries, abandonment, and escalation to a human.
- Latency, cancellation, tool failure, and cost per successful task.
- Source inspection, approval denial, undo, and safety-intervention rates where relevant.
- Retention or expansion only when tied to repeated value, not forced engagement.

Present pricing or upgrade prompts after value is evident or a real usage limit is reached. Explain the limit and preserve the user's work. Do not use obstructive cancellation, hidden defaults, artificial urgency, or underpowered experiments as evidence.

### 9. Produce the handoff

Deliver:

1. User, job, value event, product outcome, evidence, and assumptions.
2. Chosen interaction primitive and rejected alternatives.
3. End-to-end flow and model-state matrix.
4. Input, output, editing, retry, approval, and recovery contracts.
5. Visual fingerprint and existing-system reuse.
6. Trust, privacy, provenance, and accessibility requirements.
7. Measurement plan, guardrails, acceptance criteria, and unresolved decisions.

Use [references/ai-interface-review.md](references/ai-interface-review.md) for a formal review or implementation handoff.

## Review order

1. Value event and task completion.
2. Interaction primitive and information architecture.
3. Model states, recovery, and user control.
4. Trust, provenance, permissions, and high-impact actions.
5. Accessibility, responsive behavior, and realistic content.
6. Visual specificity and anti-template quality.
7. Measurement and monetization integrity.

Report observed defects separately from hypotheses and aesthetic preferences.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| “Add a chatbot” without a user job | Chooses a technology shell before the workflow |
| Endless spinner or “AI is thinking” | Hides progress, failure, and control |
| Retry with undefined scope | Can duplicate work or repeat costly actions |
| Final-looking output with no provenance | Encourages automation bias |
| Raw chain-of-thought as transparency | Exposes the wrong signal and may fabricate confidence |
| Prompt engineering as required UX | Transfers product complexity to the user |
| AI styling as purple gradients and sparkles | Signals category sameness instead of product identity |
| Engagement as the primary success metric | Rewards more interaction instead of useful completion |
| Upsell before demonstrated value | Interrupts the value path and erodes trust |

## Verification checklist

- [ ] The model, tool, data, latency, quota, and permission contracts were inspected rather than invented.
- [ ] The user job, value event, product metric, guardrail, evidence, and assumptions are explicit.
- [ ] The interaction primitive fits the work; chat was not chosen by reflex.
- [ ] Streaming, tool activity, approval, partial, failed, refused, cancelled, stale, and complete states are covered as relevant.
- [ ] Stop, retry, edit, branch, regenerate, undo, and recovery scopes are defined.
- [ ] User edits and valid input survive late responses and failures.
- [ ] Claims, citations, uncertainty, provenance, privacy, and action effects are honest.
- [ ] The visual structure comes from the brief and avoids unjustified AI-template defaults.
- [ ] Accessibility and responsive behavior inherit the full `frontend-design` baseline.
- [ ] Monetization follows real value and usage; dark patterns are excluded.
- [ ] Acceptance criteria are implementation-ready and unverified assumptions remain labeled.
