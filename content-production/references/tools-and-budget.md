# Tools and budget routing

Reviewed on 2026-10-27. Verify current availability, capabilities, cost and license for the actual version/account before execution. No fixed price, free quota or provider ranking is maintained here.

| Route | Useful for | Cost/access distinction |
| --- | --- | --- |
| Tool-independent brief/script/storyboard/edit map | Preparing content or handing work to an editor | No media engine needed for text; does not produce encoded video or generated pixels |
| Existing footage + local FFmpeg/ffprobe | Repeatable cuts, assembly, resizing, audio and technical checks | No required paid generation; needs installed binaries/codecs and local compute |
| Kdenlive or another available editor | Interactive timeline edits, titles, captions and mixing | Kdenlive is free/open source; installed GUI/control access is still required |
| Recordly | Screen-recorded product demos/tutorials with cursor/zoom polish | Optional native app; [platform/account limits](recordly.md) must be checked |
| Code motion with an available renderer | Explain product flows, animated typography/charts/diagrams | Reuse HTML/canvas/Blender/Remotion tooling when suitable; code alone is not an export |
| Connected image-generation tool | Raster assets, thumbnails, product visuals | Follow that tool's contract; existing plan usage is different from an external API charge |
| Higgsfield website/connector/MCP/API | Generative clips, product creatives and multi-model workflows | Optional paid/limited access; [billing and integration](higgsfield.md) vary by entry point |
| A directly accessible video provider or local generation stack | Generation without Higgsfield | Check actual tool/API, model license, cost and hardware; do not assume setup/access |

Choose the lightest route that can deliver the required artifact and quality. For a bootstrapped project, a real screen capture, good cuts/captions and a clear story can be more useful than purchased cinematic footage. For a cinematic scene that does not exist, generation or a shoot may be necessary. Match the route to the content, not the vendor name.

## Claude and independent production

Claude can plan, write, direct and generate animation code; its documented Motion product builds code-based animations and exports them, rather than generating realistic footage. Motion availability is account/plan-specific; having a Claude model in another harness does not provide that product or export UI. See [official Claude Motion guidance](https://support.claude.com/en/articles/17454997-get-started-with-claude-motion).

Higgsfield adds media generation and workflow tools to compatible assistants, including Claude through MCP. It is not a prerequisite for writing scripts, local editing, rendering code-based motion, or using another available video provider. Do not interpret a marketing page called "Claude Video Generator" as proof Claude itself generated the pixels or is universally the strongest video model.

Use an explicitly selected model when given. Otherwise use the capable current agent for planning/edit instructions, and select a generator/renderer based on available features, reference/identity control, duration, revision needs, budget and actual output quality. T3 cross-provider delegation follows its current catalog and [delegation contract](../../t3-workflows/references/delegation.md); avoid a mandatory director/artist/editor agent fleet. Model and tool access are different checks.

## Free does not mean every layer is free

Distinguish open-source editing, free-tier credits, existing subscriptions, software licenses and compute/GPU time. Local generation may have substantial hardware/download cost and restrictive model terms; do not install a large stack just to avoid a small paid render. Remotion's free commercial eligibility is conditional on its current license/entity criteria; do not call it unconditionally free for any business. Verify rights before embedding or redistributing tool code, separately from using a tool to produce content.

Estimate the total meaningful work: draft variants, clip duration/resolution, image/audio generation, retries, upscaling, export and external costs. Prefer a small representative sample before committing a budget to a long sequence. Reuse approved shots and revise the failed part; do not rerender the entire campaign for one caption. A free website allowance or unlimited label does not establish API/MCP entitlement.

## Official references

- [Kdenlive manual](https://docs.kdenlive.org/en/).
- [FFmpeg documentation](https://ffmpeg.org/documentation.html), plus the installed binary's version/help and actual encoder/filter availability.
- [Blender video editing](https://www.blender.org/features/video-editing/).
- [Remotion license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) and [documentation](https://www.remotion.dev/docs/).

These are optional routes, not installed dependencies or endorsed quality benchmarks. Tool licensing, current platform restrictions and commercial asset rights must be checked for the concrete task.
