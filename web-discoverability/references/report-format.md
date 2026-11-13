# Report format

Keep reports scannable and evidence-based. Replace sections that do not apply with a one-line "not checked" note.

```
# Discoverability review: <site or repo>
Date: <YYYY-MM-DD>   Scope: <URLs/templates/routes sampled>   Mode: <live read-only | codebase | both>
Tools used: <curl, browser, Lighthouse, CrUX...>   Not available: <what and why>

## Summary
<3 to 5 lines: overall state, top risks, what to fix first. No outcome promises.>

## Findings
### Critical
1. <Title> [observed|inferred]
   - Where: <URL/template/file:line>
   - Evidence: <header, HTML snippet, command output, measurement with source: field|lab>
   - Impact: <what crawlers/users cannot do>
   - Fix: <specific change; owner action if it needs live-site access>
### High / Medium / Low
...

## Passed checks
<short list of verified-good items>

## Not checked / limitations
<no Search Console, no field data, JS rendering unverified, sample size, auth-gated pages>

## Dated facts used
<each time-sensitive claim with "reviewed YYYY-MM-DD" and its official source URL>

## Suggested next steps
<ordered; flag any step needing explicit authorization: robots.txt change, Indexing API, IndexNow, paid tools>
```

## Rules

- One finding per root cause; list affected URL count and 2 to 3 examples.
- Every finding has evidence and a concrete fix. Mark observed or inferred.
- Give CWV numbers with data type (field or lab), device, percentile, and date.
- Severity per the table in [../SKILL.md](../SKILL.md). Retired-schema cleanup and llms.txt are low.
- Do not add a numeric overall score unless the user asks, and then label it a local heuristic with its rubric.
- Do not state expected ranking, traffic, or citation gains. Use "should remove the indexing blocker" style language instead.
- Keep secrets, tokens, and private URLs out of the report.
