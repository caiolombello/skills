# Model Notes

Load when setting up this skill for a specific model or agent, when results are inconsistent across models, or when making the quality bar always-on in a repository. Provider details change quickly; verify against current official documentation before relying on a specific flag or default.

## Contents

- [What every model needs](#what-every-model-needs)
- [OpenAI models in Codex](#openai-models-in-codex)
- [Claude](#claude)
- [Gemini, Cursor, and other agents](#gemini-cursor-and-other-agents)
- [Smaller models and long sessions](#smaller-models-and-long-sessions)
- [No skills runtime](#no-skills-runtime)
- [Always-on in a repository](#always-on-in-a-repository)
- [Measure whether it helps](#measure-whether-it-helps)

## What every model needs

Most of the gap between an average and an excellent UI comes from four inputs, not from the model:

1. **Real material.** Product name, audience, real copy or data, brand assets, and reference screenshots. Placeholder input produces placeholder design.
2. **A committed brief.** Direction, type, color, density, signature, rejected defaults, and out-of-scope items written before code.
3. **Eyes.** The ability to render the UI and look at screenshots (`visual_qa.mjs` plus an image viewer). Without them the model is guessing.
4. **A stop rule.** The definition of done and the critique rubric, so "done" means verified rather than "the code compiles".

## OpenAI models in Codex

- **Invoke explicitly** for UI work: `$frontend-design` (and `$frontend-development` for production code). Implicit selection depends on the description matching the request.
- **Reasoning effort:** start at the model's default (medium for GPT-5.5). OpenAI's GPT-5.4 frontend guidance reports that low or medium effort often yields stronger frontend results than high; raise effort only when a comparison on your own tasks shows a gain.
- **Literal reading:** recent GPT models follow instructions literally and thoroughly. This skill is written as decision rules ("default to X unless the brief says Y"). Avoid adding contradictory absolutes in `AGENTS.md`; phrase extra rules as defaults with exceptions.
- **Give it eyes:** Codex can run `visual_qa.mjs` and inspect the PNGs with its image viewer tool (`view_image`), or you can attach screenshots (`codex -i shot.png`). If image input is unavailable, the audit's text findings still apply; the report must say "visually unverified".
- **Scope control:** some GPT versions write more than the spec asks. The brief's "Out of scope" line and "the smallest complete version" in the prompt keep features from multiplying.
- **References and content:** attach screenshots or a mood board and supply real copy; OpenAI's guidance notes both improve structure and believability.
- **Delivery:** start the dev server after implementation and share the URL; for a static page, share the file path.

Starter prompt:

```text
$frontend-design $frontend-development
Build <screen or page> for <product>. Users: <who>; job: <what they must get done>.
Real content: <copy, data, or file paths>. Brand: <colors, fonts, logo — or "derive from the brief">.
Stack: <existing stack>. Out of scope: <features not to add>.
Write the Brief first, then implement. Done when the definition of done holds and
visual_qa reports no errors at 390px and 1440px; report rubric scores and screenshot paths.
```

## Claude

- Skills load natively (Claude Code reads `~/.claude/skills` or project `.claude/skills`), and Claude reads images, so the screenshot step works as written.
- A known drift after steering away from purple gradients is a cream/beige palette with an editorial serif on everything. The palette check in [visual-direction.md](visual-direction.md#palette-strategy) applies.

## Gemini, Cursor, and other agents

- The skill files are provider-neutral; install them where the agent discovers skills (see the repository's `setup/README.md`).
- If the agent has its own browser tool but cannot run Node, evaluate `scripts/ui_audit.js` in the page and call `__uiAudit()`, then take screenshots with the agent's tool.
- If it cannot view images at all, run the audit and the rubric on code and audit evidence, and label the result visually unverified.

## Smaller models and long sessions

- One screen per task; the brief first; start from `assets/design-tokens.css`.
- Run `ui_lint.py` after each meaningful edit; cap critique loops at two rounds.
- Prefer existing accessible primitives (the project's library, or headless components) over hand-built widgets.
- In long sessions, restate the brief before each new screen so later screens keep the same system.

## No skills runtime

Paste [assets/agents-snippet.md](../assets/agents-snippet.md) into the system or project instructions (ChatGPT projects, API system prompts, IDE rules files) and attach screenshots manually for critique rounds.

## Always-on in a repository

Skills trigger on demand; a project rules file is read every session. To hold every UI change to the same bar:

1. Copy [assets/agents-snippet.md](../assets/agents-snippet.md) into the repository's `AGENTS.md` (read by Codex, Cursor, and many other agents) and/or `CLAUDE.md`.
2. Point its script paths at the installed skill (for example `~/.agents/skills/frontend-design/scripts/`), or vendor the four scripts into the repository (for example `tools/ui-qa/`) when CI or teammates should run them.
3. Add `.ui-qa/` to `.gitignore`.
4. Keep project-specific decisions (brand fonts, tokens file, component library) in the same section so every agent reuses them.

## Measure whether it helps

Judge the skill by results on your own work, not by how thorough it sounds:

1. Pick three to five representative prompts (a dashboard, a form flow, a landing page, a settings screen, a restyle of an existing page).
2. Run each with and without the skill — same model, same reasoning effort, fresh sessions.
3. Run `ui_lint.py` and `visual_qa.mjs` on every result; record error and warning counts.
4. Score the screenshots blind with the [rubric](critique-rubric.md) (shuffle the order; a second model or a person scores).
5. Keep changes that raise the average rubric score without adding errors. For description changes, also run the repository's trigger evaluation.
