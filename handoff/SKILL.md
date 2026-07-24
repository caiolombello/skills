---
name: handoff
description: Create a paste-ready continuation briefing when the user asks to hand off, conclude, transfer, resume in a new conversation, or preserve session context. Capture verified state, changed files, pending work, blockers, and safety constraints without exposing secrets.
---

# Handoff

Produce a concise briefing that another Codex session can use without reading the full conversation.

Before writing it:

1. Inspect the current workspace, Git status, and relevant diffs when available.
2. Reconcile observed state with claims made in the conversation.
3. Separate completed, pending, blocked, and unverified work.
4. Exclude secret values, credentials, tokens, private keys, and unnecessary transcript content.

Use this structure:

## Current state

State the concrete outcome first, including repository, branch, commit, deployment, or incident status when relevant.

## Changes

List every file created, edited, or deleted and summarize the behavior changed.

## Verification

List commands run and observed results. Explicitly identify checks that were skipped, failed, or remain uncertain.

## Pending work

Give ordered next actions, blockers, owners, and decisions still required.

## Essential context

Preserve constraints, assumptions, risks, commands, identifiers, and boundaries the next session must not lose.

Keep the output paste-ready. Do not claim work is complete unless verification supports it.
