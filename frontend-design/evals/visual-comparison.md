# Comparing frontend skill revisions

Use when evaluating the skill, not as a mandatory step in ordinary UI work.
`scenarios.json` contains decision exercises and two `mode: visual` briefs.
Decision answers alone do not establish rendered design quality.

## Controlled build

1. Identify baseline and candidate skill revisions or exact content hashes.
   Decide the cases and criteria before inspecting results; include an unseen
   brief when tuning from previous failures. Preserve prompts and raw artifacts.
2. Give the same brief to separate fresh sessions with the same model, effort,
   tool availability, time/token allowance, stack, starting files, and data. Load
   the appropriate skill version and relevant references, withholding scoring
   expectations and the other variant. Use temporary projects; do not modify a
   live product, native skill installation, or customer data for an experiment.
3. Build the same requested deliverable in each condition. Record model/version,
   settings, commands, failures, tool availability, and any meaningful differences
   in execution or revision effort. Static HTML is acceptable when the brief
   requests it; do not invent a backend, build tool, imagery, or claims.
4. Render the final artifacts with the same capture tool, routes, viewports,
   theme, state, scale, and asset/font availability. Use at least a narrow and a
   wide view for a responsive brief and capture relevant data states. Build
   output is the target when the project has one. Record unavailable captures
   rather than substituting an unexecuted pass.

## Blind assessment

- Randomize opaque labels and presentation order separately from the condition
  mapping. Give the reviewer screenshots and the shared brief, not skill files,
  build notes, scoring expectations, provenance labels, or the condition map.
  Include all captured variants and relevant lower-page views. Record whether
  the reviewer is a model or a person; never call a model score human approval.
- Judge factual/brand fidelity, task visibility, hierarchy, content completeness,
  data-state meaning, responsive geometry, and appropriate motion separately.
  Name visible defects with image locations. Use equal criteria for both sides;
  do not reward novelty, image/animation counts, or a prescribed layout.
- Report observed defects separately from aesthetic preferences. Allow a tie,
  different strengths, or neither variant meeting the brief. A prettier render
  does not compensate for invented proof, lost content, or a wrong data meaning.
- Screenshots do not establish interaction, reduced-motion behavior, keyboard
  access, source rights, or arithmetic not visible there. Assess those from
  separate tool/source evidence without pretending the screenshot proves them.
  A static screenshot of an animation is not a motion test.
- A table extending beyond a narrow capture may have intentional contained
  scrolling. Record the visible crop or weak scroll affordance; verify scrolling
  and access to offscreen cells separately before calling data unreachable.

## Record and interpret

Keep the condition map separate until assessment is complete, then record the
predefined criteria, exact checked inputs, reviewer outputs, ties/regressions,
and unexecuted checks. Prefer the project's existing evaluation artifacts or an
explicitly requested report over creating new documentation in the tested app.

Separate image identity from condition identity: supplied product names and
required labels remain visible, but folder names must not reveal which skill
was used. A small single-run comparison can expose a failure; it cannot prove
general superiority or a stable improvement rate. Add independent briefs or
repeat runs when that uncertainty matters, instead of silently recycling the
same tuned examples or counting lint findings as user preference.
