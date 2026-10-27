# Investigating design rationale

Use this when the question is why code has its current shape, where a threshold came from, or whether a proposed change would erase an important constraint. For current mechanics, trace the source instead. This procedure is informed by pstack's `why`; see [credits](../../CREDITS.md).

Anchor the question in actual paths, symbols and the checked revision. Inspect the relevant implementation and tests, then the history that could explain it: a bounded `git blame`/`git log` over the affected lines/path, substantive PR discussion, nearby ADRs, issues, or incident records. Follow renames or an earlier decision when the latest edit merely moved code. The newest commit is not automatically the decision's origin.

Use connected documents, chats, metrics or incidents only when they are relevant and available within the task's scope. Prefer precise issue/PR/thread identifiers and narrow queries over searching every app. Do not contact people, read unrelated private history, or require a category-wide search for a trivial question. Parallel investigation is useful for independent evidence, not a mandatory investigator per connector.

Keep three kinds of conclusion distinct:

- **Documented rationale:** a source explicitly records the decision/reason; cite the actual location and date/revision.
- **Supported inference:** current behavior or converging history suggests a reason; explain the evidence and credible competing explanations.
- **Unknown:** the consulted material does not establish it. Record relevant unavailable or empty sources as gaps; absence of a record does not mean the constraint never existed.

Compare historical rationale to the current code and environment. An old workaround can have been necessary and now be obsolete; a recent refactor can preserve an older invariant. State which claim is historical and which is currently verified. Do not use a transcript summary as fresh runtime proof.

Return the answer at the requested depth with source pointers, meaningful uncertainty and any consequence for a proposed change: what must be preserved, what can change with evidence, and which assumption still needs a check. Do not create an ADR or edit the code just because an explanation was requested; [architecture-decision-records](../../architecture-decision-records/SKILL.md) owns recording a new consequential decision when requested.
