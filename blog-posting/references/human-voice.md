# Human voice

The positive half of the work: what human writing does that slop does not. The negative half (what to cut) is [ai-tells.md](ai-tells.md). Use this file for voice capture in step 2 and for the substance pass in step 4 of the workflow.

## The honest goal

"Human" does not mean quirky, and it does not mean undetectable. It means: a reader with real stakes (their time, their money, their pager) finishes the post believing a person wrote it, because the post knows things and takes positions. Chasing detector scores produces worse text than either honest writing or honest AI assistance.

## Substance first

Slop is 50% emptiness. Before touching a word, make sure every claim has a body.

The specificity ladder. Each rung is more work to fake and easier to trust:

1. "Improves performance" (nothing)
2. "Improves cold starts" (a direction)
3. "Cut cold starts from 1.2s to 300ms" (a measurement)
4. "Cut cold starts from 1.2s to 300ms by lazy-loading the SDK" (a mechanism)
5. "Cut cold starts from 1.2s to 300ms by lazy-loading the SDK, which took one afternoon and broke file uploads for a week" (a lived story)

Aim for rung 3 everywhere and rung 5 where it matters. For each abstract claim, ask "such as?" up to three times.

## Stakes and opinion

- A post with no stance is a summary. Say what you would pick and why.
- Disagree with something: a tool, a best practice, a popular take. One real disagreement beats three balanced "it depends".
- If the honest position is uncertainty, say what you would bet on and with what confidence. "I don't know why this works, but it does" is a human sentence.
- Costs and trade-offs: name the price you paid. What broke, what it cost, how long it took.

## Anecdotes and experience

- Real anecdotes do the heavy lifting of credibility. But never invent one. A fabricated story that collapses under one question is worse than no story.
- Insertion-point protocol when the author's material is missing: note in the delivery report where a two-sentence anecdote would strengthen the post ("after the section on retry storms, a war story about your last one"). Not bracketed placeholders in the body text; those get published by accident.
- When writing from research only, attribute clearly and let the post be useful without a persona: "The PostgreSQL docs are blunt about this..." is fine.

## Rhythm

Human writing has high burstiness. Sentence length swings: a four-word sentence next to a forty-word one. Model prose clusters in a narrow band, which is why uniform length is the quietest tell.

- Vary on purpose. Long is fine. So is a fragment. "It broke." "Two reasons."
- One-word answers to your own rhetorical structure, used sparingly.
- The read-aloud protocol: read the draft sentence by sentence (out loud, or fully voiced in your head). Rewrite anything you cannot finish in one breath, and anything you would not say to a colleague at a whiteboard.
- Do not inject "burstiness" mechanically (sprinkling random short sentences). Vary the rhythm by merging and splitting where the meaning actually breaks.

## Asides, self-interruption, direct address

- Parenthetical asides (like this one) carry the voice of a person thinking while writing.
- Self-interruption: "which, honestly, surprised me too".
- Direct address is earned by knowing the reader: reference shared context they actually have ("you already have the metrics endpoint"), not generic "as a developer, you know how challenging it can be".
- Humor that risks falling flat is a human marker; gentle universal quips are not.

## Voice capture procedure

From a voice sample (a past post, or five to ten sentences of the writer talking about the subject), extract five to eight checkable rules:

1. Contractions: yes / no / situation.
2. Sentence length: short-burst, long-form, or mixed. Evidence: typical range.
3. Opinion density: how often they take sides, how strong.
4. Humor: dry, overt, absent. Do they joke about themselves?
5. Pet constructions: catchphrases, recurring metaphors, a preferred way to open sections.
6. Formality and slang: "kind of", "sorte de", "meio que", or none.
7. How they address the reader: "you", "we", "nós", named reader?
8. Punctuation habits: em dashes, ellipses, exclamation marks, none.

Write the rules down before drafting (they go in the report when there is no sample, as the chosen register). During the anti-tell pass, check the draft against them. When humanizing the user's own draft, their existing sentences outrank every rule in this file.

## Register by platform

| Platform | Register | Notes |
|---|---|---|
| Personal blog / Substack | First person, opinions, stories | Longest leash on rhythm and asides |
| Company engineering blog | First person plural, evidence-heavy | Keep voice; cut slang; keep numbers and mechanisms |
| Dev.to / Hashnode | Direct, tutorial-friendly | Keep one personal thread through the how-to |
| LinkedIn article | Restrained, concrete | Shorter sentences; no emoji headers; still no slop |
| Ghost / newsletter | Conversational | Write like the subscriber knows you |

## Translation (PT-EN / EN-PT)

A translated post inherits the source's tells and adds its own calques. When the job is translation plus humanizing:

- Translate meaning, not structure. A sentence that was slop in English does not deserve a faithful rendering.
- Avoid calques: "deep dive" as "mergulho profundo" in PT, "na prática" as "in practice" used as filler in EN.
- Keep idioms on the target side, not the source side ("mão na massa" stays PT; "hit the ground running" stays EN).
- Localize examples when the audience differs: prices, tool names, default stacks.

## Do not

- Fake errors, deliberate typos, random capitals: quirkiness theater, itself a pattern.
- Uniform contractions or uniform anything: variance is the point.
- Blanket-replace every flagged word: precision loses, blandness wins.
- Add opinions the author does not hold; when humanizing their draft, preserve their positions exactly.
