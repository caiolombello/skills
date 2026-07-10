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


def _normalize_alertmanager(payload: dict[str, object]) -> dict[str, object]:
    alerts = payload.get("alerts")
    first_alert = alerts[0] if isinstance(alerts, list) and alerts else {}
    if not isinstance(first_alert, dict):
        first_alert = {}

    labels = _merge_dicts(
        payload.get("groupLabels"),
        payload.get("commonLabels"),
        first_alert.get("labels"),
    )
    annotations = _merge_dicts(
        payload.get("commonAnnotations"),
        first_alert.get("annotations"),
    )

    return {
        "source": "alertmanager",
        "title": _first_non_empty(
            _pick(annotations, "summary", "description"),
            _pick(labels, "alertname"),
        ),
        "service": _pick(labels, "service", "app", "job"),
        "environment": _pick(labels, "environment", "env"),
        "severity": _pick(labels, "severity"),
        "alertname": _pick(labels, "alertname"),
        "cluster": _pick(labels, "cluster"),
        "namespace": _pick(labels, "namespace", "kubernetes_namespace"),
        "workload": _pick(labels, "deployment", "statefulset", "daemonset", "job"),
        "instance": _pick(labels, "instance", "pod", "node"),
        "summary": _pick(annotations, "summary", "description"),
        "runbook_url": _pick(annotations, "runbook_url"),
        "dashboard_url": _pick(annotations, "dashboard_url"),
        "incident_url": _first_non_empty(
            payload.get("externalURL") if isinstance(payload.get("externalURL"), str) else "",
        ),
        "labels": labels,
        "annotations": annotations,
        "group_status": payload.get("status", ""),
        "receiver": payload.get("receiver", ""),
        "alert_count": len(alerts) if isinstance(alerts, list) else 0,
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
