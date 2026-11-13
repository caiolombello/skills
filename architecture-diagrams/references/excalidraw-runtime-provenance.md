# Offline Excalidraw runtime provenance

The renderer uses a vendored browser bundle rather than executing CDN code.
`scripts/render_excalidraw.py` verifies the bundle SHA-256 from
`assets/excalidraw-runtime.json`, places the browser context offline before it
loads any page content, and injects the private scene only after the local
runtime is ready.

## Reviewed inputs

- `@excalidraw/excalidraw@0.18.1`, MIT, npm integrity recorded in the manifest.
- `react@18.3.1`.
- `esbuild@0.25.9`, used only to build the vendored asset.
- Exact transitive versions in
  [excalidraw-runtime-build/package-lock.json](excalidraw-runtime-build/package-lock.json).
- Complete package notices in
  [licenses/excalidraw-renderer-third-party-notices.txt](licenses/excalidraw-renderer-third-party-notices.txt).

The production package exposes `restore` and `exportToSvg` through minified
internal aliases. The pinned rebuild input records the aliases for 0.18.1;
they are not a stable public API and must be re-audited on every upgrade.

## Rebuild in disposable storage

Do not install build dependencies into the skill directory. In an empty,
task-local directory:

```bash
cp references/excalidraw-runtime-build/package.json .
cp references/excalidraw-runtime-build/package-lock.json .
cp assets/excalidraw-renderer-entry.js ./entry.js
npm ci --ignore-scripts
./node_modules/.bin/esbuild entry.js \
  --bundle --format=iife --platform=browser --target=chrome120 \
  --minify --legal-comments=eof --metafile=metafile.json \
  --outfile=excalidraw-renderer.bundle.js
sha256sum excalidraw-renderer.bundle.js
```

Before replacing the vendored bundle:

1. Verify npm integrity and the upstream license at the pinned tag.
2. Inspect the esbuild metafile and regenerate third-party notices from every
   included package.
3. Update the SHA-256 and package versions in `assets/excalidraw-runtime.json`.
4. Run the renderer tests, render representative scenes, and inspect SVG and
   PNG output visually.
5. Confirm a network monitor sees no browser requests during rendering.

Never update only the version string or hash. The bundle, lockfile, entry,
manifest, notices, and rendered regression evidence are one review unit.
