# Structured data (JSON-LD)

Reviewed 2026-11-13. Google's supported-feature list changes often; re-verify every type against https://developers.google.com/search/docs/appearance/structured-data/search-gallery before recommending or removing it. schema.org vocabulary: https://schema.org. Validators: Rich Results Test https://search.google.com/test/rich-results and https://validator.schema.org.

## Principles

- Use JSON-LD in a `<script type="application/ld+json">` (Google's recommended format). Prefer it in the server-rendered HTML.
- Markup must describe content visible on the page. Do not mark up hidden, misleading, or fabricated content (fake reviews, ratings with no source). That risks a manual action.
- Valid markup makes a page eligible for a rich result; it never guarantees one and is not a ranking boost. Do not claim structured data increases AI citations unless a primary source says so.
- Match required and recommended properties from Google's feature doc, not only the schema.org type definition.

## Review checklist

1. `@context` is `https://schema.org`; `@type` is valid and appropriate.
2. Required properties present; values typed correctly (numbers, ISO 8601 dates, absolute URLs).
3. No placeholders, no empty strings, no lorem text.
4. Data agrees with the visible page (price, availability, author, dates).
5. Use `@id` and `sameAs` to connect entities (Organization, WebSite, Person) consistently across pages.
6. JSON parses (run it through a JSON parser) and survives templating (escaping quotes, no trailing commas).
7. Nesting is sensible: Article with author Person and publisher Organization; Product with Offer.

## Commonly useful types (generally supported; verify)

Organization, WebSite, BreadcrumbList, Article/BlogPosting/NewsArticle, Product with Offer and review/aggregate rating (genuine, first-party-visible reviews only), ProfilePage, Person, VideoObject, Event (public, physical), JobPosting, Course, DiscussionForumPosting, QAPage (genuine user Q&A pages), ProductGroup for variants, merchant return and shipping policy. LocalBusiness exists but local SEO is out of scope here.

## Deprecated or reduced (as of review date; re-verify)

| Type | Status noted at review |
|---|---|
| HowTo | Rich results removed (2023) |
| FAQPage | Restricted to authoritative government and health sites in 2023; the upstream snapshot reports full retirement of the rich result in 2026. Verify; do not recommend adding it for Google rich results, and do not flag existing markup above informational |
| SpecialAnnouncement, CourseInfo, EstimatedSalary, LearningVideo, VehicleListing, Practice Problem | Reported retired from Search rich results during 2025 to early 2026 |
| ClaimReview | Reported no longer a Search rich result; markup may still serve other consumers |
| Dataset | Not a Search rich result but used by Dataset Search; do not say it was discontinued |
| Sitelinks search box (WebSite SearchAction) | No longer displayed; markup is harmless |

Note on retired types: removing working markup is optional cleanup, not a fix. Do not escalate it above low severity. These entries come from a third-party snapshot, so confirm against Google's documentation and change log before telling a user to change anything.

## Report items

- Parse errors or invalid JSON: medium to high depending on template reach.
- Markup contradicting visible content, or fabricated ratings: high (policy risk).
- Missing Organization/WebSite/BreadcrumbList or Article basics: low to medium.
- Deprecated type present: low, informational.
