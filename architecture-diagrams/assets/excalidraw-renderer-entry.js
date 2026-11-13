// Rebuild input for @excalidraw/excalidraw@0.18.1. The version-pinned package
// exports these two functions from its production chunk as `lh` and `ri`.
// Re-check the aliases before updating the package; they are not a public API.
import {
  lh as restore,
  ri as exportToSvg,
} from "./node_modules/@excalidraw/excalidraw/dist/prod/chunk-K2UTITRG.js";

window.renderArchitectureScene = async (scene, options) => {
  const restored = restore(
    {
      elements: scene.elements ?? [],
      appState: scene.appState ?? {},
      files: scene.files ?? {},
    },
    null,
    null,
    {
      refreshDimensions: true,
      repairBindings: true,
    },
  );
  const elements = restored.elements.filter((element) => !element.isDeleted);
  const appState = {
    ...restored.appState,
    exportBackground: options.background,
    exportEmbedScene: false,
    viewBackgroundColor:
      scene.appState?.viewBackgroundColor ?? "#ffffff",
  };
  const svg = await exportToSvg({
    elements,
    appState,
    files: restored.files,
    exportPadding: options.padding,
    renderEmbeddables: false,
    skipInliningFonts: true,
  });
  svg.dataset.renderer = "architecture-diagrams";
  document.body.replaceChildren(svg);
  return new XMLSerializer().serializeToString(svg);
};

window.architectureRendererReady = true;
