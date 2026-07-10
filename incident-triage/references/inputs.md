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
