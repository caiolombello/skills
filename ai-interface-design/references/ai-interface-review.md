# AI Interface Review and Handoff

Load this reference for a formal review or implementation handoff.

## Context

- Product surface:
- Primary user and job:
- AI capability and model/tool contract:
- Value event:
- Product outcome:
- Guardrail:
- Evidence:
- Assumptions:
- Existing design-system primitives:

## Interaction decision

- Selected primitive:
- Why it fits:
- Alternatives rejected:
- Input and context:
- Primary artifact or decision:
- Human review point:

## Flow

1. Entry:
2. Input and scoping:
3. Execution:
4. Review and correction:
5. Commit, export, or action:
6. Recovery or safe exit:

## Model-state matrix

| State | Trigger | Visible status | Available control | Preserved work | Recovery | Accessible announcement |
|---|---|---|---|---|---|---|
| Ready | | | | | | |
| Starting/queued | | | | | | |
| Streaming | | | | | | |
| Tool/agent activity | | | | | | |
| Awaiting approval/input | | | | | | |
| Partial/stale | | | | | | |
| Complete | | | | | | |
| Failed/rate-limited | | | | | | |
| Refused/unsupported | | | | | | |
| Cancelled | | | | | | |

Remove irrelevant rows and add domain-specific states.

## Control contract

- Stop:
- Retry scope:
- Edit and resubmit:
- Branch/version:
- Regenerate scope:
- Undo/rollback:
- Approval and denial:
- Duplicate-action prevention:

## Trust and provenance

- User data sent:
- Retention and visibility:
- Generated vs user-authored content:
- Tool/retrieval provenance:
- Citation behavior:
- Uncertainty and limitations:
- High-impact action preview:
- Audit/version history:
- Report, correct, or override path:

## Visual fingerprint

- Macrostructure:
- Hierarchy:
- Density and spatial rhythm:
- Typography:
- Color roles:
- Component voice:
- Motion and reduced-motion behavior:
- Domain-specific differentiators:
- Existing tokens/components reused:
- AI-template defaults explicitly rejected:

## Responsive and accessibility behavior

- Narrow and wide layout:
- Keyboard and focus order:
- Streaming/status announcements:
- Zoom, reflow, and text enlargement:
- Touch targets and input modes:
- Long prompts, long outputs, code, tables, citations, and attachments:

## Measurement

| Signal | Why it matters | Instrumentation | Guardrail |
|---|---|---|---|
| Value event / activation | | | |
| Time-to-value | | | |
| Accepted output / task completion | | | |
| Edits, retries, or abandonment | | | |
| Latency, failure, and cost | | | |
| Approval, undo, or escalation | | | |

## Acceptance criteria

- [ ] ...

## Open decisions

- ...
