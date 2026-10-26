# Blog formats

Choose a format that serves the brief and evidence. The skeletons below are options, not a mandatory sequence. Per-format: skeleton, credibility requirements, and the specific way AI drafts of that format fail. Voice and editing are covered in [natural-writing](../../natural-writing/SKILL.md), [human-voice.md](human-voice.md), and [ai-tells.md](ai-tells.md); this file is about shape.

## How-to / tutorial

Promise: the reader can do X after the post.

Skeleton: what you end up with (screenshot or result first) → prerequisites with versions → steps in the order a first-timer hits them → the step where it usually breaks → how to verify it worked → what to do next.

Credibility: verified commands, actual output when available, versions, and sourced failure modes. Do not claim to have hit a problem personally without supplied experience.

AI failure: generic steps ("configure your settings appropriately"), no commands or with invented flags, and a "Common Pitfalls" section of strawmen. If steps cannot be run, source them and disclose the verification limit rather than implying a tested walkthrough.

## Opinion / argument

Promise: a position, defended.

Skeleton: the claim, in the first paragraph, stated strongly enough to be wrong → the evidence (numbers, cases, comparisons) → the strongest counterargument, fairly stated → why you still hold the claim → the conditions under which you would change your mind.

Credibility: a real disagreement with a real target (a tool, a practice, a popular post), and the author's skin in the game (what they built or lost with this opinion).

AI failure: both-sides mush ("ultimately, it depends on your needs"), a claim so hedged it asserts nothing, or an opinion with no author anywhere.

## Experience report ("I did X for N days")

Promise: what actually happened.

Skeleton: the setup and stakes (why you tried this) → what you expected → what happened, in time order, with dates → the numbers → what you would do differently → who should try this.

Credibility: dates, numbers, named tools, and at least one thing that went wrong. A report need not include a failure when none was supplied; do not invent one for credibility.

AI failure: a story with no specifics and no failure; "the results were surprising" without the surprise stated.

## Comparison / "X vs Y"

Promise: which one, for whom.

Skeleton: the axis that actually matters for the reader's job (name it) → the comparison on that axis with numbers → the axes people cite but you found irrelevant → the verdict, per reader type → what you would pick today.

Credibility: hands-on or attributed evidence for both sides. State whose benchmarks or costs are used and their limits; do not imply tests the author did not run.

AI failure: a feature-table tie and a non-verdict ("both are excellent choices depending on your needs"). The whole point of the post is the verdict.

## News reaction / analysis

Promise: what this means, not what happened.

Skeleton: the news in two sentences (link out) → what most coverage gets wrong → who wins and who pays, concretely → what to watch next → what you would do about it this month.

Credibility: the primary source, checked; relevant author experience only if supplied.

AI failure: a rewritten press release with "This development is a significant milestone" energy, no analysis, and an invented quote.

## Listicle

Promise: the list IS the content, and the title quantified it ("7 mistakes", "5 tools").

Skeleton: the filter that defines the list (what qualified, what didn't) → the items, each with a concrete example and the one thing most posts omit → the item that almost didn't make it (a real judgment call).

Credibility: every item earns its slot; the ordering reflects an actual opinion.

AI failure: padded items to reach a round number, one-sentence items with bold leads, and a list that exists because listicles rank. If you only have four, the title says four.

## Announcement / release note post

Promise: what shipped, and why it matters to the reader.

Skeleton: the one-line what → the reader's before/after → the migration or breaking bit, stated plainly → the numbers if any → what is next.

Credibility: the actual changelog, real limits ("does not yet work with...").

AI failure: adjectives instead of user effects ("a faster, more seamless experience"), and no breaking-change honesty.

## Interview / Q&A

Promise: a person's actual answers.

Skeleton: who they are, in one specific line (not "a leading expert") → the questions the audience would ask → follow-ups that chase the vague answer ("you said 'interesting problems'; which one specifically?").

Credibility: quotes you can verify against the recording; disagreements kept in.

AI failure: long summaries of questions, uniform answer lengths, and every answer polished into mush.

## Title and meta description

Write last, when the post's actual promise is known.

- Title: the specific promise, with a number or a named outcome where honest. Not "The Ultimate Guide to X".
- Meta description: one honest sentence about who the post is for and what they leave with, not a keyword list.
- Slug: short, stable, lowercase, following the platform's convention. Preserve required URL hyphens.
- Match the publication's heading structure. Use a table of contents or recap only when it helps readers; numbered tutorial steps are appropriate.
