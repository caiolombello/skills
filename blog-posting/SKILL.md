---
name: blog-posting
description: "Use when drafting or editing blog posts and articles: audience, angle, evidence, structure, and publication checks. For messages and everyday prose, use natural-writing."
---

<!-- Informed by public AI-humanizer skills; independently written. See ../CREDITS.md -->

# Blog posting

Write a useful article with an identifiable purpose, supported claims, and a voice suited to its author and readers. Preserve facts and the author's good writing when editing. Naturalness is an editorial judgment, not a detector score or a word-count formula.

## Scope

Use for a new post, an article made from supplied notes, or a substantial edit of an existing post in English or Portuguese. A short announcement, personal message, email, caption, or ordinary assistant reply belongs to [`natural-writing`](../natural-writing/SKILL.md).

Required document formats, technical documentation, PRs, and exact text keep their own contracts. A blog request authorizes drafting, not publishing, sending, or creating unrelated files.

## Establish the brief

Use the existing request and material to infer reader, platform, purpose, angle, length, and voice. Ask only for missing information that would materially change the post. Do not require a questionnaire or a voice sample when a useful draft is possible.

Distinguish the author's evidence and views from source material. An explainer can teach without a personal stance; an opinion piece needs an actual position. Never invent an opinion or personal experience to fill an empty brief. If the format depends on missing experience, ask for it or suggest a research-based format.

For voice matching and general prose editing, use [`natural-writing`](../natural-writing/SKILL.md) when available. It can use `write-like-me` if installed, or supplied examples without that plugin. If the general skill is absent, preserve the author's draft, match the requested register, avoid sentence-connecting dashes and filler, and keep facts and commitments intact. [references/human-voice.md](references/human-voice.md) adds article-specific guidance on evidence and voice.

## Draft or revise the argument

- Start where the reader needs to start. Cut a generic setup, not an arbitrary number of sentences. Keep a useful opening or a scene supported by the brief.
- Choose the shape that fulfills the post's promise. [references/blog-formats.md](references/blog-formats.md) offers options, not mandatory skeletons.
- Prefer precise explanations and available evidence over abstract adjectives. Do not require a number, anecdote, disagreement, or named tool in every section. If detail is unavailable, narrow or qualify the claim; never manufacture it.
- Let headings and lists help navigation. A tutorial may need numbered steps, a comparison may need a table, and a long post may earn a recap. Remove them when they repeat the text or impose a generic essay structure.
- Preserve the meaning, useful sentences, and degree of certainty of the source. Do not silently change dates, prices, examples, recommendations, or technical terms while translating or editing.
- Avoid em dashes, en dashes, double hyphens, and spaced hyphens as sentence connectors in newly written prose. Preserve grammatical hyphens, code, URLs, ranges, negative numbers, and exact quotations. Respect an explicit request for a different style.
- Read for repetition and pacing. Split or join sentences when meaning calls for it, without chasing sentence-length variance or injecting fragments.

For a draft dense with stock language, consult [references/ai-tells.md](references/ai-tells.md). Review structure and unsupported claims before vocabulary. An unusual word, a real contrast, or a conventional heading is not automatically a defect.

## Optional diagnostic

For a substantial post saved to a file, the bundled lint can surface phrases and repeated structures for review:

```sh
python3 /path/to/blog-posting/scripts/blog_lint.py post.md
```

Replace `/path/to/blog-posting` with this skill's directory. The command is read-only. Its findings are advisory; it does not detect AI authorship, verify facts, or prove quality. Keep a justified word or structure rather than rewriting to reach zero findings. Use `--strict` only when an explicit workflow wants a nonzero exit code for advisory findings. No script or temporary file is necessary for a short inline edit.

## Verify and deliver

Check new externally sourced facts, numbers, quotations, and links against their sources. For an editing-only task, preserve supplied claims and distinguish anything not independently checked; do not silently certify it. Keep necessary attribution in the post. Raise a material factual problem separately rather than hiding it in a stylistic rewrite.

Return the requested post, usually inline and without an editorial preamble when the user wants copy-ready text. Provide a file only if requested or appropriate to the established workflow. Include a short separate note only when needed for unresolved facts, missing author input, or requested review detail. Avoid placeholders that could be published by mistake; a complete draft must not depend on invented facts.

Before delivery, confirm that the title promises what the post supplies, claims match the evidence, the author's voice and certainty survived, and no punctuation or stock phrase remains merely by habit. A recap, courtesy, or list can stay when it earns its place.

## Interaction with other skills

- [`natural-writing`](../natural-writing/SKILL.md) owns cross-format voice, register, and the naturalness pass. This skill adds article structure, evidence, and publication checks. Keep both roles distinct.
- `write-like-me`, when available, supplies real style references through its own workflow. It is optional, not a dependency to duplicate or a license to reuse old facts.
- [`git-hygiene`](../git-hygiene/SKILL.md) and [`pr-workflow`](../pr-workflow/SKILL.md) own commit and PR formats; do not apply article formatting to them.
