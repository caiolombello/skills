/*
 * ui_audit.js — dependency-free, in-page UI quality audit.
 *
 * Evaluate this file inside a rendered page (Playwright `page.evaluate(source)`,
 * DevTools console, or any browser tool that runs JavaScript), then call:
 *
 *   await window.__uiAudit({ narrow: innerWidth <= 480 })
 *
 * It returns JSON: { tool, version, url, viewport, metrics, issues[], summary }.
 * Findings are heuristic evidence to inspect in screenshots, not a conformance
 * verdict: "error" is a likely defect, "warn" a likely quality problem, "info" a
 * signal for the design critique. The audit only reads the page.
 */
(() => {
  'use strict';

  const VERSION = '1.0.0';
  const SKIP_TAGS = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'HEAD', 'TITLE', 'OPTION', 'DATALIST']);
  const MEDIA_TAGS = new Set(['IMG', 'VIDEO', 'CANVAS', 'PICTURE', 'SVG', 'IFRAME', 'OBJECT', 'EMBED']);
  const GENERIC_FAMILIES = new Set([
    'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui', 'ui-serif', 'ui-sans-serif',
    'ui-monospace', 'ui-rounded', 'emoji', 'math', 'fangsong', '-apple-system', 'blinkmacsystemfont',
  ]);
  const INTERACTIVE_SELECTOR = [
    'a[href]', 'button', 'input:not([type="hidden"])', 'select', 'textarea', 'summary',
    '[role="button"]', '[role="link"]', '[role="tab"]', '[role="menuitem"]', '[role="checkbox"]',
    '[role="switch"]', '[role="radio"]', '[role="option"]', '[tabindex]:not([tabindex="-1"])',
  ].join(',');
  const CLICHES = [
    'supercharge', 'seamless', 'seamlessly', 'unlock', 'revolutionize', 'revolutionise', 'game-changer',
    'game changer', 'game-changing', 'next-gen', 'next-level', 'cutting-edge', 'effortless', 'effortlessly',
    'elevate your', 'empower', 'streamline your', 'unleash', 'harness the power', "in today's fast-paced",
    'world-class', 'best-in-class', 'all-in-one platform', 'blazing fast', 'lightning-fast', 'transform your',
    'potencialize', 'alavanque', 'revolucione', 'revolucionári', 'eleve seu', 'eleve sua', 'transforme seu',
    'transforme sua', 'sem complicação', 'de forma simples e rápida', 'solução completa', 'próximo nível',
  ];
  const PLACEHOLDER_PATTERNS = [
    [/lorem ipsum|dolor sit amet/i, 'lorem ipsum'],
    [/\b(?:Feature|Item|Product|Card|Title|Heading|Section) [1-9]\b/, 'numbered placeholder ("Feature 1")'],
    [/\b(?:John|Jane) Doe\b/, '"John/Jane Doe"'],
    [/\b(?:Your (?:Company|Brand|Product) (?:Name|Here|Inc)|Your Logo|Company Name|Logo Here)\b/, '"Your Company Name"'],
    [/\b(?:placeholder text|insert (?:text|image|content) here)\b/i, 'placeholder instruction'],
  ];
  // Characters that render as color emoji (not ©, ®, ™, arrows, or check marks).
  const EMOJI = /\p{Emoji_Presentation}|\p{Extended_Pictographic}️/u;
  const EMOJI_START = /^(?:\p{Emoji_Presentation}|\p{Extended_Pictographic}️)/u;
  // Platform fonts that legitimately fall back on other operating systems.
  const OS_FONTS = new Set([
    'segoe ui', 'sf pro', 'sf pro text', 'sf pro display', 'helvetica neue', 'helvetica', 'arial', 'roboto',
    'ubuntu', 'cantarell', 'noto sans', 'oxygen', 'fira sans', 'droid sans', 'menlo', 'monaco', 'consolas',
    'courier new', 'courier', 'sfmono-regular', 'sf mono', 'liberation mono', 'georgia', 'times new roman',
    'times', 'verdana', 'tahoma', 'trebuchet ms', 'avenir', 'avenir next', 'gill sans', 'optima', 'palatino',
    'iowan old style', 'charter', 'cambria', 'calibri', 'garamond', 'lucida grande', 'apple color emoji',
    'segoe ui emoji', 'noto color emoji',
  ]);

  // ---------------------------------------------------------------- helpers

  const round = (n, d = 1) => Math.round(n * 10 ** d) / 10 ** d;

  function selectorOf(el) {
    if (!el || el.nodeType !== 1) return '';
    const safe = (s) => /^[A-Za-z_][\w-]*$/.test(s);
    if (el.id && safe(el.id)) return `#${el.id}`;
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && parts.length < 4 && node !== document.documentElement) {
      if (node.id && safe(node.id)) { parts.unshift(`#${node.id}`); break; }
      let part = node.tagName.toLowerCase();
      const classes = Array.from(node.classList).filter((c) => safe(c) && c.length <= 28).slice(0, 2);
      if (classes.length) part += `.${classes.join('.')}`;
      const parent = node.parentElement;
      if (parent) {
        const same = Array.from(parent.children).filter((c) => c.tagName === node.tagName);
        if (same.length > 1) part += `:nth-of-type(${same.indexOf(node) + 1})`;
      }
      parts.unshift(part);
      node = parent;
    }
    return parts.join(' > ');
  }

  function snippet(text, max = 70) {
    const t = (text || '').replace(/\s+/g, ' ').trim();
    return t.length > max ? `${t.slice(0, max - 1)}…` : t;
  }

  function isVisuallyHidden(el, rect) {
    if (rect.width <= 1 && rect.height <= 1) return true;
    let node = el;
    for (let depth = 0; node && node.nodeType === 1 && depth < 5; depth += 1) {
      const cs = getComputedStyle(node);
      if (cs.clipPath === 'inset(50%)') return true;
      if (cs.clip && cs.clip !== 'auto' && /rect\(\s*0(px)?[\s,]+0(px)?[\s,]+0(px)?[\s,]+0(px)?\s*\)/.test(cs.clip)) return true;
      const r = node.getBoundingClientRect();
      if (r.width <= 1 && r.height <= 1 && cs.overflow === 'hidden') return true;
      node = node.parentElement;
    }
    return false;
  }

  function isRendered(el) {
    if (!el || el.nodeType !== 1) return false;
    if (typeof el.checkVisibility === 'function') {
      if (!el.checkVisibility({ opacityProperty: true, visibilityProperty: true })) return false;
    } else {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility !== 'visible' || Number(cs.opacity) === 0) return false;
    }
    const rect = el.getBoundingClientRect();
    if (rect.width < 1 || rect.height < 1) return false;
    return !isVisuallyHidden(el, rect);
  }

  function unionRect(a, b) {
    const left = Math.min(a.left, b.left);
    const top = Math.min(a.top, b.top);
    const right = Math.max(a.right, b.right);
    const bottom = Math.max(a.bottom, b.bottom);
    return { left, top, right, bottom, width: right - left, height: bottom - top };
  }

  function plainRect(r) {
    return { left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height };
  }

  // ---------------------------------------------------------------- color

  const colorCache = new Map();
  let pixel = null;

  function parseColor(value) {
    if (!value) return null;
    if (colorCache.has(value)) return colorCache.get(value);
    let color = null;
    const m = value.match(/^rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)$/);
    if (m) {
      const alpha = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4]);
      color = { r: +m[1], g: +m[2], b: +m[3], a: alpha };
    } else if (value === 'transparent') {
      color = { r: 0, g: 0, b: 0, a: 0 };
    } else {
      // oklch(), lab(), color(display-p3 …): let the canvas convert to sRGB.
      if (!pixel) {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        pixel = canvas.getContext('2d', { willReadFrequently: true });
      }
      pixel.clearRect(0, 0, 1, 1);
      pixel.fillStyle = '#000';
      pixel.fillStyle = value;
      pixel.fillRect(0, 0, 1, 1);
      const d = pixel.getImageData(0, 0, 1, 1).data;
      color = { r: d[0], g: d[1], b: d[2], a: d[3] / 255 };
    }
    colorCache.set(value, color);
    return color;
  }

  const channel = (v) => {
    const c = v / 255;
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  };
  const luminance = (c) => 0.2126 * channel(c.r) + 0.7152 * channel(c.g) + 0.0722 * channel(c.b);
  const contrast = (a, b) => {
    const l1 = luminance(a);
    const l2 = luminance(b);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  };
  const over = (top, bottom) => {
    const a = top.a + bottom.a * (1 - top.a);
    if (a <= 0) return { r: 0, g: 0, b: 0, a: 0 };
    const mix = (t, b) => (t * top.a + b * bottom.a * (1 - top.a)) / a;
    return { r: mix(top.r, bottom.r), g: mix(top.g, bottom.g), b: mix(top.b, bottom.b), a };
  };
  const hex = (c) => `#${[c.r, c.g, c.b].map((v) => Math.round(v).toString(16).padStart(2, '0')).join('')}`;

  function hsl(c) {
    const r = c.r / 255;
    const g = c.g / 255;
    const b = c.b / 255;
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const l = (max + min) / 2;
    if (max === min) return { h: 0, s: 0, l };
    const d = max - min;
    const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    let h;
    if (max === r) h = (g - b) / d + (g < b ? 6 : 0);
    else if (max === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    return { h: h * 60, s, l };
  }

  function canvasColor() {
    const scheme = getComputedStyle(document.documentElement).colorScheme || '';
    const prefersDark = matchMedia('(prefers-color-scheme: dark)').matches;
    const dark = /dark/.test(scheme) && (!/light/.test(scheme) || prefersDark);
    return dark ? { r: 18, g: 18, b: 18, a: 1 } : { r: 255, g: 255, b: 255, a: 1 };
  }

  function compositeBackground(elements) {
    const layers = [];
    for (let i = 0; i < elements.length; i += 1) {
      const e = elements[i];
      if (i > 0 && MEDIA_TAGS.has(e.tagName.toUpperCase())) return { unknown: 'text over media' };
      const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return { unknown: 'background image or gradient' };
      if (coveringPseudo(e)) return { unknown: 'pseudo-element background' };
      const bg = parseColor(cs.backgroundColor);
      if (bg && bg.a > 0) {
        layers.push(bg);
        if (bg.a >= 0.999) break;
      }
    }
    let color = canvasColor();
    for (let i = layers.length - 1; i >= 0; i -= 1) color = over(layers[i], color);
    return { color };
  }

  function coveringPseudo(e) {
    const box = e.getBoundingClientRect();
    for (const which of ['::before', '::after']) {
      const ps = getComputedStyle(e, which);
      if (ps.content === 'none' || ps.content === 'normal' || !/absolute|fixed/.test(ps.position)) continue;
      const painted = (ps.backgroundImage && ps.backgroundImage !== 'none') || (parseColor(ps.backgroundColor) || { a: 0 }).a > 0;
      if (painted && parseFloat(ps.width) >= box.width * 0.5 && parseFloat(ps.height) >= box.height * 0.5) return true;
    }
    return false;
  }

  let mediaBoxes = null;
  function mediaUnder(el, x, y) {
    // Hit testing skips pointer-events:none layers (hero canvases, background video), so check geometry.
    if (!mediaBoxes) {
      mediaBoxes = Array.from(document.querySelectorAll('img, video, canvas, picture, svg, iframe'))
        .map((m) => ({ m, r: m.getBoundingClientRect() }))
        .filter(({ r }) => r.width >= 40 && r.height >= 40);
    }
    return mediaBoxes.some(({ m, r }) => !el.contains(m) && !m.contains(el) && x >= r.left && x <= r.right && y >= r.top && y <= r.bottom);
  }

  function backgroundBehind(el, rect) {
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    if (mediaUnder(el, x, y)) return { unknown: 'text over media' };
    if (x >= 0 && y >= 0 && x < innerWidth && y < innerHeight) {
      const stack = document.elementsFromPoint(x, y);
      const idx = stack.findIndex((e) => e === el || el.contains(e));
      if (idx >= 0) {
        const below = [el, ...stack.slice(idx + 1).filter((e) => e !== el && !el.contains(e))];
        return compositeBackground(below);
      }
    }
    const chain = [];
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) chain.push(n);
    return compositeBackground(chain);
  }

  function effectiveOpacity(el) {
    let value = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) value *= Number(getComputedStyle(n).opacity);
    return value;
  }

  // ---------------------------------------------------------------- collection

  function collectText(limit = 5000) {
    const groups = new Map();
    const root = document.body || document.documentElement;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const parent = node.parentElement;
        if (!parent || SKIP_TAGS.has(parent.tagName) || parent.closest('svg')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    for (let node = walker.nextNode(); node && groups.size < limit; node = walker.nextNode()) {
      const parent = node.parentElement;
      if (!groups.has(parent)) groups.set(parent, []);
      groups.get(parent).push(node);
    }
    const out = [];
    const range = document.createRange();
    for (const [el, nodes] of groups) {
      if (!isRendered(el)) continue;
      let rect = null;
      let text = '';
      const lines = [];
      for (const t of nodes) {
        range.selectNodeContents(t);
        const r = range.getBoundingClientRect();
        if (r.width > 0 && r.height > 0) rect = rect ? unionRect(rect, r) : plainRect(r);
        for (const line of range.getClientRects()) if (line.width > 1 && line.height > 1) lines.push(plainRect(line));
        text += t.nodeValue;
      }
      if (!rect || clippedAway(el, rect)) continue;
      // Illustrations built from DOM (aria-hidden or role="img") are pictures, not readable content.
      if (el.closest('[aria-hidden="true"], [role="img"]')) continue;
      out.push({ el, nodes, rect, lines, text: text.replace(/\s+/g, ' ').trim(), cs: getComputedStyle(el) });
    }
    return out;
  }

  // Text moved fully outside the page or its clipping box (text-indent image replacement,
  // off-screen slides) is invisible; it should not be audited as visible text.
  function clippedAway(el, rect) {
    if (rect.right <= 0 || rect.bottom <= -scrollY) return true;
    for (let a = el, depth = 0; a && a !== document.body && depth < 4; a = a.parentElement, depth += 1) {
      const cs = getComputedStyle(a);
      if (!/hidden|clip/.test(cs.overflowX + cs.overflowY)) continue;
      const box = a.getBoundingClientRect();
      if (rect.right <= box.left || rect.left >= box.right || rect.bottom <= box.top || rect.top >= box.bottom) return true;
    }
    return false;
  }

  function lineCount(nodes) {
    const range = document.createRange();
    const tops = new Set();
    for (const t of nodes) {
      range.selectNodeContents(t);
      for (const r of range.getClientRects()) if (r.width > 1) tops.add(Math.round(r.top / 4));
    }
    return tops.size;
  }

  function visibleTextOf(el) {
    let text = '';
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      if (n.parentElement && n.parentElement.closest('[aria-hidden="true"]')) continue;
      text += n.nodeValue;
    }
    return text.replace(/\s+/g, ' ').trim();
  }

  function accessibleName(el) {
    const label = el.getAttribute('aria-label');
    if (label && label.trim()) return { name: label.trim() };
    const ids = el.getAttribute('aria-labelledby');
    if (ids) {
      const t = ids.split(/\s+/).map((id) => (document.getElementById(id) || {}).textContent || '').join(' ').trim();
      if (t) return { name: t };
    }
    if (el.labels && el.labels.length) {
      const t = Array.from(el.labels).map((l) => l.textContent).join(' ').trim();
      if (t) return { name: t };
    }
    const tag = el.tagName;
    if (tag === 'INPUT') {
      const type = (el.getAttribute('type') || 'text').toLowerCase();
      if (['submit', 'button', 'reset'].includes(type)) return { name: (el.value || '').trim() || (type === 'button' ? '' : type) };
      if (type === 'image') return { name: (el.getAttribute('alt') || '').trim() };
    }
    const isField = tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA';
    if (!isField) {
      const text = visibleTextOf(el);
      if (text) return { name: text };
      const img = el.querySelector('img[alt]:not([alt=""])');
      if (img) return { name: img.getAttribute('alt').trim() };
      for (const child of el.querySelectorAll('[aria-label], [aria-labelledby]')) {
        if (child.closest('[aria-hidden="true"]')) continue;
        const own = (child.getAttribute('aria-label') || '').trim()
          || (child.getAttribute('aria-labelledby') || '').split(/\s+/).map((id) => (document.getElementById(id) || {}).textContent || '').join(' ').trim();
        if (own) return { name: own };
      }
      const title = el.querySelector('svg title');
      if (title && title.textContent.trim()) return { name: title.textContent.trim() };
    }
    const titleAttr = el.getAttribute('title');
    if (titleAttr && titleAttr.trim()) return { name: titleAttr.trim() };
    const placeholder = el.getAttribute('placeholder');
    if (placeholder && placeholder.trim()) return { name: placeholder.trim(), placeholderOnly: true };
    return { name: '' };
  }

  function fontAvailable(family) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const sample = 'mmmmmmmmmmlli1WQ@#&gy';
    const width = (font) => { ctx.font = font; return ctx.measureText(sample).width; };
    return ['monospace', 'serif', 'sans-serif'].some((fallback) => {
      const base = width(`72px ${fallback}`);
      return Math.abs(width(`72px "${family}", ${fallback}`) - base) > 0.5;
    });
  }

  // ---------------------------------------------------------------- audit

  async function audit(options = {}) {
    mediaBoxes = null;
    const narrow = options.narrow !== undefined ? Boolean(options.narrow) : innerWidth <= 480;
    const maxExamples = options.maxExamples || 5;
    const issues = new Map();
    const report = (id, severity, message, example) => {
      if (!issues.has(id)) issues.set(id, { id, severity, message, count: 0, examples: [] });
      const issue = issues.get(id);
      issue.count += 1;
      if (example && issue.examples.length < maxExamples) issue.examples.push(example);
    };
    const docEl = document.documentElement;
    const vw = docEl.clientWidth;
    const vh = innerHeight;

    const texts = collectText();
    const allElements = Array.from((document.body || docEl).querySelectorAll('*'));
    const interactive = Array.from(document.querySelectorAll(INTERACTIVE_SELECTOR))
      .filter((el) => !el.closest('[inert]') && isRendered(el));

    // -- document semantics
    if (!docEl.getAttribute('lang')) report('html-lang-missing', 'warn', 'The <html> element has no lang attribute.');
    if (!document.title.trim()) report('title-missing', 'warn', 'The document has no <title>.');
    const viewportMeta = document.querySelector('meta[name="viewport"]');
    if (!viewportMeta) {
      report('viewport-meta-missing', 'warn', 'No <meta name="viewport">; mobile browsers will render a zoomed-out desktop layout.');
    } else {
      const content = (viewportMeta.getAttribute('content') || '').toLowerCase();
      const max = content.match(/maximum-scale\s*=\s*([\d.]+)/);
      if (/user-scalable\s*=\s*(no|0)/.test(content) || (max && parseFloat(max[1]) < 2)) {
        report('zoom-disabled', 'error', 'The viewport meta blocks pinch-zoom (user-scalable=no or maximum-scale < 2).', { detail: content });
      }
    }
    if (!document.querySelector('main, [role="main"]')) report('main-landmark-missing', 'warn', 'No <main> landmark; screen-reader users cannot jump to the content.');

    // -- headings
    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6, [role="heading"]'))
      .filter(isRendered)
      .map((el) => ({ el, level: Number(el.getAttribute('aria-level')) || Number(el.tagName.slice(1)) || 2, text: snippet(el.textContent, 80) }));
    const h1s = headings.filter((h) => h.level === 1);
    if (!h1s.length) report('h1-missing', 'warn', 'No visible h1; the page purpose has no top-level heading.');
    if (h1s.length > 1) report('h1-multiple', 'info', `${h1s.length} visible h1 elements; usually one page title is clearer.`);
    for (let i = 1; i < headings.length; i += 1) {
      if (headings[i].level > headings[i - 1].level + 1) {
        report('heading-skip', 'warn', 'Heading levels skip (e.g. h2 → h4); structure is unclear to assistive tech.', {
          selector: selectorOf(headings[i].el), detail: `h${headings[i - 1].level} → h${headings[i].level}: ${headings[i].text}`,
        });
      }
    }

    // -- horizontal overflow
    const rootOverflow = `${getComputedStyle(docEl).overflowX} ${document.body ? getComputedStyle(document.body).overflowX : ''}`;
    if (docEl.scrollWidth > vw + 1) {
      const clipped = /hidden|clip/.test(rootOverflow);
      const offenders = [];
      const scrollsOrClips = (from) => {
        for (let a = from; a && a !== document.body && a !== docEl; a = a.parentElement) {
          if (/hidden|clip|auto|scroll/.test(getComputedStyle(a).overflowX)) return true;
        }
        return false;
      };
      for (const el of allElements) {
        const r = el.getBoundingClientRect();
        if (r.width < 1 || (r.right <= vw + 1 && r.left >= -1)) continue;
        if (getComputedStyle(el).position === 'fixed' || !isRendered(el)) continue;
        if (scrollsOrClips(el.parentElement) || offenders.some((o) => o.el.contains(el))) continue;
        offenders.push({ el, r });
      }
      // Unbreakable text (long words, nowrap) overflows without any element box doing so.
      for (const t of texts) {
        if (t.rect.right <= vw + 1 || offenders.some((o) => o.el.contains(t.el))) continue;
        if (!scrollsOrClips(t.el)) offenders.push({ el: t.el, r: t.rect, text: t.text });
      }
      const severity = clipped ? 'info' : 'error';
      const message = clipped
        ? 'Content is wider than the viewport but clipped by overflow-x on the root; check nothing important is cut off.'
        : `Page scrolls horizontally (${docEl.scrollWidth}px content in a ${vw}px viewport).`;
      if (!offenders.length) report('horizontal-overflow', severity, message);
      for (const o of offenders.slice(0, 8)) {
        const parent = o.el.parentElement;
        const track = parent && /grid|flex/.test(getComputedStyle(parent).display) && parent.getBoundingClientRect().right <= vw + 1;
        report('horizontal-overflow', severity, message, {
          selector: selectorOf(o.el), text: o.text ? snippet(o.text, 40) : undefined,
          detail: `extends to ${Math.round(o.r.right)}px${track ? ' (grid/flex item wider than its container: try min-width: 0 or minmax(0, 1fr))' : ''}`,
        });
      }
    }

    // -- text: contrast, clipping, sizing, line length, copy
    const fontSizes = new Map();
    const families = new Map();
    const textColors = new Map();
    const contrastSeen = new Set();
    let unknownContrast = 0;
    let uppercaseLabels = 0;
    const pageText = [];
    for (const t of texts) {
      const { el, cs, rect, text } = t;
      const size = parseFloat(cs.fontSize);
      const weight = Number(cs.fontWeight) || 400;
      fontSizes.set(round(size), (fontSizes.get(round(size)) || 0) + 1);
      families.set(cs.fontFamily, (families.get(cs.fontFamily) || 0) + 1);
      pageText.push(text);

      const fg = parseColor(cs.color);
      if (fg) textColors.set(hex(fg), (textColors.get(hex(fg)) || 0) + 1);
      const disabled = el.closest(':disabled, [aria-disabled="true"], [inert]');
      if (fg && !disabled) {
        const bg = backgroundBehind(el, rect);
        if (bg.unknown) {
          unknownContrast += 1;
        } else {
          const ink = over({ ...fg, a: fg.a * effectiveOpacity(el) }, bg.color);
          const ratio = contrast(ink, bg.color);
          const large = size >= 24 || (size >= 18.66 && weight >= 700);
          const needed = large ? 3 : 4.5;
          const key = `${hex(ink)}|${hex(bg.color)}|${large}`;
          if (ratio < needed && !contrastSeen.has(key)) {
            contrastSeen.add(key);
            report('contrast', 'error', 'Text contrast below WCAG AA (4.5:1 normal, 3:1 large text).', {
              selector: selectorOf(el), text: snippet(text, 50), detail: `${round(ratio, 2)}:1 ${hex(ink)} on ${hex(bg.color)} at ${round(size)}px/${weight}`,
            });
          } else if (ratio < needed) {
            report('contrast', 'error', 'Text contrast below WCAG AA (4.5:1 normal, 3:1 large text).');
          }
        }
      }

      // Clipped or spilling text. Measure against the nearest box-generating ancestor.
      let box = el;
      while (box.parentElement && ['inline', 'contents'].includes(getComputedStyle(box).display)) box = box.parentElement;
      const boxRect = box.getBoundingClientRect();
      const clamped = (s) => s.textOverflow === 'ellipsis' || (s.webkitLineClamp && s.webkitLineClamp !== 'none');
      if (!clamped(cs) && getComputedStyle(box).overflowX === 'visible' && (rect.right > boxRect.right + 2 || rect.left < boxRect.left - 2)) {
        report('text-overflow', 'warn', 'Text spills outside its box (fixed width, nowrap, or a long word).', { selector: selectorOf(el), text: snippet(text, 50) });
      }
      for (let a = box, depth = 0; a && a !== document.body && depth < 6; a = a.parentElement, depth += 1) {
        const acs = getComputedStyle(a);
        const clipX = /hidden|clip/.test(acs.overflowX);
        const clipY = /hidden|clip/.test(acs.overflowY);
        if (!clipX && !clipY) continue;
        if (clamped(acs)) break;
        const ar = a.getBoundingClientRect();
        // Fully outside means an off-screen slide or panel, not text that was cut.
        const startsInside = rect.top < ar.bottom && rect.left < ar.right;
        if (startsInside && ((clipY && rect.bottom > ar.bottom + 2) || (clipX && rect.right > ar.right + 2))) {
          report('text-clipped', 'warn', 'Text is cut off by a container with overflow hidden (fixed height or width).', { selector: selectorOf(el), text: snippet(text, 50) });
        }
        break;
      }

      if (size < 12 && !/^(SUP|SUB)$/.test(el.tagName)) report('text-tiny', 'warn', 'Text smaller than 12px.', { selector: selectorOf(el), text: snippet(text, 40), detail: `${round(size)}px` });
      if (cs.textTransform === 'uppercase' && parseFloat(cs.letterSpacing) / size > 0.04 && size <= 14) uppercaseLabels += 1;

      if (el.closest('td, th') && text.length <= 16 && lineCount(t.nodes) >= 2) {
        report('cell-wrap', 'info', 'Short table values wrap onto two lines; keep dates, amounts, and statuses on one line or change the layout on narrow screens.', { selector: selectorOf(el), text: snippet(text, 30) });
      }

      if (/^(P|LI|DD|BLOCKQUOTE|FIGCAPTION)$/.test(el.tagName) && text.length > 160) {
        const lines = lineCount(t.nodes);
        if (lines >= 2 && text.length / lines > 95) {
          report('measure-long', 'warn', 'Running text lines are too long (> ~90 characters); cap at ~65ch.', { selector: selectorOf(el), detail: `~${Math.round(text.length / lines)} chars/line` });
        }
        const lh = cs.lineHeight === 'normal' ? 1.2 : parseFloat(cs.lineHeight) / size;
        if (lh < 1.35) report('leading-tight', 'warn', 'Running text line-height below 1.35; use ~1.5–1.65.', { selector: selectorOf(el), detail: `${round(lh, 2)}` });
        if (size < 14) report('body-small', 'info', 'Running text below 14px.', { selector: selectorOf(el), detail: `${round(size)}px` });
      }

      if ((/^(H[1-6]|BUTTON|A|LABEL|TH|SUMMARY)$/.test(el.tagName) && EMOJI.test(text)) || (el.tagName === 'LI' && EMOJI_START.test(text))) {
        report('emoji-ui', 'warn', 'Emoji used as icons or bullets in headings, controls, or lists; use one icon set.', { selector: selectorOf(el), text: snippet(text, 40) });
      }
    }
    if (unknownContrast) report('contrast-unverified', 'info', `${unknownContrast} text elements sit on images or gradients; verify their contrast in the screenshots.`);
    if (uppercaseLabels > 6) report('eyebrow-overuse', 'info', `${uppercaseLabels} small uppercase tracked labels; eyebrow labels lose meaning when everything has one.`);

    // -- copy quality
    const fullText = pageText.join('\n');
    for (const [pattern, label] of PLACEHOLDER_PATTERNS) {
      const m = fullText.match(pattern);
      if (m) report('placeholder-copy', 'warn', 'Placeholder content is visible; write real, domain-specific copy.', { detail: `${label}: "${snippet(m[0], 40)}"` });
    }
    const lower = fullText.toLowerCase();
    const cliches = CLICHES.filter((c) => lower.includes(c));
    if (cliches.length) report('cliche-copy', 'info', 'Generic marketing phrases; replace with concrete specifics from the product.', { detail: cliches.slice(0, 8).join(', ') });

    // -- overlap of text and controls
    // Compare line boxes, not bounding boxes: run-in headings and wrapped inline text share lines legitimately.
    const items = texts.flatMap((t) => t.lines.map((r) => ({ el: t.el, r })))
      .concat(interactive.map((el) => ({ el, r: plainRect(el.getBoundingClientRect()), control: true })))
      .slice(0, 8000);
    items.sort((a, b) => a.r.top - b.r.top);
    let overlapCount = 0;
    const overlapSeen = new Set();
    for (let i = 0; i < items.length && overlapCount < 50; i += 1) {
      const A = items[i];
      for (let j = i + 1; j < items.length; j += 1) {
        const B = items[j];
        if (B.r.top >= A.r.bottom) break;
        if (A.el === B.el || A.el.contains(B.el) || B.el.contains(A.el)) continue;
        const ix = Math.min(A.r.right, B.r.right) - Math.max(A.r.left, B.r.left);
        const iy = Math.min(A.r.bottom, B.r.bottom) - Math.max(A.r.top, B.r.top);
        if (ix <= 2 || iy <= 2) continue;
        const ratio = (ix * iy) / Math.min(A.r.width * A.r.height, B.r.width * B.r.height);
        if (ratio < 0.25) continue;
        // Stretched-link overlays (an absolutely positioned link covering a card) are intentional.
        const overlay = [A, B].some((x) => x.control && getComputedStyle(x.el).position === 'absolute' && !visibleTextOf(x.el));
        if (overlay) continue;
        const pairKey = `${selectorOf(A.el)}|${selectorOf(B.el)}`;
        if (overlapSeen.has(pairKey)) continue;
        overlapSeen.add(pairKey);
        overlapCount += 1;
        report('overlap', 'warn', 'Text or controls overlap each other.', { selector: `${selectorOf(A.el)}  ⟂  ${selectorOf(B.el)}`, text: snippet(`${A.el.textContent} | ${B.el.textContent}`, 60) });
      }
    }

    // -- fixed chrome covering the viewport
    let fixedHeight = 0;
    for (const el of allElements) {
      const cs = getComputedStyle(el);
      if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
      if (!isRendered(el)) continue;
      const r = el.getBoundingClientRect();
      const pinned = cs.position === 'fixed' || r.top <= 1 || r.bottom >= vh - 1;
      if (pinned && r.width >= vw * 0.6 && r.bottom > 0 && r.top < vh && r.height < vh * 0.9) fixedHeight += Math.min(r.bottom, vh) - Math.max(r.top, 0);
    }
    if (fixedHeight > vh * (narrow ? 0.3 : 0.25)) {
      report('fixed-chrome', 'warn', `Fixed/sticky bars cover ${Math.round((fixedHeight / vh) * 100)}% of the viewport.`);
    }

    // -- controls: names, labels, targets, dead links
    const targets = [];
    for (const el of interactive) {
      const tag = el.tagName;
      const type = (el.getAttribute('type') || '').toLowerCase();
      const { name, placeholderOnly } = accessibleName(el);
      const isField = (tag === 'INPUT' && !['submit', 'button', 'reset', 'image'].includes(type)) || tag === 'SELECT' || tag === 'TEXTAREA';
      const native = /^(A|BUTTON|INPUT|SELECT|TEXTAREA|SUMMARY)$/.test(tag) || el.hasAttribute('role');
      if (!name && isField) {
        report('field-unlabeled', 'error', 'Form field has no label.', { selector: selectorOf(el), detail: el.outerHTML.slice(0, 90) });
      } else if (!name && native) {
        report('control-unnamed', 'error', 'Control has no accessible name (icon-only button or empty link?).', { selector: selectorOf(el), detail: el.outerHTML.slice(0, 90) });
      } else if (!name) {
        report('focusable-unnamed', 'warn', 'Focusable element (tabindex) has no accessible name or role.', { selector: selectorOf(el) });
      } else if (placeholderOnly && isField) {
        report('placeholder-as-label', 'warn', 'Placeholder used as the only label; it disappears while typing.', { selector: selectorOf(el), detail: name });
      }
      if (tag === 'A' && /^rgb\((0, 0, 238|85, 26, 139)\)$/.test(getComputedStyle(el).color)) {
        report('default-link-style', 'info', 'Links still use the browser default blue/purple; style them from the palette.', { selector: selectorOf(el), text: snippet(el.textContent, 30) });
      }
      if (tag === 'A') {
        const href = (el.getAttribute('href') || '').trim();
        if (href === '#' || href === '' || /^javascript:/i.test(href)) report('dead-link', 'warn', 'Placeholder link (href="#" or javascript:); wire it up or use a button.', { selector: selectorOf(el), text: snippet(el.textContent, 40) });
      }
      const cs = getComputedStyle(el);
      if (tag === 'A' && cs.display === 'inline') {
        const parentText = (el.parentElement && el.parentElement.textContent) || '';
        if (parentText.trim().length > el.textContent.trim().length + 10) continue; // inline link in a sentence: exempt
      }
      let r = el.getBoundingClientRect();
      if (tag === 'INPUT' && ['checkbox', 'radio'].includes(type) && el.labels && el.labels[0]) {
        const lr = el.labels[0].getBoundingClientRect();
        if (lr.width * lr.height > r.width * r.height) r = lr;
      }
      targets.push({ el, r, cx: r.left + r.width / 2, cy: r.top + r.height / 2, small: r.width < 24 || r.height < 24, isField });
      if (narrow && isField && parseFloat(cs.fontSize) < 16) report('input-zoom', 'warn', 'Inputs below 16px make iOS Safari zoom on focus.', { selector: selectorOf(el), detail: cs.fontSize });
    }
    let smallTouch = 0;
    for (const t of targets) {
      if (narrow && Math.min(t.r.width, t.r.height) < 40) smallTouch += 1;
      if (!t.small) continue;
      const crowded = targets.some((o) => {
        if (o === t || o.el.contains(t.el) || t.el.contains(o.el)) return false;
        if (o.small) return Math.hypot(o.cx - t.cx, o.cy - t.cy) < 24;
        const dx = Math.max(o.r.left - t.cx, 0, t.cx - o.r.right);
        const dy = Math.max(o.r.top - t.cy, 0, t.cy - o.r.bottom);
        return Math.hypot(dx, dy) < 12;
      });
      if (crowded) report('target-size', 'warn', 'Target smaller than 24×24px and crowded by neighbours (WCAG 2.2 target size).', { selector: selectorOf(t.el), detail: `${Math.round(t.r.width)}×${Math.round(t.r.height)}` });
    }
    if (smallTouch) report('touch-target', 'info', `${smallTouch} controls are under 40px on a touch viewport; 44px is the comfortable minimum.`);

    // -- fake controls: look clickable but are not buttons or links
    const CONTROL_ANCESTOR = 'a[href], button, label, summary, select, [role="button"], [role="link"], [role="tab"], [role="menuitem"], [role="option"], [role="checkbox"], [role="switch"], [role="radio"]';
    for (const el of allElements) {
      if (SKIP_TAGS.has(el.tagName) || el.matches(INTERACTIVE_SELECTOR) || el.closest(CONTROL_ANCESTOR)) continue;
      const inline = el.hasAttribute('onclick');
      const pointer = getComputedStyle(el).cursor === 'pointer';
      if (!inline && !pointer) continue;
      if (!inline && el.parentElement && getComputedStyle(el.parentElement).cursor === 'pointer') continue;
      if (!isRendered(el)) continue;
      report('fake-control', inline ? 'error' : 'warn', 'Looks clickable (onclick or pointer cursor) but is not a button or link; keyboard and screen-reader users cannot use it.', {
        selector: selectorOf(el), text: snippet(el.textContent, 40),
      });
    }

    // -- images
    for (const img of document.images) {
      if (!img.hasAttribute('alt')) report('img-alt-missing', 'error', 'Image without alt attribute (use alt="" if decorative).', { selector: selectorOf(img), detail: (img.currentSrc || img.src || '').split('/').pop().slice(0, 60) });
      if (img.complete && img.naturalWidth === 0 && (img.currentSrc || img.src)) report('img-broken', 'error', 'Broken image.', { selector: selectorOf(img), detail: (img.currentSrc || img.src).slice(0, 90) });
      if (!isRendered(img)) continue;
      const cs = getComputedStyle(img);
      if (!img.getAttribute('width') && !img.getAttribute('height') && cs.aspectRatio === 'auto') report('img-dimensions', 'info', 'Images without width/height or aspect-ratio can shift layout while loading.', { selector: selectorOf(img) });
      const rendered = img.getBoundingClientRect().width * (devicePixelRatio || 1);
      if (img.naturalWidth > 2.5 * rendered && img.naturalWidth > 1200) report('img-oversized', 'info', 'Image file is much larger than its rendered size.', { selector: selectorOf(img), detail: `${img.naturalWidth}px for ${Math.round(rendered)}px` });
    }

    // -- system consistency and generic-template signals
    const radii = new Map();
    const shadows = new Map();
    const hueBuckets = new Map();
    let gradientText = 0;
    let glass = 0;
    let glows = 0;
    let transitionAll = 0;
    let nestedCards = 0;
    let pills = 0;
    let purpleGradients = 0;
    const isCard = (cs) => parseFloat(cs.borderTopLeftRadius) >= 6 && (cs.boxShadow !== 'none' || parseFloat(cs.borderTopWidth) > 0)
      && (parseColor(cs.backgroundColor) || { a: 0 }).a > 0 && parseFloat(cs.paddingTop) >= 12;
    for (const el of allElements) {
      if (SKIP_TAGS.has(el.tagName)) continue;
      const cs = getComputedStyle(el);
      if (cs.display === 'none') continue;
      const radius = cs.borderTopLeftRadius;
      if (radius && radius !== '0px') radii.set(radius, (radii.get(radius) || 0) + 1);
      if (cs.boxShadow !== 'none') shadows.set(cs.boxShadow, (shadows.get(cs.boxShadow) || 0) + 1);
      if ((cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text') && /gradient/.test(cs.backgroundImage)) gradientText += 1;
      if (cs.backdropFilter && cs.backdropFilter !== 'none') glass += 1;
      const blur = cs.filter.match(/blur\(([\d.]+)px\)/);
      if (blur && parseFloat(blur[1]) >= 40) glows += 1;
      if (/(^|,\s*)all(,|$)/.test(cs.transitionProperty) && parseFloat(cs.transitionDuration) > 0) transitionAll += 1;
      if (/gradient/.test(cs.backgroundImage)) {
        const stops = (cs.backgroundImage.match(/rgba?\([^)]+\)|oklch\([^)]+\)|color\([^)]+\)/g) || []).map(parseColor).filter(Boolean).map(hsl);
        const purple = stops.filter((h) => h.s > 0.35 && h.h >= 235 && h.h <= 330).length;
        if (stops.length >= 2 && purple >= Math.ceil(stops.length / 2)) purpleGradients += 1;
      }
      for (const prop of ['color', 'backgroundColor', 'borderTopColor']) {
        if (prop === 'borderTopColor' && parseFloat(cs.borderTopWidth) === 0) continue;
        const c = parseColor(cs[prop]);
        if (!c || c.a < 0.5) continue;
        const h = hsl(c);
        if (h.s > 0.35 && h.l > 0.15 && h.l < 0.9) {
          const bucket = Math.round(h.h / 30) % 12;
          hueBuckets.set(bucket, (hueBuckets.get(bucket) || 0) + 1);
        }
      }
      if (/^(DIV|SECTION|ARTICLE|LI|ASIDE)$/.test(el.tagName) && isCard(cs)) {
        for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
          if (/^(DIV|SECTION|ARTICLE|LI|ASIDE)$/.test(a.tagName) && isCard(getComputedStyle(a))) { nestedCards += 1; break; }
        }
      }
      const r = el.getBoundingClientRect();
      const label = el.textContent.trim();
      if (r.height > 0 && r.height < 34 && parseFloat(radius) >= r.height / 2 - 1 && r.width > r.height * 1.6
        && label.length > 0 && label.length < 30 && !el.matches(INTERACTIVE_SELECTOR)) pills += 1;
    }
    const sizeCount = fontSizes.size;
    if (sizeCount > 8) report('type-scale-sprawl', 'warn', `${sizeCount} distinct font sizes; a coherent scale uses ~6 per view.`, { detail: Array.from(fontSizes.keys()).sort((a, b) => a - b).join(', ') });
    const primaries = new Map();
    for (const [stack, count] of families) {
      const primary = stack.split(',')[0].trim().replace(/^["']|["']$/g, '');
      primaries.set(primary, (primaries.get(primary) || 0) + count);
    }
    if (primaries.size > 3) report('font-family-sprawl', 'warn', `${primaries.size} font families in use; keep to two plus an optional mono.`, { detail: Array.from(primaries.keys()).join(', ') });
    for (const family of primaries.keys()) {
      const key = family.toLowerCase();
      if (GENERIC_FAMILIES.has(key) || OS_FONTS.has(key)) continue;
      if (!fontAvailable(family)) report('font-not-loaded', 'warn', 'A declared font is not available, so a fallback renders instead; load it or change the stack.', { detail: family });
    }
    for (const face of document.fonts || []) {
      if (face.status === 'error') report('font-not-loaded', 'warn', 'A declared font is not available, so a fallback renders instead; load it or change the stack.', { detail: `${face.family} (failed to load)` });
    }
    if (textColors.size > 12) report('color-sprawl', 'info', `${textColors.size} distinct text colors; route colors through a small token set.`);
    if (radii.size > 6) report('radius-sprawl', 'info', `${radii.size} distinct corner radii; use one radius scale.`, { detail: Array.from(radii.keys()).slice(0, 10).join(', ') });
    if (shadows.size > 5) report('shadow-sprawl', 'info', `${shadows.size} distinct shadows; keep to 2–3 elevation levels.`);
    if (hueBuckets.size > 4) report('accent-hue-sprawl', 'info', `${hueBuckets.size} distinct saturated hues; one accent plus semantic colors reads as a system.`);
    if (gradientText) report('gradient-text', 'info', `${gradientText} gradient-clipped text elements (a common generic-AI tell unless it is the brand).`);
    if (purpleGradients) report('purple-gradient', 'info', `${purpleGradients} purple/indigo gradients (the most common generic-AI palette); confirm the brief asks for it.`);
    if (glass > 2) report('glass-overuse', 'info', `${glass} backdrop-filter (glass) surfaces.`);
    if (glows) report('glow-decoration', 'info', `${glows} heavily blurred decorative shapes (glow orbs/blobs).`);
    if (transitionAll > 3) report('transition-all', 'info', `${transitionAll} elements transition "all"; name the properties you animate.`);
    if (nestedCards > 1) report('nested-cards', 'info', `${nestedCards} card-styled boxes nested inside other cards; flatten with spacing and dividers.`);
    if (pills > 12) report('pill-overuse', 'info', `${pills} pill/badge shapes; badges stop signalling anything when everything has one.`);

    // -- motion
    let infinite = 0;
    if (document.getAnimations) {
      for (const a of document.getAnimations()) {
        const timing = a.effect && a.effect.getTiming ? a.effect.getTiming() : {};
        if (a.playState === 'running' && timing.iterations === Infinity) infinite += 1;
      }
    }
    if (infinite > 2) report('infinite-animation', 'info', `${infinite} infinitely looping animations; constant motion competes with content.`);

    // -- first viewport
    const foldHeadings = headings.filter((h) => { const r = h.el.getBoundingClientRect(); return r.top < vh && r.bottom > 0; });
    const foldControls = interactive.filter((el) => { const r = el.getBoundingClientRect(); return r.top < vh && r.bottom > 0; });
    if (!foldHeadings.length) report('fold-no-heading', 'info', 'No heading visible in the first viewport; the page purpose may be unclear at a glance.');

    const list = Array.from(issues.values());
    const order = { error: 0, warn: 1, info: 2 };
    list.sort((a, b) => order[a.severity] - order[b.severity] || b.count - a.count);
    const summary = { error: 0, warn: 0, info: 0 };
    for (const i of list) summary[i.severity] += 1;
    const body = document.body ? getComputedStyle(document.body) : null;
    return {
      tool: 'ui_audit',
      version: VERSION,
      url: location.href,
      title: document.title,
      viewport: { width: vw, height: vh, dpr: devicePixelRatio || 1, narrow },
      colorScheme: matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
      metrics: {
        documentHeight: docEl.scrollHeight,
        textElements: texts.length,
        controls: interactive.length,
        images: document.images.length,
        fontSizes: Object.fromEntries(Array.from(fontSizes.entries()).sort((a, b) => a[0] - b[0])),
        fontFamilies: Object.fromEntries(primaries),
        textColors: textColors.size,
        radii: Array.from(radii.keys()).slice(0, 12),
        shadows: shadows.size,
        saturatedHues: hueBuckets.size,
        headings: headings.slice(0, 30).map((h) => `h${h.level} ${h.text}`),
        firstViewport: { headings: foldHeadings.map((h) => `h${h.level} ${h.text}`).slice(0, 6), controls: foldControls.length },
        rootBackground: body ? body.backgroundColor : '',
        rootColor: body ? body.color : '',
        htmlBackground: getComputedStyle(docEl).backgroundColor,
      },
      issues: list,
      summary,
    };
  }

  globalThis.__uiAudit = audit;
  globalThis.__uiAuditSelector = selectorOf;
})();
