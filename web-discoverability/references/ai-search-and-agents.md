# AI search (GEO) and agent readiness

Reviewed 2026-11-13; re-verify crawler tokens and vendor behavior against each vendor's official documentation before acting. Google's position (Search Central, AI features guidance https://developers.google.com/search/docs/appearance/ai-features): optimizing for AI features in Search is largely the same as sound SEO. Treat "GEO" as SEO fundamentals plus crawler access plus content that is easy to cite, not a separate guaranteed tactic.

## What to check

1. **Fetchable and indexable.** Everything in [technical-checklist.md](technical-checklist.md). Content that is not indexable in Google Search is not eligible for its AI features.
2. **Content in server HTML.** Many non-Google AI fetchers do not execute JavaScript; confirm main content appears in `curl` output.
3. **Crawler policy per purpose** (below). Decide deliberately which purposes to allow.
4. **Citability** (reviewer heuristic, not a ranking factor): a direct answer near the top of a section, self-contained passages that make sense when quoted, specific facts with sources and dates, named authors and organization, consistent entity names, clear headings, real tables and lists where the content is tabular or sequential. Do not chunk or rewrite pages into artificial snippets for AI; Google has said that is unnecessary.
5. **Entity clarity.** Consistent brand and author names, an About page, `Organization` and `Person` markup with `sameAs` to real profiles. Report brand-mention research as correlational.

## AI crawler tokens by purpose

Reviewed 2026-11-13; vendors add and rename tokens, so re-verify.

| Token | Operator | Purpose | Notes |
|---|---|---|---|
| Googlebot | Google | Search crawling and indexing | Blocking it removes the site from Search |
| Google-Extended | Google | Control token for Gemini and Vertex AI training and grounding | Not a crawler; does not affect Google Search inclusion or ranking |
| GPTBot | OpenAI | Model training | Blocking does not remove ChatGPT search citations |
| OAI-SearchBot | OpenAI | ChatGPT search index | Needed for appearing in ChatGPT search results |
| ChatGPT-User | OpenAI | User-initiated fetches | Vendor says robots rules may not apply |
| ClaudeBot | Anthropic | Model training | |
| Claude-SearchBot | Anthropic | Search result quality | |
| Claude-User | Anthropic | User-initiated fetches | |
| PerplexityBot | Perplexity | Search index | |
| Perplexity-User | Perplexity | User-initiated fetches | Generally not governed by robots.txt |
| CCBot | Common Crawl | Open web corpus (often reused for training) | |
| Applebot-Extended | Apple | Opt-out of Apple generative training use | Does not itself crawl |

Rules:
- Training and search are different decisions. Blocking a training token is not the same as hiding from AI search, and the reverse. Ask the owner which they want; do not choose for them.
- robots.txt is a preference signal. Well-behaved crawlers honor it; user-initiated agents may not. Use authentication or a WAF for real access control.
- Do not IP-block crawlers you want to allow; a blocked crawler cannot read robots.txt.
- Every change to robots.txt on a live host is the owner's action. Draft the diff; do not apply it without authorization.
- Sample group (adapt, do not paste blindly):

```
User-agent: OAI-SearchBot
Allow: /

User-agent: GPTBot
Disallow: /

User-agent: *
Allow: /
Sitemap: https://example.com/sitemap.xml
```

## llms.txt

`/llms.txt` is a community proposal (https://llmstxt.org) for a Markdown index of a site for LLMs. Google has not adopted it and it is not a Google Search signal; no major vendor has committed to using it as a ranking or citation factor. It is cheap, low-risk, and optional. If asked for one: draft it, keep it accurate and short (title, summary, curated links with one-line descriptions), say plainly that benefits are unproven, and rank it low priority. Never describe it as affecting Google Search, AI Overviews, or rankings.

## Agent readiness

Browsing agents (user-driven assistants that read and act on pages) benefit from the same things as accessibility, performance, and a clear access policy:

- **Accessibility tree**: semantic HTML, accessible names for links, buttons, and inputs, labels tied to fields, valid ARIA only where needed, nothing interactive hidden from the tree. Check with the browser's accessibility snapshot or Lighthouse accessibility.
- **Performance and stability**: low layout shift, content present without long script waits, stable selectors, no blocking interstitials.
- **Access policy**: deliberate robots.txt groups per purpose, a sane WAF/bot-management stance (does not blanket-block legitimate user agents), clear terms, authentication for private actions. Do not test a WAF with spoofed agent user-agents unless the owner authorizes it.
- **Optional layers**: Markdown versions of pages, `/.well-known` discovery files, and WebMCP (a browser-side proposal for exposing site tools to agents). WebMCP is optional and experimental; consider it only for sites with forms or transactions, and verify current browser support first. None of these is a foundation or a ranking factor.
- Report Lighthouse or third-party "agent readiness" scores as that tool's heuristic, exactly as reported, with date and version.

## Do not claim

- That llms.txt, FAQ markup, or schema increases AI citations without a primary source.
- That blocking Google-Extended affects Google Search (it does not) or that allowing it improves it.
- Specific AI-referral or citation-lift percentages from third-party blogs.
- That a site "is cited" or "is not cited" by an AI product unless you observed it, naming the product, query, date, and that results vary by run.
