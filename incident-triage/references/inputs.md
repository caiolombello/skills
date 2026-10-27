# Alert Inputs

Use this file only when the payload shape is unclear.

## PagerDuty

Common useful fields:

- `event.title`
- `event.subtitle`
- `event.custom_details`
- `service.summary`
- `urgency`
- `incident_number`
- `html_url`
- `assignments`

Look inside `custom_details` for:

- labels
- annotations
- cluster
- namespace
- pod
- workload
- dashboard or runbook URLs

## Alertmanager

Common useful fields:

- `status`
- `receiver`
- `groupLabels`
- `commonLabels`
- `commonAnnotations`
- `externalURL`
- `alerts[]`

Important keys often found in labels or annotations:

- `alertname`
- `severity`
- `service`
- `job`
- `cluster`
- `namespace`
- `pod`
- `container`
- `instance`
- `summary`
- `description`
- `runbook_url`
- `dashboard_url`

## Normalized Target Shape

For Alertmanager, the helper also returns `alert_count` and an `alerts` array
containing every normalized member. A single member retains the legacy top-level
target fields. For groups, a top-level field is populated only when every member
shares it; use the member list for differing targets, symptoms and severities.
String labels/annotations, including custom routing metadata, are preserved.
Normalization is not secret redaction: follow source access/privacy rules and
do not label the resulting JSON a sanitized report merely because it normalized.

Try to end up with:

```json
{
  "source": "pagerduty|alertmanager|unknown",
  "title": "",
  "service": "",
  "environment": "",
  "severity": "",
  "alertname": "",
  "cluster": "",
  "namespace": "",
  "workload": "",
  "instance": "",
  "summary": "",
  "runbook_url": "",
  "dashboard_url": "",
  "incident_url": "",
  "labels": {},
  "annotations": {}
}
```
