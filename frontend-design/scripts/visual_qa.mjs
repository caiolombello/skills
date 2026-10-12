#!/usr/bin/env node
// visual_qa.mjs — render pages at several widths and color schemes, capture
// screenshots, run ui_audit.js, walk keyboard focus, check reduced motion, and
// write report.json + report.md. Requires Node 18+ and Playwright (project-local,
// global, or NODE_PATH) with a Chromium build or a system Chrome/Edge.
import { createRequire } from 'node:module';
import { execFileSync, spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const VERSION = '1.0.0';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const AUDIT_SOURCE = fs.readFileSync(path.join(HERE, 'ui_audit.js'), 'utf8');

const HELP = `visual_qa.mjs ${VERSION} — screenshots + UI audit for agents and humans

Usage:
  node visual_qa.mjs --url http://localhost:5173/ [--url /pricing ...]
  node visual_qa.mjs --start "npm run dev" --url http://localhost:5173/
  node visual_qa.mjs --file ./index.html
  node visual_qa.mjs --serve ./dist [--url /about]

Options:
  --url URL           Page to check (repeatable). Paths starting with "/" are
                      resolved against --serve or the previous absolute URL.
  --file PATH         Local HTML file (repeatable).
  --serve DIR         Serve DIR on 127.0.0.1 (SPA fallback to index.html).
  --start CMD         Start a dev server, wait for the first --url to answer,
                      run, then stop it (log: <out>/server.log).
  --start-timeout MS  How long to wait for --start (default 90000).
  --widths LIST       Screenshot widths (default 390,768,1440).
  --audit-widths LIST Extra audit-only widths (default 320 for WCAG reflow).
  --themes MODE       auto | light | dark | light,dark (default auto: dark is
                      captured only when the page has a dark theme).
  --dark-class NAME   Class that turns on dark mode, set on <html> (e.g. dark).
  --dark-attr K=V     Attribute that turns on dark mode (e.g. data-theme=dark).
  --steps FILE        JSON steps for interaction states (see below).
  --storage-state F   Playwright storage state (cookies/localStorage) for pages
                      behind login, e.g. from: npx playwright codegen --save-storage=F URL
  --out DIR           Output root (default .ui-qa). Add it to .gitignore.
  --wait MS           Extra settle time after load (default 400).
  --wait-for SEL      Wait for a selector before capturing.
  --max-tiles N       Lower-page screenshots per page at the narrowest and
                      widest width, one viewport tall each (default 3).
  --no-full-page      Only capture the first viewport.
  --focus-steps N     Tab stops to inspect (default 30; 0 disables).
  --fail-on LEVEL     error | warn | never (default error) for the exit code.
  --executable-path P Browser binary (or PLAYWRIGHT_CHROMIUM_EXECUTABLE).
  --timeout MS        Navigation timeout (default 30000).
  --json              Print the JSON report path and summary only.

Steps file (runs at the narrowest and widest screenshot widths):
  [{"action":"click","selector":"text=Sign in"},
   {"action":"fill","selector":"#email","value":"not-an-email"},
   {"action":"press","key":"Enter"},
   {"action":"wait","ms":300},
   {"action":"capture","name":"login-error"},
   {"action":"route","url":"**/api/invoices*","json":[]},
   {"action":"reload"},
   {"action":"capture","name":"empty"}]
Actions: click, fill, press, hover, focus, wait, waitFor, scroll, goto, reload,
route (mock a request: json | body | status | delay | abort), capture.

Exit codes: 0 ok, 1 findings at --fail-on level, 2 setup problem.`;

// ------------------------------------------------------------------ args

function parseArgs(argv) {
  const opts = {
    urls: [], files: [], serve: null, widths: [390, 768, 1440], auditWidths: [320], themes: 'auto',
    steps: null, storageState: null, out: '.ui-qa', wait: 400, waitFor: null, maxTiles: 3, fullPage: true,
    start: null, startTimeout: 90000, darkClass: null, darkAttr: null,
    focusSteps: 30, failOn: 'error', executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || null,
    timeout: 30000, json: false,
  };
  const list = (v) => v.split(',').map((x) => Number(x.trim())).filter((n) => Number.isFinite(n) && n >= 200 && n <= 4000);
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = () => {
      if (i + 1 >= argv.length) throw new Error(`${arg} needs a value`);
      i += 1;
      return argv[i];
    };
    switch (arg) {
      case '--url': opts.urls.push(next()); break;
      case '--file': opts.files.push(next()); break;
      case '--serve': opts.serve = next(); break;
      case '--widths': opts.widths = list(next()); break;
      case '--audit-widths': opts.auditWidths = list(next()); break;
      case '--themes': opts.themes = next(); break;
      case '--steps': opts.steps = next(); break;
      case '--storage-state': opts.storageState = next(); break;
      case '--out': opts.out = next(); break;
      case '--wait': opts.wait = Number(next()); break;
      case '--wait-for': opts.waitFor = next(); break;
      case '--max-tiles': opts.maxTiles = Number(next()); break;
      case '--start': opts.start = next(); break;
      case '--start-timeout': opts.startTimeout = Number(next()); break;
      case '--dark-class': opts.darkClass = next(); break;
      case '--dark-attr': opts.darkAttr = next(); break;
      case '--no-full-page': opts.fullPage = false; break;
      case '--focus-steps': opts.focusSteps = Number(next()); break;
      case '--fail-on': opts.failOn = next(); break;
      case '--executable-path': opts.executablePath = next(); break;
      case '--timeout': opts.timeout = Number(next()); break;
      case '--json': opts.json = true; break;
      case '-h': case '--help': opts.help = true; break;
      default: throw new Error(`Unknown option: ${arg}`);
    }
  }
  if (!['error', 'warn', 'never'].includes(opts.failOn)) throw new Error('--fail-on must be error, warn or never');
  if (!opts.widths.length) throw new Error('--widths needs at least one width between 200 and 4000');
  if (opts.darkAttr && !/^[\w:-]+=.*$/.test(opts.darkAttr)) throw new Error('--dark-attr must look like name=value');
  if (opts.start && !opts.urls.some((u) => /^https?:\/\//i.test(u))) throw new Error('--start needs an absolute http(s) --url to wait for');
  for (const [flag, value] of [['--wait', opts.wait], ['--max-tiles', opts.maxTiles], ['--focus-steps', opts.focusSteps], ['--timeout', opts.timeout], ['--start-timeout', opts.startTimeout]]) {
    if (!Number.isFinite(value) || value < 0) throw new Error(`${flag} must be a non-negative number`);
  }
  return opts;
}

// ------------------------------------------------------------------ setup

async function loadPlaywright() {
  const bases = [path.join(process.cwd(), 'noop.js'), path.join(HERE, 'noop.js')];
  try {
    const root = execFileSync('npm', ['root', '-g'], {
      encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], shell: process.platform === 'win32', timeout: 15000,
    }).trim();
    if (root) bases.push(path.join(root, 'noop.js'));
  } catch { /* npm unavailable: skip global lookup */ }
  for (const base of bases) {
    const require = createRequire(base);
    for (const name of ['playwright', 'playwright-core', '@playwright/test']) {
      try {
        const mod = await import(pathToFileURL(require.resolve(name)).href);
        const pw = mod.chromium ? mod : mod.default;
        if (pw && pw.chromium) return pw;
      } catch { /* try the next candidate */ }
    }
  }
  return null;
}

async function launch(pw, executablePath) {
  const attempts = executablePath ? [{ executablePath }] : [{}, { channel: 'chrome' }, { channel: 'msedge' }];
  let lastError;
  for (const extra of attempts) {
    try {
      return await pw.chromium.launch({ headless: true, ...extra });
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}

const MIME = {
  '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8', '.js': 'text/javascript',
  '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp',
  '.avif': 'image/avif', '.ico': 'image/x-icon', '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf',
  '.otf': 'font/otf', '.mp4': 'video/mp4', '.webm': 'video/webm', '.txt': 'text/plain; charset=utf-8',
  '.wasm': 'application/wasm', '.map': 'application/json',
};

function serveDirectory(dir) {
  const root = path.resolve(dir);
  if (!fs.existsSync(root) || !fs.statSync(root).isDirectory()) throw new Error(`--serve directory not found: ${dir}`);
  const server = http.createServer((req, res) => {
    let pathname;
    try {
      pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    } catch {
      res.writeHead(400).end();
      return;
    }
    let file = path.resolve(root, `.${pathname}`);
    if (file !== root && !file.startsWith(root + path.sep)) {
      res.writeHead(403).end();
      return;
    }
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    if (!fs.existsSync(file) && !path.extname(pathname)) file = path.join(root, 'index.html');
    if (!fs.existsSync(file)) {
      res.writeHead(404).end('Not found');
      return;
    }
    res.writeHead(200, { 'content-type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => resolve({ server, origin: `http://127.0.0.1:${server.address().port}` }));
  });
}

function resolveTargets(opts, origin) {
  const targets = [];
  let base = origin;
  for (const url of opts.urls) {
    if (/^https?:\/\//i.test(url) || /^file:/i.test(url)) {
      targets.push(url);
      base = new URL(url).origin;
    } else if (base) {
      targets.push(new URL(url, `${base}/`).href);
    } else {
      throw new Error(`Relative --url ${url} needs --serve or an earlier absolute --url`);
    }
  }
  for (const file of opts.files) {
    const abs = path.resolve(file);
    if (!fs.existsSync(abs)) throw new Error(`--file not found: ${file}`);
    targets.push(pathToFileURL(abs).href);
  }
  if (!targets.length && origin) targets.push(`${origin}/`);
  return targets;
}

function slugFor(url, used) {
  const u = new URL(url);
  let slug = u.protocol === 'file:' ? path.basename(u.pathname).replace(/\.[^.]+$/, '') : u.pathname.replace(/^\/+|\/+$/g, '');
  slug = (slug || 'home').replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').toLowerCase().slice(0, 40) || 'page';
  let unique = slug;
  for (let n = 2; used.has(unique); n += 1) unique = `${slug}-${n}`;
  used.add(unique);
  return unique;
}

const heightFor = (width) => (width <= 360 ? 640 : width <= 480 ? 844 : width <= 900 ? 1024 : 900);

async function startServer(command, url, timeoutMs, logFile) {
  const log = fs.openSync(logFile, 'a');
  const child = spawn(command, { shell: true, detached: process.platform !== 'win32', stdio: ['ignore', log, log] });
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (child.exitCode !== null) throw new Error(`--start command exited with code ${child.exitCode}; see ${logFile}`);
    try {
      const res = await fetch(url, { redirect: 'manual' });
      if (res.status < 500) return child;
    } catch { /* not listening yet */ }
    await new Promise((r) => setTimeout(r, 500));
  }
  stopServer(child);
  throw new Error(`--start: ${url} did not answer within ${timeoutMs}ms; see ${logFile}`);
}

function stopServer(child) {
  if (!child || child.exitCode !== null) return;
  try {
    if (process.platform === 'win32') execFileSync('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' });
    else process.kill(-child.pid, 'SIGTERM');
  } catch { /* already stopped */ }
}

// ------------------------------------------------------------------ page helpers

const INIT_SCRIPT = `(() => {
  window.__uiQaCls = 0;
  try {
    new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) if (!entry.hadRecentInput) window.__uiQaCls += entry.value;
    }).observe({ type: 'layout-shift', buffered: true });
  } catch (e) {}
})();`;

async function openPage(browser, url, opts, { width, theme = 'light', reducedMotion = 'no-preference' }) {
  const narrow = width <= 480;
  const context = await browser.newContext({
    viewport: { width, height: heightFor(width) }, deviceScaleFactor: 1, isMobile: narrow, hasTouch: narrow,
    colorScheme: theme, reducedMotion, bypassCSP: true,
    ...(opts.storageState ? { storageState: opts.storageState } : {}),
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];
  const ignored = (url) => /\/favicon\.ico(\?|$)/.test(url);
  page.on('console', (msg) => {
    // Resource failures are reported from the network events instead.
    if (msg.type() === 'error' && !/^Failed to load resource/.test(msg.text())) consoleErrors.push(msg.text().slice(0, 300));
  });
  page.on('pageerror', (err) => pageErrors.push(String(err && err.message ? err.message : err).slice(0, 300)));
  page.on('requestfailed', (req) => {
    const reason = req.failure() ? req.failure().errorText : 'failed';
    if (!/ERR_ABORTED|NS_BINDING_ABORTED/.test(reason) && !ignored(req.url())) failedRequests.push(`${reason} ${req.url().slice(0, 200)}`);
  });
  page.on('response', (res) => { if (res.status() >= 400 && !ignored(res.url())) failedRequests.push(`${res.status()} ${res.url().slice(0, 200)}`); });
  await page.addInitScript(INIT_SCRIPT);
  await page.goto(url, { waitUntil: 'load', timeout: opts.timeout });
  try { await page.waitForLoadState('networkidle', { timeout: 5000 }); } catch { /* long-polling pages never idle */ }
  if (opts.waitFor) await page.waitForSelector(opts.waitFor, { timeout: opts.timeout });
  if (theme === 'dark' && (opts.darkClass || opts.darkAttr)) {
    await page.evaluate(({ cls, attr }) => {
      if (cls) document.documentElement.classList.add(cls);
      if (attr) {
        const at = attr.indexOf('=');
        document.documentElement.setAttribute(attr.slice(0, at), attr.slice(at + 1));
      }
    }, { cls: opts.darkClass, attr: opts.darkAttr });
  }
  await page.evaluate(() => (document.fonts ? document.fonts.ready.then(() => true) : true));
  await page.waitForTimeout(opts.wait);
  return { context, page, consoleErrors, pageErrors, failedRequests };
}

async function revealLazyContent(page) {
  // Scroll through once so lazy images and reveal-on-scroll sections render, then settle at the top.
  await page.evaluate(async () => {
    const step = Math.max(200, Math.floor(innerHeight * 0.8));
    const limit = Math.min(document.documentElement.scrollHeight, 40000);
    for (let y = 0; y < limit; y += step) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 60));
    }
    window.scrollTo(0, 0);
    await new Promise((r) => setTimeout(r, 120));
  });
}

async function finishAnimations(page) {
  await page.evaluate(() => {
    for (const a of document.getAnimations ? document.getAnimations() : []) {
      try {
        const timing = a.effect && a.effect.getTiming ? a.effect.getTiming() : {};
        if (timing.iterations !== Infinity) {
          a.finish();
        } else {
          // Measure loops at their resting frame, as the screenshots do.
          a.pause();
          a.currentTime = 0;
        }
      } catch { /* some animations cannot finish */ }
    }
  });
}

async function runAudit(page, narrow) {
  await page.evaluate(AUDIT_SOURCE);
  return page.evaluate((n) => globalThis.__uiAudit({ narrow: n }), narrow);
}

async function screenshot(page, file) {
  await page.screenshot({ path: file, animations: 'disabled', caret: 'hide' });
  return { path: file };
}

// Lower sections as viewport-sized tiles: one tall image shrinks to an unreadable strip
// when a model or a chat viewer scales it down.
async function tiles(page, base, width, max) {
  const vh = page.viewportSize().height;
  const total = await page.evaluate(() => Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0));
  const available = Math.max(0, Math.ceil(total / vh) - 1);
  const files = [];
  for (let i = 1; i <= Math.min(max, available); i += 1) {
    const y = i * vh;
    const height = Math.min(vh, total - y);
    if (height < 40) break;
    const file = `${base}-${i + 1}.png`;
    await page.screenshot({ path: file, fullPage: true, clip: { x: 0, y, width, height }, animations: 'disabled', caret: 'hide' });
    files.push(file);
  }
  return { files, omitted: Math.max(0, available - files.length) };
}

async function focusWalk(page, maxSteps) {
  if (!maxSteps) return [];
  await page.evaluate(() => {
    window.scrollTo(0, 0);
    if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
  });
  const stops = [];
  const seen = new Set();
  for (let i = 0; i < maxSteps; i += 1) {
    await page.keyboard.press('Tab');
    await page.waitForTimeout(60);
    const info = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body || el === document.documentElement) return null;
      const sel = globalThis.__uiAuditSelector ? globalThis.__uiAuditSelector(el) : el.tagName.toLowerCase();
      const chain = [el, el.parentElement, el.parentElement && el.parentElement.parentElement].filter(Boolean);
      const read = () => chain.map((node) => {
        const s = getComputedStyle(node);
        const after = getComputedStyle(node, '::after');
        const before = getComputedStyle(node, '::before');
        return [s.outlineStyle, s.outlineWidth, s.outlineColor, s.boxShadow, s.borderTopColor, s.borderBottomColor,
          s.borderBottomWidth, s.backgroundColor, s.color, s.textDecorationLine, after.boxShadow, after.outlineStyle,
          after.opacity, after.borderTopColor, before.boxShadow, before.opacity].join('|');
      }).join('#');
      const s = getComputedStyle(el);
      const hasOutline = s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0;
      const focused = read();
      const r = el.getBoundingClientRect();
      const inset = Math.min(2, r.width / 4, r.height / 4);
      const points = [[r.left + r.width / 2, r.top + r.height / 2], [r.left + inset, r.top + inset], [r.right - inset, r.top + inset],
        [r.left + inset, r.bottom - inset], [r.right - inset, r.bottom - inset]];
      let coveredPoints = 0;
      let obscuredBy = null;
      for (const [x, y] of points) {
        if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) continue;
        const top = document.elementFromPoint(x, y);
        if (!top || top === el || el.contains(top) || top.contains(el)) continue;
        for (let n = top; n; n = n.parentElement) {
          const p = getComputedStyle(n).position;
          if (p === 'fixed' || p === 'sticky') {
            coveredPoints += 1;
            obscuredBy = globalThis.__uiAuditSelector ? globalThis.__uiAuditSelector(top) : top.tagName.toLowerCase();
            break;
          }
        }
      }
      const obscured = coveredPoints === 0 ? null : coveredPoints === points.length ? 'full' : 'partial';
      el.blur();
      const blurred = read();
      el.focus({ preventScroll: true });
      const name = (el.getAttribute('aria-label') || el.innerText || el.value || el.getAttribute('title') || '').trim().replace(/\s+/g, ' ').slice(0, 50);
      return { selector: sel, tag: el.tagName.toLowerCase(), name, visible: focused !== blurred, hasOutline, obscured, obscuredBy, key: `${sel}@${Math.round(r.x)},${Math.round(r.y + scrollY)}` };
    });
    if (!info || seen.has(info.key)) break;
    seen.add(info.key);
    stops.push(info);
  }
  return stops;
}

async function runSteps(page, steps, capture) {
  for (const step of steps) {
    switch (step.action) {
      case 'click': await page.click(step.selector); break;
      case 'fill': await page.fill(step.selector, String(step.value ?? '')); break;
      case 'press': await page.keyboard.press(step.key); break;
      case 'hover': await page.hover(step.selector); break;
      case 'focus': await page.focus(step.selector); break;
      case 'wait': await page.waitForTimeout(Number(step.ms) || 300); break;
      case 'waitFor': await page.waitForSelector(step.selector); break;
      case 'scroll':
        if (step.selector) await page.locator(step.selector).first().scrollIntoViewIfNeeded();
        else await page.evaluate((y) => window.scrollTo(0, y), Number(step.y) || 0);
        break;
      case 'goto': await page.goto(new URL(step.url, page.url()).href, { waitUntil: 'load' }); break;
      case 'reload': await page.reload({ waitUntil: 'load' }); break;
      case 'route': {
        // Mock a request to render empty, error, or loading states without touching the backend.
        const json = step.json !== undefined;
        await page.route(step.url, async (route) => {
          if (step.delay) await new Promise((r) => setTimeout(r, Number(step.delay)));
          try {
            if (step.abort) await route.abort();
            else await route.fulfill({ status: Number(step.status) || 200, contentType: json ? 'application/json' : (step.contentType || 'text/plain'), body: json ? JSON.stringify(step.json) : String(step.body ?? '') });
          } catch { /* page closed while the mock was pending */ }
        });
        break;
      }
      case 'capture': await capture(step.name || 'state'); break;
      default: throw new Error(`Unknown step action: ${step.action}`);
    }
  }
}

// ------------------------------------------------------------------ main

function mergeFindings(target) {
  const merged = new Map();
  const add = (issue, where) => {
    const key = issue.id;
    if (!merged.has(key)) merged.set(key, { id: issue.id, severity: issue.severity, message: issue.message, count: 0, where: [], examples: [] });
    const m = merged.get(key);
    const rank = { error: 0, warn: 1, info: 2 };
    if (rank[issue.severity] < rank[m.severity]) m.severity = issue.severity;
    m.count = Math.max(m.count, issue.count || 1);
    if (!m.where.includes(where)) m.where.push(where);
    for (const ex of issue.examples || []) {
      const sig = JSON.stringify(ex);
      if (m.examples.length < 6 && !m.examples.some((e) => JSON.stringify(e) === sig)) m.examples.push(ex);
    }
  };
  for (const run of target.runs) {
    const where = `${run.width}px ${run.theme}${run.state ? ` ${run.state}` : ''}`;
    for (const issue of run.audit.issues) add(issue, where);
    if (run.cls > 0.1) add({ id: 'layout-shift', severity: 'warn', message: `Cumulative layout shift ${run.cls.toFixed(3)} during load (> 0.1).`, count: 1 }, where);
    const crashes = Array.from(new Set(run.pageErrors || []));
    if (crashes.length) add({ id: 'page-error', severity: 'error', message: 'Uncaught exceptions while rendering.', count: crashes.length, examples: crashes.map((detail) => ({ detail })) }, where);
    const errors = Array.from(new Set(run.consoleErrors || []));
    if (errors.length) add({ id: 'console-error', severity: 'warn', message: 'console.error output while rendering (framework warnings, failed calls).', count: errors.length, examples: errors.map((detail) => ({ detail })) }, where);
    const failures = Array.from(new Set(run.failedRequests || []));
    if (failures.length) add({ id: 'request-failed', severity: 'warn', message: 'Failed network requests (missing assets, fonts, or API calls).', count: failures.length, examples: failures.map((detail) => ({ detail })) }, where);
  }
  const unfocusable = target.focus.filter((s) => !s.visible);
  if (unfocusable.length) add({ id: 'focus-invisible', severity: 'error', message: 'Keyboard focus is not visible on these elements (WCAG 2.4.7).', count: unfocusable.length, examples: unfocusable.slice(0, 6).map((s) => ({ selector: s.selector, text: s.name })) }, 'keyboard');
  const hidden = target.focus.filter((s) => s.obscured === 'full');
  if (hidden.length) add({ id: 'focus-obscured', severity: 'warn', message: 'Focused elements are completely hidden behind fixed/sticky UI (WCAG 2.4.11).', count: hidden.length, examples: hidden.slice(0, 6).map((s) => ({ selector: s.selector, detail: `under ${s.obscuredBy}` })) }, 'keyboard');
  const partly = target.focus.filter((s) => s.obscured === 'partial');
  if (partly.length) add({ id: 'focus-partly-obscured', severity: 'info', message: 'Focused elements are partly covered by fixed/sticky UI (heuristic; check scroll-padding).', count: partly.length, examples: partly.slice(0, 6).map((s) => ({ selector: s.selector, detail: `under ${s.obscuredBy}` })) }, 'keyboard');
  if (target.reducedMotion && target.reducedMotion.length) add({ id: 'reduced-motion-ignored', severity: 'warn', message: 'Animations keep running with prefers-reduced-motion: reduce.', count: target.reducedMotion.length, examples: target.reducedMotion.slice(0, 6) }, 'reduced motion');
  const rank = { error: 0, warn: 1, info: 2 };
  return Array.from(merged.values()).sort((a, b) => rank[a.severity] - rank[b.severity] || b.count - a.count);
}

function toMarkdown(report) {
  const lines = [`# Visual QA report`, '', `Generated ${report.createdAt} by visual_qa.mjs ${VERSION}.`, ''];
  lines.push(`Summary: **${report.summary.error} error**, **${report.summary.warn} warn**, ${report.summary.info} info finding types.`, '');
  lines.push('Open the screenshots in this order (first viewports, states and dark theme, then lower sections), describe what you see, then score the critique rubric:', '');
  for (const shot of report.viewOrder) lines.push(`- ${shot}`);
  for (const target of report.targets) {
    lines.push('', `## ${target.slug} — ${target.url}`, '');
    lines.push(`Dark theme: ${target.darkSupported ? 'detected' : 'not detected'}. Focus stops inspected: ${target.focus.length}.`, '');
    const metrics = target.runs.find((r) => !r.state && r.theme === 'light' && r.width === Math.max(...report.widths))?.audit.metrics;
    if (metrics) {
      lines.push(`Desktop metrics: ${Object.keys(metrics.fontSizes).length} font sizes (${Object.keys(metrics.fontSizes).join(', ')}px); families ${Object.keys(metrics.fontFamilies).join(', ')}; ${metrics.textColors} text colors; ${metrics.saturatedHues} saturated hues; radii ${metrics.radii.join(', ') || 'none'}.`, '');
      if (metrics.headings.length) lines.push(`Headings: ${metrics.headings.slice(0, 12).join(' · ')}`, '');
    }
    lines.push('| Severity | Finding | Seen at | Examples |', '|---|---|---|---|');
    for (const f of target.findings) {
      const examples = f.examples.slice(0, 3).map((e) => [e.selector, e.text && `"${e.text}"`, e.detail].filter(Boolean).join(' — ')).join('<br>');
      lines.push(`| ${f.severity} | **${f.id}** — ${f.message} (${f.count}) | ${f.where.join(', ')} | ${examples.replace(/\|/g, '\\|')} |`);
    }
  }
  return `${lines.join('\n')}\n`;
}

async function main() {
  let opts;
  try {
    opts = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(`visual_qa: ${error.message}\n\n${HELP}`);
    process.exit(2);
  }
  if (opts.help || (!opts.urls.length && !opts.files.length && !opts.serve)) {
    console.log(HELP);
    process.exit(opts.help ? 0 : 2);
  }
  const pw = await loadPlaywright();
  if (!pw) {
    console.error('visual_qa: Playwright not found. Install it in the project or globally:\n  npm i -D playwright && npx playwright install chromium\nor point NODE_PATH at a node_modules that contains it.');
    process.exit(2);
  }
  let steps = null;
  if (opts.steps) steps = JSON.parse(fs.readFileSync(opts.steps, 'utf8'));
  if (opts.storageState && !fs.existsSync(opts.storageState)) {
    console.error(`visual_qa: --storage-state file not found: ${opts.storageState}`);
    process.exit(2);
  }
  let served = null;
  let browser = null;
  let server = null;
  process.on('exit', () => stopServer(server));
  for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => { stopServer(server); process.exit(130); });
  try {
    const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\..+$/, '').replace('T', '-');
    const outDir = path.resolve(opts.out, stamp);
    fs.mkdirSync(outDir, { recursive: true });
    if (opts.serve) served = await serveDirectory(opts.serve);
    const targets = resolveTargets(opts, served && served.origin);
    if (opts.start) {
      try {
        server = await startServer(opts.start, opts.urls.find((u) => /^https?:\/\//i.test(u)), opts.startTimeout, path.join(outDir, 'server.log'));
      } catch (error) {
        console.error(`visual_qa: ${error.message}`);
        process.exit(2);
      }
    }
    try {
      browser = await launch(pw, opts.executablePath);
    } catch (error) {
      console.error(`visual_qa: could not launch Chromium (${error.message.split('\n')[0]}).\nRun "npx playwright install chromium", or pass --executable-path to a Chrome/Chromium binary.`);
      process.exit(2);
    }
    const shotWidths = Array.from(new Set(opts.widths)).sort((a, b) => a - b);
    const allWidths = Array.from(new Set([...shotWidths, ...opts.auditWidths])).sort((a, b) => a - b);
    const minW = shotWidths[0];
    const maxW = shotWidths[shotWidths.length - 1];
    const used = new Set();
    const report = { tool: 'visual_qa', version: VERSION, createdAt: new Date().toISOString(), outDir, widths: shotWidths, targets: [], viewOrder: [] };
    const rel = (p) => path.relative(process.cwd(), p) || p;

    for (const url of targets) {
      const slug = slugFor(url, used);
      const target = { url, slug, runs: [], focus: [], reducedMotion: [], darkSupported: false };
      const folds = [];
      const lower = [];
      let lightColors = null;

      for (const width of allWidths) {
        const { context, page, consoleErrors, pageErrors, failedRequests } = await openPage(browser, url, opts, { width });
        // Load-time shift only; the scroll-through below would add shifts no user caused.
        const cls = await page.evaluate(() => window.__uiQaCls || 0);
        await revealLazyContent(page);
        await finishAnimations(page);
        const audit = await runAudit(page, width <= 480);
        const run = { width, theme: 'light', audit, cls, consoleErrors, pageErrors, failedRequests, screenshots: {} };
        if (!lightColors) lightColors = `${audit.metrics.rootBackground}|${audit.metrics.rootColor}|${audit.metrics.htmlBackground}`;
        if (shotWidths.includes(width)) {
          const fold = await screenshot(page, path.join(outDir, `${slug}-${width}-light-fold.png`));
          run.screenshots.fold = rel(fold.path);
          folds.push(run.screenshots.fold);
          if (opts.fullPage && opts.maxTiles > 0 && (width === minW || width === maxW)) {
            const result = await tiles(page, path.join(outDir, `${slug}-${width}-light-part`), width, opts.maxTiles);
            run.screenshots.lower = result.files.map(rel);
            run.screenshots.omittedTiles = result.omitted;
            lower.push(...run.screenshots.lower);
          }
        }
        if (width === maxW) target.focus = await focusWalk(page, opts.focusSteps);
        target.runs.push(run);
        await context.close();

        if (steps && (width === minW || width === maxW)) {
          const session = await openPage(browser, url, opts, { width });
          await runSteps(session.page, steps, async (name) => {
            await finishAnimations(session.page);
            const stateAudit = await runAudit(session.page, width <= 480);
            const file = path.join(outDir, `${slug}-${width}-${name.replace(/[^a-z0-9-]+/gi, '-')}.png`);
            await screenshot(session.page, file);
            folds.push(rel(file));
            target.runs.push({ width, theme: 'light', state: name, audit: stateAudit, cls: 0, consoleErrors: [], pageErrors: [], failedRequests: [], screenshots: { fold: rel(file) } });
          });
          const base = target.runs.find((r) => r.width === width && !r.state);
          base.consoleErrors.push(...session.consoleErrors);
          base.pageErrors.push(...session.pageErrors);
          await session.context.close();
        }
      }

      const wantDark = opts.themes.includes('dark');
      const autoDark = opts.themes === 'auto';
      if (wantDark || autoDark) {
        for (const width of Array.from(new Set([minW, maxW]))) {
          const { context, page, consoleErrors, pageErrors, failedRequests } = await openPage(browser, url, opts, { width, theme: 'dark' });
          await finishAnimations(page);
          const audit = await runAudit(page, width <= 480);
          const darkColors = `${audit.metrics.rootBackground}|${audit.metrics.rootColor}|${audit.metrics.htmlBackground}`;
          target.darkSupported = target.darkSupported || darkColors !== lightColors;
          if (autoDark && !target.darkSupported) {
            await context.close();
            break;
          }
          const fold = await screenshot(page, path.join(outDir, `${slug}-${width}-dark-fold.png`));
          folds.push(rel(fold.path));
          target.runs.push({ width, theme: 'dark', audit, cls: 0, consoleErrors, pageErrors, failedRequests, screenshots: { fold: rel(fold.path) } });
          await context.close();
        }
      }

      {
        const { context, page } = await openPage(browser, url, opts, { width: maxW, reducedMotion: 'reduce' });
        await page.evaluate(AUDIT_SOURCE);
        target.reducedMotion = await page.evaluate(() => (document.getAnimations ? document.getAnimations() : [])
          .filter((a) => a.playState === 'running')
          .map((a) => {
            const timing = a.effect && a.effect.getTiming ? a.effect.getTiming() : {};
            const node = a.effect && a.effect.target;
            return { selector: node && globalThis.__uiAuditSelector ? globalThis.__uiAuditSelector(node) : (node ? node.tagName.toLowerCase() : ''), detail: `${a.animationName || a.transitionProperty || 'animation'} ${timing.iterations === Infinity ? 'infinite' : `${timing.duration}ms`}`, infinite: timing.iterations === Infinity, duration: Number(timing.duration) || 0 };
          })
          .filter((a) => a.infinite || a.duration > 1000));
        await context.close();
      }

      target.findings = mergeFindings(target);
      report.targets.push(target);
      report.viewOrder.push(...folds, ...lower);
    }

    const summary = { error: 0, warn: 0, info: 0 };
    for (const t of report.targets) for (const f of t.findings) summary[f.severity] += 1;
    report.summary = summary;
    const jsonPath = path.join(outDir, 'report.json');
    const mdPath = path.join(outDir, 'report.md');
    fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2));
    fs.writeFileSync(mdPath, toMarkdown(report));

    if (opts.json) {
      console.log(JSON.stringify({ report: rel(jsonPath), markdown: rel(mdPath), summary, viewOrder: report.viewOrder }, null, 2));
    } else {
      console.log(`visual_qa ${VERSION}: ${summary.error} error, ${summary.warn} warn, ${summary.info} info finding types`);
      for (const t of report.targets) {
        console.log(`\n${t.slug} (${t.url})`);
        for (const f of t.findings.filter((x) => x.severity !== 'info').slice(0, 15)) {
          const ex = f.examples[0];
          const hint = ex ? ` — ${[ex.selector, ex.text && `"${ex.text}"`, ex.detail].filter(Boolean).join(' ')}` : '';
          console.log(`  ${f.severity.toUpperCase().padEnd(5)} ${f.id} ×${f.count} [${f.where.join(', ')}] ${f.message}${hint}`);
        }
        const infos = t.findings.filter((x) => x.severity === 'info').map((x) => x.id);
        if (infos.length) console.log(`  INFO  ${infos.join(', ')}`);
      }
      console.log('\nView these screenshots (first viewports, states, dark theme, then lower sections):');
      for (const shot of report.viewOrder) console.log(`  ${shot}`);
      console.log(`\nReport: ${rel(mdPath)} (JSON: ${rel(jsonPath)})`);
    }
    const failing = opts.failOn === 'never' ? 0 : opts.failOn === 'warn' ? summary.error + summary.warn : summary.error;
    process.exitCode = failing ? 1 : 0;
  } finally {
    if (browser) await browser.close();
    if (served) served.server.close();
    stopServer(server);
  }
}

main().catch((error) => {
  console.error(`visual_qa: ${error && error.stack ? error.stack : error}`);
  process.exit(2);
});
