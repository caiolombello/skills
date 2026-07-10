# Response Template

Use this when the user wants a message ready to paste into Slack, PagerDuty, or an incident room.

```text
Summary:
<one short paragraph describing what is firing and the likely scope>

Impact:
<customer-facing, internal-only, unknown, or no confirmed impact yet>

Evidence:
- <metric/log/state observation>
- <metric/log/state observation>
- <metric/log/state observation>

Hypothesis:
<most likely cause> (confidence: low|medium|high)

Next steps:
1. <lowest-risk next action>
2. <next validation or mitigation>
3. <escalation or owner action if needed>

Escalation:
<who should be involved, or "not needed yet">
```

## Tone

- Be concrete
- Avoid drama
- Separate evidence from inference
- Do not claim a root cause unless proved
