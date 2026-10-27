# Surfaces, context, and artifacts

Read the live host instructions and tool descriptions. This reference records contracts inspected on 2026-10-27, not a guarantee that a given tool is exposed to every provider or child.

## Browser and devices

When browser work is requested, T3's shared browser is `preview_*`: call `preview_status` first, then `preview_open` if there is no automatable tab. Public pages requested only as research use web fetch/search. Do not use preview tools unasked to verify your own edit, even if a matching tab exists; host restrictions govern the check. Do not repeat a preview call just because an earlier turn used it.

Use snapshot locators over coordinates. References expire on navigation, a new snapshot, or handoff. Check control ownership: act on your tab or an unclaimed one with no human in control. Do not seize human control. Parallel workers need separate owned tabs (`reuseExistingTab: false` when opening one), not simultaneous input to the same tab. Close a tab this run opened before handback unless the user requested it or uses it.

Switch browsers only when tools are absent, `preview_open` reports unsupported, the user asks, or two preview calls fail on the same step. Quote the error before using the allowed alternative. Tool absence/unsupported means the observed contract, not an assumption from the model name. Page evaluation can mutate state; do not label arbitrary evaluate calls read-only.

Browser preview is not native desktop access. `device_list`/`device_open` concern supported iOS/Android emulators; use the actual returned device controls/CLI contract. Neither implies control of the user's Linux desktop. For all surfaces follow [computer-use](../../computer-use/SKILL.md).

## Thread continuity

Given a thread id, use `t3_thread_read` before answering about it. Keep reads bounded; page with `nextPosition` and retrieve a truncated item's continuation using its actual `itemId`/`nextTextOffset`. Search only the task-relevant project/history; do not mine unrelated private transcripts to infer preferences.

A thread's first mention in a reply uses its returned `link` verbatim; without one use `[title](t3-thread://v1/<exact id>)`. Never invent an id or substitute a plain title. A recalled transcript is history: reconcile it with current files, head, tool state and unresolved work. Use [context-engineering](../../context-engineering/SKILL.md) and [handoff](../../handoff/SKILL.md).

For a catch-up, tell the user what changed, which results are verified, what remains active or blocked, and any decision actually needed. For a continuation brief, preserve source/version pointers, authorization and stop conditions, evidence paths, and uncertainties. Do not create a new thread, change memory/global preferences, or start a recurring recap just because a catch-up was requested.

`t3_worktree_handoff` moves this thread, not a child: it is a final tool call that ends the current live session. Supply a continuation prompt when the authorized move should resume automatically. For a child checkout use `delegate_task` isolation; for a user-requested new top-level thread use the launch tool's workspace binding. Do not approximate these with shell-created worktrees.

## Show and deliver

Use the current host's artifact rules. For requested inline visuals or data trends/comparisons, prepare self-contained HTML, call `html_preview`, inspect its image/console/height, correct issues, then `html_render`. Do not start a server or treat webpage tools as a presentation mechanism. Follow the renderer's live theme, sizing and local-image contract rather than copying a stale stylesheet. A generated/exportable image requested for use elsewhere is a PNG file with its path, not an inline HTML substitute.

Use exact absolute paths for existing files and the host's upload/attachment flow when needed. Successful upload or send means delivery accepted, not proof a model read it. Preserve evidence before closing owned sessions. Do not manufacture a screenshot or URL for an artifact that does not exist.

For credentials, call `request_secret` yourself. Pass its one-use `secretRef` to a compatible tool; for shell-only consumption use its supported private-file delivery. Do not ask the user to paste a token into ordinary chat, expose its value, or pass it in an agent brief.
