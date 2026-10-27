#!/usr/bin/env python3
"""Normalize PagerDuty and Alertmanager payloads into a stable JSON shape."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _load_input() -> object:
    if len(sys.argv) > 1:
        return json.loads(Path(sys.argv[1]).read_text())
    return json.load(sys.stdin)


def _first_non_empty(*values: object) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _merge_dicts(*values: object) -> dict[str, object]:
    merged: dict[str, object] = {}
    for value in values:
        if isinstance(value, dict):
            merged.update(value)
    return merged


def _pick(mapping: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


_ALERT_MEMBER_FIELDS = (
    "title", "service", "environment", "severity", "alertname", "cluster",
    "namespace", "workload", "instance", "summary", "runbook_url", "dashboard_url",
)


def _string_fields(mapping: object) -> dict[str, object]:
    if not isinstance(mapping, dict):
        return {}
    return {key: value for key, value in mapping.items() if isinstance(key, str) and isinstance(value, str)}


def _normalize_alertmanager_member(alert: object, common_labels: dict[str, object],
                                   common_annotations: dict[str, object]) -> dict[str, object]:
    if not isinstance(alert, dict):
        alert = {}
    labels = {**common_labels, **_string_fields(alert.get("labels"))}
    annotations = {
        **common_annotations,
        **_string_fields(alert.get("annotations")),
    }
    summary = _pick(annotations, "summary", "description")
    alertname = _pick(labels, "alertname")
    return {
        "title": _first_non_empty(summary, alertname),
        "service": _pick(labels, "service", "app", "job"),
        "environment": _pick(labels, "environment", "env"),
        "severity": _pick(labels, "severity"),
        "alertname": alertname,
        "cluster": _pick(labels, "cluster"),
        "namespace": _pick(labels, "namespace", "kubernetes_namespace"),
        "workload": _pick(labels, "deployment", "statefulset", "daemonset", "job"),
        "instance": _pick(labels, "instance", "pod", "node"),
        "summary": summary,
        "runbook_url": _pick(annotations, "runbook_url"),
        "dashboard_url": _pick(annotations, "dashboard_url"),
        "labels": labels,
        "annotations": annotations,
    }


def _shared_values(members: list[dict[str, object]], key: str) -> dict[str, object]:
    if not members:
        return {}
    first = members[0].get(key)
    if not isinstance(first, dict):
        return {}
    return {
        name: value
        for name, value in first.items()
        if all(isinstance(member.get(key), dict) and member[key].get(name) == value
               for member in members[1:])
    }


def _normalize_alertmanager(payload: dict[str, object]) -> dict[str, object]:
    alerts = payload.get("alerts")
    alert_members = alerts if isinstance(alerts, list) else []
    common_labels = _string_fields(_merge_dicts(payload.get("groupLabels"), payload.get("commonLabels")))
    common_annotations = _string_fields(payload.get("commonAnnotations"))
    members = [
        _normalize_alertmanager_member(alert, common_labels, common_annotations)
        for alert in alert_members
    ]

    # Preserve the legacy top-level fields for single alerts. For groups, expose
    # a top-level field only when every member has the same value.
    if len(members) == 1:
        summary = members[0]
        labels = members[0]["labels"]
        annotations = members[0]["annotations"]
    else:
        labels = _shared_values(members, "labels")
        annotations = _shared_values(members, "annotations")
        summary = {}
        for field in _ALERT_MEMBER_FIELDS:
            values = [member.get(field, "") for member in members]
            summary[field] = values[0] if values and values[0] and all(value == values[0] for value in values) else ""

    return {
        "source": "alertmanager",
        **{field: summary.get(field, "") for field in _ALERT_MEMBER_FIELDS},
        "incident_url": _first_non_empty(
            payload.get("externalURL") if isinstance(payload.get("externalURL"), str) else "",
        ),
        "labels": labels,
        "annotations": annotations,
        "group_status": payload.get("status", ""),
        "receiver": payload.get("receiver", ""),
        "alert_count": len(alert_members),
        "alerts": members,
    }


def _normalize_pagerduty(payload: dict[str, object]) -> dict[str, object]:
    event = payload.get("event")
    if not isinstance(event, dict):
        event = payload

    custom_details = event.get("custom_details")
    if not isinstance(custom_details, dict):
        custom_details = {}

    labels = _merge_dicts(custom_details.get("labels"), custom_details)
    annotations = _merge_dicts(custom_details.get("annotations"))

    return {
        "source": "pagerduty",
        "title": _first_non_empty(
            event.get("title") if isinstance(event.get("title"), str) else "",
            payload.get("title") if isinstance(payload.get("title"), str) else "",
        ),
        "service": _first_non_empty(
            _pick(labels, "service", "app", "job"),
            payload.get("service", {}).get("summary", "") if isinstance(payload.get("service"), dict) else "",
        ),
        "environment": _pick(labels, "environment", "env"),
        "severity": _first_non_empty(
            payload.get("urgency") if isinstance(payload.get("urgency"), str) else "",
            _pick(labels, "severity"),
        ),
        "alertname": _pick(labels, "alertname"),
        "cluster": _pick(labels, "cluster"),
        "namespace": _pick(labels, "namespace"),
        "workload": _pick(labels, "deployment", "statefulset", "daemonset", "job"),
        "instance": _pick(labels, "instance", "pod", "node"),
        "summary": _first_non_empty(
            event.get("subtitle") if isinstance(event.get("subtitle"), str) else "",
            _pick(annotations, "summary", "description"),
        ),
        "runbook_url": _first_non_empty(
            _pick(annotations, "runbook_url"),
            _pick(labels, "runbook_url"),
        ),
        "dashboard_url": _first_non_empty(
            _pick(annotations, "dashboard_url"),
            _pick(labels, "dashboard_url"),
        ),
        "incident_url": _first_non_empty(
            payload.get("html_url") if isinstance(payload.get("html_url"), str) else "",
            event.get("html_url") if isinstance(event.get("html_url"), str) else "",
        ),
        "labels": labels,
        "annotations": annotations,
        "incident_number": payload.get("incident_number", ""),
    }


def normalize(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        return {
            "source": "unknown",
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
            "annotations": {},
        }

    if "alerts" in payload and isinstance(payload.get("alerts"), list):
        return _normalize_alertmanager(payload)

    if "event" in payload or "incident_number" in payload or "urgency" in payload:
        return _normalize_pagerduty(payload)

    labels = _merge_dicts(payload.get("labels"))
    annotations = _merge_dicts(payload.get("annotations"))

    return {
        "source": "unknown",
        "title": _first_non_empty(
            payload.get("title") if isinstance(payload.get("title"), str) else "",
            _pick(annotations, "summary", "description"),
        ),
        "service": _pick(labels, "service", "app", "job"),
        "environment": _pick(labels, "environment", "env"),
        "severity": _pick(labels, "severity"),
        "alertname": _pick(labels, "alertname"),
        "cluster": _pick(labels, "cluster"),
        "namespace": _pick(labels, "namespace"),
        "workload": _pick(labels, "deployment", "statefulset", "daemonset", "job"),
        "instance": _pick(labels, "instance", "pod", "node"),
        "summary": _pick(annotations, "summary", "description"),
        "runbook_url": _pick(annotations, "runbook_url"),
        "dashboard_url": _pick(annotations, "dashboard_url"),
        "incident_url": "",
        "labels": labels,
        "annotations": annotations,
    }


def main() -> int:
    payload = _load_input()
    print(json.dumps(normalize(payload), ensure_ascii=True, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
