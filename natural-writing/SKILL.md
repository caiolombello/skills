---
name: natural-writing
description: "Use when drafting or humanizing prose for people, including messages, emails, group notices, reports, and assistant replies. Match voice and register; preserve facts, exact text, and output contracts."
---

# Natural Writing

Write something the intended speaker would actually say to the intended reader. Apply this to copy-ready writing and ordinary assistant prose. Natural does not always mean casual; a respectful group notice can be direct without sounding like a memo from a legal department.

## Scope and precedence

- Use for personal messages, workplace chat, emails, group notices, captions, and natural-language answers. For an explicit request to humanize other prose, apply the same editing pass within that document's constraints.
- For posts and articles, let [`blog-posting`](../blog-posting/SKILL.md), when available, own research, structure, and publication requirements. These voice rules can complement it; do not turn a short message into an article.
- Preserve exact quotes, required wording, code, commands, identifiers, schemas, and strict JSON or other output contracts. Do not apply voice editing inside them. Minor literal corrections do not need a writing workflow.
- Follow the current request over general defaults. Do not rewrite a formal document into chat or add a greeting where the requested format has none.

## Establish speaker, reader, and purpose

Infer them from the request and the supplied conversation before asking anything. Distinguish an assistant answer from text written on the user's behalf. Never import the user's first-person identity or personal experiences into an assistant answer.

For copy-ready writing, identify what the reader needs to know or do, the relationship, the channel, and any stated tone. Ask a focused question only if a missing fact materially changes the message. A routine reply should not require an intake form or a writing sample.

## Match voice using actual evidence

Start with the user's current draft and relevant user-authored examples already provided for this task. A sample from the same medium and audience is more useful than a polished article in an unrelated register. Do not treat assistant replies, forwarded text, or other people's messages as the user's voice.

When personal style matching would help and `write-like-me` is available, follow that skill's retrieval workflow. It supplies evidence for voice, not facts for the new message. This skill works without that plugin. Do not search unrelated apps or private files to build a voice profile, persist retrieved samples, or claim to match a voice you have not inspected.

Pick only the traits that matter: directness, formality, sentence shape, contractions, vocabulary, warmth, greeting and sign-off. Keep this analysis internal. Sparse chat samples do not establish how the user writes a formal email. Without suitable evidence, use a clear register suited to the recipient and follow explicit preferences.

## Draft to the situation

- **One-to-one conversation:** answer the actual message with the minimum useful context. Keep warmth proportional to the relationship. Do not add an email-style salutation, sign-off, or repeated name by habit.
- **Group announcement:** make the change, timing, audience, and requested action clear when supplied. Use ordinary professional language. Keep formality moderate unless the request calls for more.
- **Email or formal communication:** be respectful and specific without ceremonial filler. Preserve a necessary subject, greeting, closing, or required wording.
- **Assistant answer:** lead with the useful answer and explain as much as the task needs. Keep technical precision, evidence, and uncertainty. Use lists or headings when they help comprehension, rather than dressing every answer in the same template.

Use the language and regional variant requested or evident in context. In Brazilian Portuguese, do not automatically add abbreviations such as "vc", "tb", "pra", emojis, or slang. Match those only when they suit the speaker, audience, and instruction. In English, do not force contractions or fragments to simulate personality.

For calibrated examples, read [references/register-and-examples.md](references/register-and-examples.md) when the channel or formality is unclear.

## Edit for naturalness without changing the message

1. Preserve intent and substance. Keep who does what, deadlines, amounts, names, links, conditions, refusals, uncertainty, and the strength of commitments. "I can try" must not become "I'll deliver". Do not soften a clear boundary into optional advice.
2. Remove filler that does no work: generic praise, stock openings, corporate abstractions, announced structure, padded conclusions, and offers of further help added by habit. Keep a courtesy or recap when it serves this reader.
3. Replace formulaic contrasts such as "não é sobre X, é sobre Y" and repeated "not only... but also" with the actual claim when the contrast adds nothing. Keep meaningful comparisons, emphasis, and precise vocabulary.
4. Avoid em dashes, en dashes, double hyphens, and spaced hyphens as sentence connectors in newly written prose. Use a period, comma, colon, or a rewritten sentence. Preserve required hyphens in words, negative values, ranges, URLs, code, and exact quotations. Never globally delete punctuation. If every dash character is explicitly forbidden, rephrase prose while preserving protected literal content or raise the conflict.
5. Remove repetitive openings, repeated summaries, symmetrical lists, and unnecessary bold labels when they make the writing feel manufactured. Do not impose arbitrary sentence lengths, paragraph variety, lists, or a quota of short sentences.
6. Keep the author's good wording. Editing may mean changing almost nothing. Do not add fake typos, false intimacy, forced humor, dramatic fragments, invented feelings, opinions, anecdotes, measurements, or citations.

For translations, preserve meaning and factual details, localize idiom and register, and keep exact names, dates, amounts, and identifiers. Rewriting is not permission to change the examples or the underlying claim.

## Deliver and check

For a message the user will copy, return the message itself in plain text with useful line breaks. Omit "Here's a more human version", quote wrappers, code fences, alternatives, and editorial notes unless requested or needed to resolve a material issue. If asked for analysis or a review, include it in the requested format. Drafting is not permission to send or publish.

Before returning it, compare against the source for facts and commitments, read it as the recipient, and remove any remaining habitual sentence dashes or empty formulas. A short natural reply can be one sentence. A complex explanation can be long. No detector score, word blacklist, or punctuation count proves that prose is human.

## Interaction with other skills

- `write-like-me`, when installed: retrieves relevant personal writing; use its evidence without inventing a voice or copying old facts. Do not modify plugin caches or duplicate that skill under its name.
- [`blog-posting`](../blog-posting/SKILL.md): specializes in posts and articles. Use this skill for reusable voice and editing decisions.
- Document, PR, and technical workflows own their required structure and validation. Improve surrounding prose without breaking their contracts.
- [`technical-writing`](../technical-writing/SKILL.md) owns developer-document purpose, organization and usable examples; this skill retains voice and register. Do not impose that workflow on an everyday message.

Installation makes this skill available for selection; it does not guarantee invocation on every turn. If an always-applied writing preference is requested, put a short preference in the applicable rules file through that file's normal workflow. Do not silently change global instructions while installing a skill.
