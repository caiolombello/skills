# Recordly for software demos

Source reviewed at [109ca3a13c362e969d9add25d1f93406c36dba2a](https://github.com/webadderallorg/Recordly/tree/109ca3a13c362e969d9add25d1f93406c36dba2a), package 1.4.0. This is a source-based assessment, not a tested desktop installation.

## When it fits

Recordly is a native screen recorder/editor suited to product walkthroughs, tutorials and launch demos where real screen interaction matters. The README/source document screen/window capture, cursor smoothing/effects, timeline trimming, zoom/speed regions, annotations, webcam presentation, backgrounds/frames, extra audio, saved `.recordly` projects, and MP4/GIF export. It is not a substitute for a generative video model or a full general-purpose editing workflow.

## Working approach

Verify the installed release, platform, capture permissions, intended window/account and available control tool. Installation or source-build instructions are not authorization to install it. Use a demo/test account and sanitized project state where appropriate; record a short representative segment first. Check framing, text readability, cursor behavior and actual audio capture before recording the whole journey.

Capture the real interaction, edit waits/mistakes while preserving a truthful demonstration, add purposeful zooms/labels and export. Keep the editable project and real output. Check the exported file, not just the timeline. If Recordly cannot perform the broader edit, move the exported clip to an available editor; do not invent automation interfaces.

The inspected package exposes development/build/test commands; no supported end-user automation CLI/API was established. Drive the actual GUI only through authorized, exposed tools, or supply a manual recording/edit recipe. Browser automation availability does not provide native app control. Never pretend a Recordly demo was recorded from reading its source or mocks.

## Platform/account boundaries

The README describes Linux capture through Electron: X11 has screen/window selection; Wayland uses the system picker at recording start. Linux cursor hiding is unavailable in the documented path, so real and rendered cursors can both appear. System audio generally depends on PipeWire. These are things to check in a short capture, not claims that every Linux session is supported.

Local editing/export is documented; source also contains authentication and cloud-sharing paths. Do not infer all features work offline/account-free, automatically create an account, or upload recordings. Cloud sharing is separate from producing a local demo. Existing mocked Linux UI tests do not prove native capture on this user's desktop.

## License and sources

The repository states AGPL-3.0 and includes additional summary language about branding/attribution. This skill copies no Recordly source. Using it as an editor and incorporating/modifying/distributing its code or hosting a service are different choices; inspect actual license terms before the latter. Do not promise commercial asset clearance from the software license; footage, music, fonts and other inputs have their own rights.

- [README](https://github.com/webadderallorg/Recordly/blob/109ca3a13c362e969d9add25d1f93406c36dba2a/README.md).
- [License](https://github.com/webadderallorg/Recordly/blob/109ca3a13c362e969d9add25d1f93406c36dba2a/LICENSE.md).
- [Package](https://github.com/webadderallorg/Recordly/blob/109ca3a13c362e969d9add25d1f93406c36dba2a/package.json) and [Linux capture tests](https://github.com/webadderallorg/Recordly/blob/109ca3a13c362e969d9add25d1f93406c36dba2a/tests/ui/linux-capture.spec.ts).
