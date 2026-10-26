---
name: blog-posting
description: "Use when writing, editing, or rewriting a blog post or article: drafting from a topic or notes, humanizing a draft so it reads human-written (humanizar um post), or a pre-publish editing pass. Not for READMEs, technical docs, or code."
---

<!-- Informed by public AI-humanizer skills and writing guides on burstiness; independently written. See ../CREDITS.md -->

# Blog posting

Write posts a reader believes a person wrote. That is the bar, and the honest version of it: the goal is writing good enough that readers trust it, not text tuned to fool a detector. Most AI-sounding drafts fail on three fronts at once: stock vocabulary, template structure, and no stakes. Fix all three, or the draft still reads generated.

## When to use

- Draft a new post from a topic, a brief, or rough notes, in English or Portuguese.
- Rewrite, humanize, or de-slop an existing draft (the user's own or a model's).
- Final pass before publishing: rhythm, tells, facts, title.
- Turn a transcript, thread, or internal document into a publishable post.

## When not to use

- READMEs, CHANGELOGs, docs, runbooks. Those are reference material; clarity beats voice, and [`no-docs-unless-asked`](../no-docs-unless-asked) owns the reflex.
- Commit messages and PR text ([`git-hygiene`](../git-hygiene), [`pr-workflow`](../pr-workflow)).
- Social-media copy and one-line captions. Short copy has its own register.
- Academic or legal documents with a required format.

## The workflow

### 1. Intake

Gather only what changes the output. Ask at most three questions, default the rest, and state the defaults you took.

- Reader and platform. Who, where, what they already know.
- Goal. Rank, teach, persuade, announce, entertain.
- Angle and the writer's real take. The opinion is the voice; a post without a stance is a summary.
- Raw material. Notes, links, numbers, quotes, screenshots. The post is built from these, not from the topic alone.
- Length and format.
- Voice. A previous post, or five to ten sentences of the writer talking about the subject.

Never fabricate experience. If there is no personal material, write from research with attribution, and list the spots where the author's own detail would add most. In the delivery note, not as bracketed placeholders in the text (those get published by accident).

### 2. Voice capture

From the sample, write down five to eight rules you can check a draft against: contractions or not, typical sentence length, humor, how much opinion, pet constructions, formality. No sample available? Ask for one paragraph in the writer's words, or pick the register the platform implies and say so in the report.

Extraction checklist: [references/human-voice.md](references/human-voice.md).

### 3. Draft like a person

- Lead with the point. A first draft that clears its throat is normal; the anti-tell pass cuts it.
- Write to one specific reader, not to an audience segment.
- Take a position. Blogs are voice pieces.
- Structure follows the argument. Headers are statements, questions, or short commands, not "Understanding X".
- Prose by default. A list only when the post's promise is the list.
- Every section carries at least one concrete: a number, name, date, tool, price, error message, quote. No concrete in a section usually means the section is filler.
- Vary sentence length on purpose. Long is fine. So is a fragment.
- Stop when done. No recap chapter, no "final thoughts".

Format skeletons and per-format failure modes: [references/blog-formats.md](references/blog-formats.md).

### 4. The anti-tell pass

Tells are statistical. One "crucial" is a style choice. A pattern is a tell. Fix in this order: structure, then substance, then words. A synonym swap on template text still reads templated.

1. Cut the first two sentences and the closing recap section. Restore only what carried real content.
2. Run the lint. Replace `<skill-dir>` with this folder's absolute path (for example `~/.agents/skills/blog-posting`), which is not an environment variable:
   `python3 <skill-dir>/scripts/blog_lint.py post.md`
   Fix every error. Review each warning. Keep one only when it is deliberate voice, and say so.
3. Restructure before rewording. Merge template sections, reorder for the argument, break uniform paragraph rhythm.
4. Add the missing concretes. For each abstract claim, ask "such as?" up to three times.
5. Words last, in context. Keep a precise word even when listed here, if it is the right word. Kill the pattern, not the vocabulary. Mechanically swapping a long blacklist for "safe" synonyms makes text blander, not more human.
6. Read the post aloud, or run it in your head sentence by sentence. Rewrite any sentence you cannot say in one breath or would not say out loud.

Full catalog with per-language rewrites: [references/ai-tells.md](references/ai-tells.md).

### 5. Verify and deliver

- Lint: zero errors. Every remaining warning is deliberate and listed.
- Facts: numbers, names, quotes, and links checked at the source. Nothing invented.
- No fabricated experience. Author-insertion points listed in the delivery note.
- Read-aloud pass done.

Deliver the file path plus a short note: what was verified, what remains risky, where the author's own material would add most.

## Humanize mode (rewriting an existing draft)

- Diagnose first. Run the lint, read the draft once, and list the actual tells before rewriting anything.
- Preserve every fact, name, number, quote, technical term, and claim. Add none.
- Keep the author's good sentences: their jokes, their word choices, their structure. Humanizing must not erase the human. When the draft is the user's own writing, this is the top rule.
- Length within about 10% unless asked otherwise.
- No quirkiness theater. Fake typos, random capitals, forced slang, and injected "burstiness" are their own tell. Vary rhythm by reading aloud, not by sprinkling short sentences at random.
- Be honest about detectors. No tool or workflow guarantees a pass, and chasing scores makes writing worse. The goal is text a reader trusts.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Synonym-swapping the flagged words | The template structure and empty claims still read generated |
| Applying a long blacklist mechanically | Precise words get replaced by weaker ones; blander, not more human |
| Invented anecdote, stat, or experience to "add voice" | One fact-check destroys trust; worse than a plain post |
| Deliberate errors and forced slang | Quirkiness theater is itself a recognizable pattern |
| Recap section at the end | The closing recap is the single strongest tell |
| Making everything a list | Lists dump items; prose carries an argument |
| SEO boilerplate bolted on ("Key Takeaways", numbered H2s) | Template signals; write the title and one honest meta description instead |
| Chasing AI-detector scores | Optimizes the wrong metric and degrades the text |

## Interaction with other skills

- [`no-docs-unless-asked`](../no-docs-unless-asked): blocks unrequested docs. A requested blog post is this skill's job, a README is that skill's boundary.
- [`git-hygiene`](../git-hygiene): commit and PR text follows its conventions, not blog voice.
- [`verification-before-completion`](../verification-before-completion): the verify step above applies the same evidence bar.

## Verification checklist

- [ ] Intake defaults stated; nothing asked that the draft could not change.
- [ ] Voice rules captured, or the chosen register reported.
- [ ] Each section has at least one concrete; author-insertion points listed, not bracketed in text.
- [ ] `blog_lint.py` reports zero errors; remaining warnings are deliberate and listed.
- [ ] Facts, numbers, quotes, and links verified at the source; nothing invented.
- [ ] Read-aloud pass done; no sentence survives that you would not say out loud.
