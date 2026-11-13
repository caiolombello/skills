# Technical SEO and indexability checklist

Reviewed 2026-11-13; re-verify against https://developers.google.com/search/docs/crawling-indexing. Collect evidence per template, not per URL.

## Crawlability

- `GET /robots.txt` returns 200 with plain text. A 5xx makes compliant crawlers assume the whole site is disallowed; 404 means no restrictions; Google treats 429 like a server error (RFC 9309 https://www.rfc-editor.org/rfc/rfc9309).
- No production `Disallow: /` (common leftover from staging). Check that CSS, JS, and API paths needed for rendering are not blocked.
- A crawler obeys only the most specific group naming its token; if a named group exists, the `*` group is ignored for it. Repeat shared rules in each named group. Match tokens whole and case-insensitively; use bare tokens (`GPTBot`, not `GPTBot/1.1`).
- `Sitemap:` lines use absolute URLs.
- robots.txt is public and advisory. It is not access control; protect private content with authentication.

## Indexability

- Meta robots (`<meta name="robots">`), bot-specific meta, and `X-Robots-Tag` headers. Check all three; headers also apply to PDFs and images. Look for `noindex` leaking from a staging env var, a layout default, or a CMS "discourage search engines" toggle.
- `noindex` only works if the page is crawlable. Do not also `Disallow` it.
- Canonical: one `rel=canonical`, absolute URL, correct scheme and host (www vs apex), self-referencing on indexable pages, not pointing to a redirected, noindexed, or 4xx URL. Canonical in the rendered DOM must match the raw HTML; conflicting values are ambiguous.
- Duplicate sources: trailing slash, case, query parameters (tracking, sort, session), http/https, www/non-www, index.html. Pick one form and redirect or canonicalize.
- Pagination: each page self-canonical and linked with crawlable `<a href>`; do not rely on infinite scroll without paginated URLs.
- Soft 404: pages that say "not found" or are empty but return 200. Unknown URLs must return a real 404 or 410.

## Redirects and status codes

- Use 301 or 308 for permanent moves, 302 or 307 for temporary. Flag chains (more than one hop), loops, and redirects to non-canonical targets.
- Internal links should point directly at the final URL.
- 200 on indexable pages; 404/410 for gone; 5xx and 429 signal trouble; check redirect from http to https and between host variants in a single hop.

## Sitemaps

- XML sitemap at a known path, referenced from robots.txt, and submitted by the owner in Search Console (submission is the owner's action, not the agent's).
- Only canonical, indexable, 200 URLs. No noindexed, redirected, or 404 URLs.
- Limits: 50,000 URLs or 50 MB uncompressed per file; use a sitemap index beyond that.
- `lastmod` is useful only if accurate (real content change), otherwise crawlers learn to ignore it. `priority` and `changefreq` are not relied on by Google.
- Image, video, and news sitemaps only when the site genuinely has that content.

## Hreflang

- Each language version lists all alternates including itself, with reciprocal links (A to B and B to A). Missing return links invalidate the pair.
- Valid codes: ISO 639-1 language, optional ISO 3166-1 region (`en-GB`, not `en-UK`). Add `x-default` for the fallback.
- Annotations in HTML head, HTTP headers, or sitemap, consistently, and URLs must be canonical and indexable.
- Do not use hreflang to merge unrelated pages; translated content should be real, not auto-generated filler.

## JavaScript rendering

- Compare raw HTML (`curl`) with rendered DOM. Titles, meta robots, canonicals, main content, and internal links should be present in the initial HTML for content pages.
- Client-side routers need real `<a href>` links and distinct URLs (no hash routing for content).
- Frameworks: in Next.js check `metadata`/`generateMetadata`, `robots` and `sitemap` route files, `next.config` redirects and headers, and that `noindex` is not set in a root layout or by an env condition leaking to production. In Nuxt, Astro, and others, check the equivalent head and route config.
- Googlebot renders JavaScript, but rendering is deferred and can fail; many other fetchers (including AI crawlers) do not render. SSR, SSG, or ISR for content routes.
- Avoid injecting or changing canonical and robots directives client-side after load.

## URL structure

- Short, lowercase, hyphenated, descriptive, stable. Avoid session IDs and unneeded parameters. Keep a logical hierarchy and minimal depth for important pages. Do not change URLs without 301 mapping.

## HTTPS and security signals

- Whole site served over HTTPS with a valid certificate, HTTP redirects to HTTPS, HSTS considered. No mixed content (http sub-resources), which browsers block or warn on. Defer header hardening depth to [`security-hardening`](../../security-hardening/SKILL.md).

## On-page signals

- One unique, descriptive `<title>` per page (roughly 50 to 60 characters displays well; length is a display heuristic, not a rule). Unique meta description written for people; Google may rewrite it.
- One clear `<h1>` matching the page topic, logical heading order. Headings should structure content, not decorate.
- Descriptive internal links with meaningful anchor text; important pages reachable within a few clicks and not orphaned (compare sitemap URLs with links found).
- Images: meaningful `alt` text (empty `alt=""` for decorative), explicit `width` and `height`, modern formats, responsive `srcset`, lazy-load below the fold but not the LCP image, descriptive filenames.
- `lang` attribute on `<html>`, viewport meta, mobile-friendly content parity (Google uses mobile-first indexing).

## Core Web Vitals as a discoverability signal

Reviewed 2026-11-13; re-verify at https://web.dev/articles/vitals.

| Metric | Good | Needs improvement | Poor |
|---|---|---|---|
| LCP | at most 2.5 s | up to 4.0 s | over 4.0 s |
| INP | at most 200 ms | up to 500 ms | over 500 ms |
| CLS | at most 0.1 | up to 0.25 | over 0.25 |

- INP replaced FID in March 2024. FID is no longer a Core Web Vital. Treat claims of other new "core" metrics or tightened thresholds as unverified until seen on web.dev.
- Assessment uses the 75th percentile of real-user (field) data, from CrUX, PageSpeed Insights field section, or Search Console. Lab data (Lighthouse, DevTools, WebPageTest) is for diagnosis and can disagree with field data. Always state which one a number came from. Low-traffic pages may have no field data; say so rather than substituting lab numbers as a verdict.
- Page experience is one of many signals; do not claim it overrides relevance.
- For root-cause fixes (profiling, bundle, server timing), hand off to [`performance-optimization`](../../performance-optimization/SKILL.md).

## Content quality and E-E-A-T (reviewer heuristics)

Google describes experience, expertise, authoritativeness, and trust as concepts its quality raters use, not a ranking factor you can score. Reviewers can check:

- Who: visible author or organization, bio, contact and about pages, editorial or review policy where relevant, sources cited.
- How: original information, first-hand experience or testing where claimed, honest disclosure of AI assistance or affiliate relationships, accurate dates.
- Why: the page exists to help readers, not primarily to attract search traffic. Flag thin, duplicated, scaled, or keyword-stuffed pages.
- Stricter care for health, finance, legal, and safety topics.
- Report these as qualitative observations with examples. Do not output a numeric E-E-A-T score as if Google computes one.
