---
name: content-production
description: "Use to create or edit video, images, voiceovers, podcasts, music/SFX and marketing content for a personal project or venture. Covers production, mixing/export and tool/budget choices; not ordinary messages, device troubleshooting or product-roadmap decisions."
---

# Content Production

Turn a project, product, or idea into an asset that helps a specific audience understand, trust, or act. Favor useful proof and a small publishable piece over a large speculative campaign. Do not promise commercial success from polished media alone.

## Establish a useful brief

Infer from the request and supplied assets: project/offer, audience and problem, intended action, channel, format/duration, available evidence, visual voice, language, deadline, tools, budget and authorized endpoint. For an early personal project without a brand, propose a simple consistent direction and identify the few assumptions that matter. Do not require an intake questionnaire before drafting.

Ask only for inputs that materially block the requested result. Continue independent preparation when footage, product facts, or integration access is missing. Use [brief and marketing](references/brief-and-marketing.md) for positioning, script, creative variants and outcome measurement. [product-management](../product-management/SKILL.md) owns consequential product strategy; this skill owns content production.

## Select the production route

Read only the relevant procedure:

| Task | Procedure |
| --- | --- |
| Cut, sequence, caption, resize/reframe, mix or export existing footage | [Video editing and QA](references/video-editing.md) |
| Record/edit spoken audio, produce narration/podcasts, create music/SFX, mix or master | [Audio and sound](references/audio-production.md) |
| Create/edit images, thumbnails, product visuals or a consistent asset family | [Images and brand](references/images-and-brand.md) |
| Choose free/local, manual, code-motion or paid generation | [Tools and budget](references/tools-and-budget.md) |
| Record a real software walkthrough with cursor/zoom polish | [Recordly](references/recordly.md) |
| Use Higgsfield, its connector/MCP, website or API | [Higgsfield](references/higgsfield.md) |

Keep these roles distinct: an assistant plans/directs or writes animation code; a capture tool records real behavior; a generative model synthesizes footage/images/audio; an editor/renderer assembles and exports. A language model, speech/music generator, Claude-branded workflow and Higgsfield account are not interchangeable capabilities. Choose by actual access and task fit; do not declare one LLM universally best for media.

If the user asks for a finished asset, produce it with available authorized tools and inspect it. A script, prompt, storyboard, score, HTML preview, queued generation or project file is not an exported video or audio file. Without rendering tools/access, deliver the useful script/edit map/prompts and exact next step, clearly identifying the unrendered artifact. A tool-independent plan is useful; do not pretend it contains encoded media.

## Build from one source of truth

Preserve supplied originals. Identify each asset's role: source footage, edit target, product evidence, style reference, insert, logo, voice, or music. An inspiration reference is not automatically authorized material to reuse. Keep offer, names, visual identity, facts and CTA consistent across video, cover and post. Use actual product captures for claims about real functionality; label a concept/mockup or synthetic demo appropriately.

For video, establish a small shot/edit map with source, in/out points, visual action, exact on-screen text, narration/audio, transition, purpose, and expected duration. Let the content determine pacing; avoid a fixed template of slogans, zooms, emojis or AI-style stock scenes. Approve a useful low-cost storyboard/still/short segment before expensive batches when that reduces risk; do not pause routine reversible work already authorized.

For raster creation/edits, use the available image-generation skill/tool and its required workflow; in Codex this is `imagegen` with the built-in tool by default. Keep target vs reference roles and exact text explicit. Do not introduce a paid image API, CLI fallback or SVG placeholder just to bypass its contract. Use existing vector/code assets when the requested result belongs in that format.

Writing uses [natural-writing](../natural-writing/SKILL.md); articles use [blog-posting](../blog-posting/SKILL.md). A content package does not need a blog workflow for every caption. Load specialist skills only for work that needs them.

## Cost, rights and authority

Reuse approved tools, spend limits and destinations. Generic interest in paid options does not authorize a subscription, top-up, external upload, paid batch or recurring job. Before a new charge not covered by the request/approved budget, establish a bounded estimate and limit. Once authorized, execute within that scope without per-render reconfirmation; stop before exceeding the limit, including revisions and retries. Distinguish zero additional software cost, existing subscription usage, trial credits and paid API usage.

Check the actual rights relevant to the deliverable: source footage, product/brand assets, music, fonts, stock, likeness and voice. Do not fabricate testimonials, results, customers or revenue. Honor the subject's consent and runtime restrictions for identity/voice work. Do not remove another creator's watermark or disguise a simulated result as customer proof. Software licensing and rights to each exported asset are separate questions; do not certify commercial clearance from a tool's name.

Discover integrations before claiming them unavailable. Prefer connected purpose-built tools where sufficient; follow [computer-use](../computer-use/SKILL.md) for requested GUI work and [t3-workflows](../t3-workflows/SKILL.md) for host-specific orchestration. Do not install software/connectors, change accounts/settings, or buy access merely because a reference mentions them. Secure secrets through the runtime's private mechanism, never chat or files committed to the project.

## Inspect and deliver

Review the export at its intended viewing size: opening, legibility, factual/brand accuracy, framing, continuity, audio/caption synchronization and ending/CTA. Inspect actual encoded media and important frames, not only an editor preview or successful render exit. Verify duration, dimensions/aspect/orientation, codecs, audio presence and source/caption coverage as relevant. The optional read-only [media probe](scripts/probe_media.py) assists metadata inspection; it cannot judge visual/audio quality or certify the platform accepts a file.

For audio-only work, verify the actual words/performance, timing, intelligibility, noise/artifacts, balance, clipping/loudness and export format as relevant. Distinguish peak normalization from perceived loudness, and use the intended delivery specification rather than a universal LUFS target. If listening is unavailable, report measured/decoded evidence and that subjective audition remains unrun.

Deliver the requested final files with absolute paths, plus editable project/timeline, captions or provenance notes when useful for reuse. Keep the package proportional; a short asset need not generate a folder of speculative documents. Clearly identify draft, render pending, rendered but unreviewed, technically checked and published states. Creating content does not publish it; if publication to a specified destination is already authorized, complete it using actual tools and report the returned outcome. Never invent posting, approval, reach or conversion results.

[Decision cases](evals/scenarios.json) test routing and limits; live Recordly/Higgsfield/provider access requires a real integration run.
