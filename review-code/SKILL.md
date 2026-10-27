---
name: review-code
description: "Compatibility entry point for reviewing code just written or changed. Use code-review for the review policy and receiving-code-review for authorized corrections."
---

# Review Code

This existing skill name remains available as a compatibility entry point. Read and follow [`code-review`](../code-review/SKILL.md); do not run a second duplicate review if that skill was already applied to this artifact.

If the canonical skill is unavailable in an isolated install, inspect the requested change proportionally to risk, report only supported material findings with real file/line and failure scenario, and separate introduced defects from pre-existing issues and uncertainty. State the limit instead of inventing a completed independent review. A clean result means no actionable findings in the inspected scope, not guaranteed correctness.

Use [`receiving-code-review`](../receiving-code-review/SKILL.md) when the user authorizes addressing feedback. This alias does not authorize edits, commits, external comments, or merge.
