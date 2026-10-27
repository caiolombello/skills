# Video editing, motion, and export verification

Use this for real footage, audio, captions and rendered animation. The same workflow applies across a local editor, FFmpeg, code renderer or a connected online editor; use only the exposed/installed route and current contracts.

## Inspect before editing

Preserve originals and work into new output paths. Inventory relevant clips, images, audio, captions, project files and references. Inspect actual duration, streams/codecs, dimensions, rotation/display aspect, frame-rate/timebase, audio layout, and relevant source quality. A file extension is not proof of encoding or orientation; variable frame rate, rotated phone clips and silent screen recordings need deliberate handling.

Read-only local inspection, if Python and ffprobe are available:

```sh
python3 -B <skill-dir>/scripts/probe_media.py /absolute/path/to/clip.mp4
```

This emits selected ffprobe metadata. It neither renders nor decodes every frame, checks captions, measures loudness, proves privacy, or judges quality. It rejects non-local inputs and limits ffprobe protocols; it is not a sandbox for hostile files. Do not infer full video capability from ffprobe's presence.

## Build an edit map

For each shot specify source and in/out, intended output duration, visual purpose/action, exact text, narration/music/SFX, transition and any speed change. Work in a clear timebase. Recalculate timing for cuts, crossfades, speed ramps and narration; do not append captions based on the unedited source timestamps. Preserve user-required ordering and wording.

For product demos, show the important interaction/result at a legible scale. Avoid long cursor travel, dead waits and unexplained jumps. Do not accelerate time-sensitive behavior while presenting the result as a real performance measurement. Synthetic mockups and generated screen interactions cannot prove actual product functionality.

For general edits, choose cuts and pacing that serve the story. Use restrained transitions and relevant B-roll; do not add motion to every frame by default. Code-based motion is useful for text, diagrams, charts, branded layouts and explainers; synthetic cinematic footage requires a video model or existing footage. Interactive HTML that looks like a video still needs a renderer/export before it is an MP4.

## Render deliberately

Check the actual tool version, codecs/filters and output requirements before building a command/project. FFmpeg builds differ: an installed ffmpeg may lack `libx264`, a font/subtitle filter, or a working hardware encoder. A listed hardware encoder does not prove an accessible device. Do not install codecs or silently change the delivery contract to hide a missing dependency.

For FFmpeg, pass arguments safely, avoid shell interpolation of filenames, disable interactive stdin, and refuse accidental overwrites (`-n`). Cropping/concatenating with stream copy can be keyframe-limited; re-encode when the requested edit requires frame-accurate cuts, compositing, captions or format changes. Check stream compatibility before concatenation and audio presence before mapping/mixing. Do not stretch footage into another aspect ratio; reframe the subject or pad deliberately.

For broad MP4 compatibility, H.264 with a suitable pixel format and AAC audio can be a useful starting profile when supported and appropriate; verify the recipient/platform requirements rather than treating it as universal. Frame rate, bitrate, resolution and audio should fit the source and use case. Higher resolution does not repair low-quality footage.

For captions, use speech grounded in the actual audio, correct names/numbers, align to edited timing, and check readable placement at mobile size. Supply SRT/VTT and/or burned-in captions as requested. Do not manufacture a transcript from metadata or assume a speech model/tool is installed. Preserve intelligible voice; check music balance, clipping, silence and sync by actually listening or measuring with a suitable tool. If listening is unavailable, report that limit.

## Inspect the exported file

Check container/streams and expected duration, frame geometry/display orientation, codec/pixel format, frame count/rate as relevant, and audio. Decode the export with an available tool when useful; a successful metadata probe alone can miss truncated/corrupt frames. Inspect beginning/end and important cuts/transitions/captions, plus continuous playback when timing/audio requires it. Extract frames/contact sheets for QA when appropriate; do not claim that a few stills verify the entire audio/video.

Check readability, exact text, privacy/redaction, identity/product consistency, blank/black or frozen frames, unexpected cursor duplication, watermark, and ending/CTA. A preview's success is not proof of the exported file. Keep editable project, source references and final export linked; retain the selected output and useful evidence when clearing temporary renders.

Deliver actual files and state what was checked. Source inspection, metadata validation, full decode, visual review, listening, provider generation and successful publication are separate evidence levels. Never promote a draft or queued job to finished video.
