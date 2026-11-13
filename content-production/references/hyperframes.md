# HyperFrames for code-based video

Source reviewed at [f01209d4aebf8768aca5cd2d0f8c2130cc51b423](https://github.com/heygen-com/hyperframes/tree/f01209d4aebf8768aca5cd2d0f8c2130cc51b423), CLI package 0.9.42 (Apache-2.0, HeyGen). This is a source/documentation assessment, not a tested installation on this machine.

## When it fits

HyperFrames renders HTML compositions to video by seeking a paused timeline frame by frame, so the same source produces the same frames. It suits motion graphics an assistant can write and revise as code: product explainers, launch films, animated charts and type, title cards, captions and overlays over existing footage, and vertical cuts. It is not a generative footage model, a screen recorder, or a replacement for a full editor when the work is mostly cutting real footage; see [tools and budget](tools-and-budget.md) for the route choice.

## Prerequisites and boundaries

- The CLI documents Node.js 22+ and FFmpeg, plus a local Chrome for rendering. Check `node --version`, `ffmpeg -version`, and `npx hyperframes doctor --json` (it exits 0; gate on its `ok` field). Do not install Node, FFmpeg, browsers, or the CLI globally unasked.
- `npx hyperframes` downloads and runs package code. Pin the version the project already uses; treat upgrades like any dependency update.
- **Telemetry.** The upstream skill tells agents to run a usage "beacon" command at start; the CLI's telemetry can be linked to a signed-in account. Do not send it on the user's behalf. Mention `npx hyperframes telemetry disable` when the user cares about privacy, and run it only on request.
- **Accounts and paid features.** Local `render` is documented without a paid plan. `cloud render`, `share`/`publish`, HeyGen avatar or voice generation, and the Pro features (`reverse-any-video`, `style-sampling`) involve an account, upload, or plan. Apply the cost and authority rules in [SKILL.md](../SKILL.md); never run billing or upgrade commands.
- Remaking another creator's video is a rights question before it is a technical one. Rebuild only material the user owns or is authorized to adapt.
- The upstream repository ships its own agent skills; they are optional. Do not run its `skills add ... --all` installer from inside a HyperFrames checkout, which upstream warns can delete the checkout's `skills/` contents.

## Composition contract (summary)

Verify details against the installed version's docs; these were stable in the reviewed snapshot:

- `index.html` is the root composition; scenes live in `compositions/`, media and fonts in `assets/` with relative `assets/...` paths.
- Every timed element is a `.clip` with `data-start` and `data-duration` in seconds; the root's `data-duration` is the video length.
- Each composition registers one paused timeline (GSAP is the primary adapter).
- Determinism: no `Date.now()`, unseeded `Math.random()`, network fetches, timers, or infinite repeats at render time. Everything visible is a function of timeline time.
- Animate transforms and opacity, not `left`/`top`/`width`/`height`; do not tween `display` or `visibility` on a clip.
- Media playback is driven by the timeline, never by `play()`/`pause()`. Separate music, voice and replacement audio into `<audio>` elements with ids.
- Fonts other than the bundled set need `@font-face` to a local file; check the font license.
- Keep copy, brand colors and swappable media as variables so later revisions are small edits.

## Working loop

1. For an existing project, read its timeline (`timeline --json`) and recent history before changing it; build on the person's own edits.
2. For a new film longer than a few seconds, agree on the storyline and a short spec (duration, aspect, scenes, on-screen text, audio) before building; reuse the edit-map discipline from [video editing](video-editing.md).
3. Before hand-writing a named effect, check the project's registry/components (`catalog`, `add`) for an editable block.
4. After the last edit: `npx hyperframes lint` and `npx hyperframes check --json`; fix every error and weigh warnings. Take snapshots of what changed and look at them.
5. Render a draft locally (`render --quality draft -o draft.mp4`), then the delivery quality only after the preview is approved or the user asked for the file without stops.
6. Inspect the encoded output, not just the exit status: non-empty file, `ffprobe` duration equal to the root duration, dimensions/fps, audio presence, and decoded frames at the opening, transitions and ending. The [media probe](../scripts/probe_media.py) helps with metadata.

## Motion craft

Upstream's internal motion guidance is opinionated; these points transfer to any code-motion tool:

- Treat a multi-scene video as one continuous movement: the direction an element exits suggests how the next scene enters.
- Motion should explain a change or carry attention; avoid idle wobble or looping decoration.
- A brief stillness before a key reveal makes it land.
- Keep text and key content inside safe areas (about 90% action-safe, 80% title-safe) and legible at the delivery size.

## Sources

- [Repository](https://github.com/heygen-com/hyperframes/tree/f01209d4aebf8768aca5cd2d0f8c2130cc51b423) and [license](https://github.com/heygen-com/hyperframes/blob/f01209d4aebf8768aca5cd2d0f8c2130cc51b423/LICENSE).
- [Documentation](https://hyperframes.heygen.com/introduction), including the CLI telemetry section.
- No HyperFrames source, skills, registry blocks or templates are vendored here.
