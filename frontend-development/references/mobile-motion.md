# Mobile and Motion Checks

Read when changing mobile behavior, viewport-sensitive surfaces, gestures, or animation. Use the actual project stack and supported platforms; do not install a library or assume web and native APIs are interchangeable.

## Mobile web

- Verify viewport metadata and responsive constraints without disabling user zoom.
- Inspect browser chrome expansion, orientation, safe-area insets, and bottom controls. Choose viewport units from the intended behavior and supported browsers rather than mechanically replacing every height.
- Open the virtual keyboard on a real supported device when available: ensure labels, focused input, errors, and submit controls remain reachable. Device emulation alone does not establish keyboard or safe-area behavior.
- Avoid hover-only actions and sticky hover feedback on touch; preserve explicit focus and pressed states. Scrolling and gestures must not block navigation or essential controls.
- Check long localized labels, dialogs, tables, sticky regions, enlarged text, and reduced motion. Preserve content and reading order when layout changes.
- If native mobile is in scope, use its existing platform controls and test on the configured simulator/device; a resized web screenshot is not native verification.

## Purposeful motion

Define what transition explains: causality, continuity, feedback, or spatial orientation. Prefer no motion when repeated animation distracts from frequent work. Choose timing and easing for travel, frequency, and interruptibility rather than imposing one duration everywhere.

Keep stable content during async changes. Define cancellation, interruption, and reduced-motion behavior; essential feedback must remain available without animation. Prefer transform/opacity for suitable visual transitions, but measure the actual implementation before claiming smoothness or a performance benefit. Avoid layout-heavy animation during streaming or high-frequency interactions. Do not use animation as proof of server progress.

## Evidence

Capture rendered images for layout and a short recording or interactive observation for motion. Record device/browser or emulator, viewport, state, and checks performed. Inspect focus and keyboard behavior separately. When real-device or native-runtime access is unavailable, state that limitation instead of claiming native polish.
