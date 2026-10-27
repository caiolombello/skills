# Audio, voice, music, and sound design

Use for standalone audio or the sound layer of a video: narration/TTS, recording cleanup, dialogue/podcast edit, music/jingles, SFX/ambience, mixing and delivery. This is creative production, not microphone hardware diagnosis or permission to change system audio settings.

## Brief and material

Infer the purpose, audience/channel, language/accent, duration, source recordings or approved spoken copy, voice/performance direction, music/SFX role, budget and deliverables. For Brazilian Portuguese, check pronunciation of names, brands, acronyms and numbers; do not force an accent or change exact offers to improve a voice model's output. A pronunciation guide can accompany protected written text.

Identify original takes, transcript, voice reference, music license, sound cues and edit target. Preserve originals and an editable session/recipe when useful. A script/score/sound prompt is preparation, not a WAV/MP3. Generated captions or a plausible transcript are not evidence of what the recording actually says.

## Voice and spoken content

For recording, use the requested capture source/session and actual tools. A specific recording request supplies authority for that capture; do not repeatedly ask consent already given. Mere access to a tab or a microphone does not authorize recording, change audio devices, start system capture or upload private takes. Do not alter a working input chain as a production shortcut.

For TTS, choose an available supported voice/model for language, style, pronunciation, continuity and use rights. Reuse approved copy and voice direction; generate a representative sample before a long paid batch when useful. Keep consistent voice/settings across segments and check join points. An LLM writing dialogue does not itself supply an audio-generation engine. Use a licensed/generic or authorized personal voice; do not fabricate a real person's endorsement or assume a supplied reference grants cloning rights. Follow actual provider consent and safety controls.

For dialogue/podcasts, make a cut map or verified transcript/markers before editing. Remove the requested dead air, mistakes or fillers while retaining meaning, speaker context and natural turn-taking. Do not cut away a qualification so a person appears to say something else. Preserve natural breaths/word endings where they support intelligibility. Recheck captions and timestamps after edits, speed changes or inserted narration; verify uncertain words against audio or flag them.

## Cleanup and mix

Inspect the source before selecting treatment. Hum, steady hiss, clicks, clipping, room reverb and another speaker are different problems. Use restrained, relevant denoise/declick/filter/EQ/de-ess/compression treatment, compare a representative before/after and listen for damage. Stronger noise removal can destroy speech; an algorithm cannot guarantee recovery of missing/clipped words. Avoid a fixed filter stack for every recording.

Balance dialogue first, then music/ambience/effects; use automation or supported ducking when helpful. Preserve appropriate headroom and check edits/fades, tails, silence, channel layout, stereo phase/mono compatibility and A/V sync. Music that masks speech is not a useful upgrade. Record which tracks and gains/effects belong to each cue when reproducibility matters.

For music/jingles/SFX, define duration, tempo/mood/instrumentation or action/material/space, loopability, cue time, tail and role in the mix. Do not assume every effect needs a generator: authorized field recordings, licensed stock and local synthesis can fit. Keep stems when useful for later revisions. A generated loop is not automatically seamless; check the join.

## Loudness and export

Set the destination's required format, codec, sample rate, bit depth and channel layout, plus integrated loudness/true-peak criteria when relevant. Verify current delivery requirements for an actual platform/client. Do not label a single LUFS number a universal podcast, video or streaming standard, or confuse peak normalization with perceived loudness. Compression, EQ and gain changes invalidate previous measurements; measure the final mix/export.

For a supported FFmpeg workflow, inspect installed filter/options first. When precise loudness normalization matters, use an appropriate measurement and normalization method, such as a measured two-pass `loudnorm` workflow, then measure again. Carry measurements from the same edited audio into that pass; don't reuse stale values from an earlier cut or ignore the tool's actual normalization mode. Use new output paths and inspect effects before processing originals.

Keep a suitable lossless/editable master when requested/useful and a delivery encode appropriate for the channel; repeatedly transcoding a lossy file can degrade it. Confirm real audio streams, duration/sample count as relevant, sample rate/channels/codec, full decode, loudness/true peaks and obvious silence/clipping. Listen for pronunciation, meaning, artifacts, balance and sync when capable. The [metadata probe](../scripts/probe_media.py) supports audio-only files but does not listen, measure loudness or certify a master. Distinguish rendered, technically measured, actually auditioned, and published states.

## Routes and rights

| Route | Useful work | Boundary |
| --- | --- | --- |
| Existing recordings + available FFmpeg/Audacity | Cuts, cleanup, fades, mix and loudness/export | Local editing can avoid generation charges; tools/capture access still need to exist |
| Available local TTS, such as Piper | Narration without a hosted generation service | Engine, voice model/language and license are separate; no automatic downloads/install |
| Connected ElevenLabs or another speech service | Narration, voice workflows, generated effects or music as actually supported | Check model/voice, language, account, budget and commercial terms; do not invent a connection/API |
| Connected Descript/editor | Transcript-assisted podcast/dialogue and media editing | Catalog availability is not installation; verify actual tool capabilities and output |
| Suno or another available music service | Jingles/tracks or music drafts | Check current download/commercial rights for this plan/output; a free trial is not ad-use clearance |
| Higgsfield audio/voice route | Audio coupled to supported content/video generation | Optional and route-dependent; follow [Higgsfield guidance](higgsfield.md), not assumed feature parity |

No provider is required. Discover the actual service/tool and honor selected providers, approved budgets and privacy/rights. Audio-only exports, stems, voiceovers, SFX and music can have different entitlements; do not transfer a subscription's terms across products. Creative generation does not authorize buying access, unbounded retries, uploading private recordings or publishing. Reuse explicit authorization when those actions are already part of the task.

Primary references reviewed on 2026-10-27:
[Audacity noise reduction](https://manual.audacityteam.org/man/noise_reduction.html),
[amplitude versus loudness](https://manual.audacityteam.org/man/amplify_and_normalize.html),
[FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html),
[Piper](https://github.com/OHF-Voice/piper1-gpl),
[ElevenLabs speech](https://elevenlabs.io/docs/overview/capabilities/text-to-speech) and [creative terms](https://elevenlabs.io/creative-terms),
[Descript podcasting](https://www.descript.com/podcasting),
[Suno download/plan changes](https://help.suno.com/en/articles/13614785) and [commercial-use guidance](https://help.suno.com/en/articles/9601665).
Refresh current account/plan/model rules before a commercial or paid use; no quotas/prices are pinned here.
