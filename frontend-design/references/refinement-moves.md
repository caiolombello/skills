# Refinement Moves

Load this reference when the user asks for a directional change to an existing
interface ("make it bolder", "too busy", "simplify this", "make it production
ready", "the copy is confusing", "fix it on mobile"), or when a review needs a
named next step. Each move is scoped: it changes one target and leaves the rest of
the page, its system, and its behavior alone.

## Rules for every move

1. **Name the target and what stays.** Ask once only when the target is genuinely ambiguous; otherwise state the inferred target and proceed.
2. **Scope is literal.** Do not restyle neighbors, migrate the page to a new direction, or add colors, fonts, radii, shadows, or primitives the system does not own. If the system cannot express the change, name the exact addition and its job, and ask before adding it.
3. **Read the surface intent** (operate, persuade, read, showcase — see the brief in [SKILL.md](../SKILL.md)). The same word means different things on a dashboard and on a landing page.
4. **Preserve substance.** Content, information architecture, routes, behavior, and real proof stay unless the user asked to change them. Ask before replacing factual copy or adding claims.
5. **Prove it on pixels.** Capture comparable before/after views and run the normal render–critique loop on the target.

## Moves

| Move | Use when | Do | Avoid |
|---|---|---|---|
| **Bolder** | A part reads flat or timid relative to what the rest implies | Raise conviction with scale contrast, weight, a stronger crop or image, tighter hierarchy, one decisive color use | Adding effects, gradients, glow, or more decoration; more elements competing for attention |
| **Quieter** | The surface is loud, busy, or tiring | Persuade/showcase: restrain palette, add air, keep the point of view. Operate/read: remove background accents, flatten cards, reduce color and motion until the task leads | Making it generic; removing the one signature detail that gives it identity |
| **Distill** | Clutter, repeated information, competing actions | Inventory every element; remove what does not serve the visitor's job; merge duplicates; reduce variants of type, color, and shape | Hiding necessary controls or state; removing recovery paths |
| **Harden** | The UI only works with perfect data | Test extreme inputs (very long/short text, emoji, RTL, large numbers, 1000+ items), every error class (offline, timeout, 4xx/5xx, validation, permission, rate limit, concurrent edits), and localization (text expansion, date/number/currency formats); design overflow, truncation with access to the full value, and recovery | Truncating essential information without a way to read it; generic "Something went wrong" |
| **Clarify** | Labels, errors, or states confuse people | Read the whole interaction path; say what happened, what it means, and what to do next; use the product's terms consistently; verb + object actions | Changing product terminology or brand voice unasked; inventing facts or guarantees |
| **Adapt** | A design must work on another size, input, or context | Rethink priority, reach, and input for the new context (touch targets, thumb zones, hover-free paths, keyboard) | Scaling the desktop layout down; hiding content only on small screens without an alternative |

For layout, typography, color, and motion fixes, the [craft baseline](craft-baseline.md)
and [component recipes](component-recipes.md) remain the source of the defaults;
these moves only frame the direction and scope.

## Reporting

State the move, the target, what stayed untouched, the evidence (before/after
captures, lint and audit results), and any addition you proposed but did not make.

## Source

Inspired by the steering vocabulary and visitor modes in
[pbakaus/impeccable](https://github.com/pbakaus/impeccable) (Apache-2.0, reviewed
at `c4cd1924c389f68d37c687d9c2bbf13f12547c41`). Independently written; no upstream
text, detector rules, launcher, hooks, or live-editing tooling are included.
