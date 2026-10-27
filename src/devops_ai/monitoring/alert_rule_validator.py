"""Static Prometheus alert-rule validation."""

from __future__ import annotations

from typing import Any


class AlertRuleValidator:
    """Validate common Prometheus alert rule structure."""

    def validate_text(
        self,
        content: str,
        filename: str = "alert-rules.yml",
    ) -> dict[str, Any]:
        try:
            import yaml
        except ImportError:
            return self._result(
                "review_required",
                [{
                    "code": "ALERT_YAML_DEPENDENCY_MISSING",
                    "severity": "medium",
                    "message": "PyYAML is required for alert-rule validation.",
                    "file": filename,
                }],
            )

        try:
            document = yaml.safe_load(content)
        except yaml.YAMLError:
            return self._result(
                "blocked",
                [{
                    "code": "ALERT_INVALID_YAML",
                    "severity": "high",
                    "message": "Alert rules contain invalid YAML.",
                    "file": filename,
                }],
            )

        findings: list[dict[str, str]] = []

        if not isinstance(document, dict):
            return self._result(
                "blocked",
                [{
                    "code": "ALERT_ROOT_INVALID",
                    "severity": "high",
                    "message": "Alert rule document must be a mapping.",
                    "file": filename,
                }],
            )

        groups = document.get("groups")
        if not isinstance(groups, list) or not groups:
            return self._result(
                "blocked",
                [{
                    "code": "ALERT_GROUPS_MISSING",
                    "severity": "high",
                    "message": "No alert rule groups were defined.",
                    "file": filename,
                }],
            )

        group_names: set[str] = set()
        alert_names: set[str] = set()

        for group_index, group in enumerate(groups):
            location = f"groups[{group_index}]"

            if not isinstance(group, dict):
                findings.append({
                    "code": "ALERT_GROUP_INVALID",
                    "severity": "high",
                    "message": f"{location} must be a mapping.",
                    "file": filename,
                })
                continue

            group_name = group.get("name")
            if not isinstance(group_name, str) or not group_name.strip():
                findings.append({
                    "code": "ALERT_GROUP_NAME_MISSING",
                    "severity": "high",
                    "message": f"{location} has no valid name.",
                    "file": filename,
                })
            elif group_name in group_names:
                findings.append({
                    "code": "ALERT_GROUP_DUPLICATE",
                    "severity": "high",
                    "message": f"Duplicate alert group name: {group_name}.",
                    "file": filename,
                })
            else:
                group_names.add(group_name)

            rules = group.get("rules")
            if not isinstance(rules, list) or not rules:
                findings.append({
                    "code": "ALERT_RULES_MISSING",
                    "severity": "high",
                    "message": f"{location} contains no rules.",
                    "file": filename,
                })
                continue

            for rule_index, rule in enumerate(rules):
                rule_location = f"{location}.rules[{rule_index}]"

                if not isinstance(rule, dict):
                    findings.append({
                        "code": "ALERT_RULE_INVALID",
                        "severity": "high",
                        "message": f"{rule_location} must be a mapping.",
                        "file": filename,
                    })
                    continue

                is_alert = "alert" in rule
                is_record = "record" in rule

                if is_alert == is_record:
                    findings.append({
                        "code": "ALERT_RULE_TYPE_INVALID",
                        "severity": "high",
                        "message": (
                            f"{rule_location} must define exactly one of "
                            "'alert' or 'record'."
                        ),
                        "file": filename,
                    })

                name = rule.get("alert") if is_alert else rule.get("record")
                if not isinstance(name, str) or not name.strip():
                    findings.append({
                        "code": "ALERT_RULE_NAME_MISSING",
                        "severity": "high",
                        "message": f"{rule_location} has no valid rule name.",
                        "file": filename,
                    })
                elif is_alert and name in alert_names:
                    findings.append({
                        "code": "ALERT_RULE_DUPLICATE",
                        "severity": "medium",
                        "message": f"Duplicate alert name detected: {name}.",
                        "file": filename,
                    })
                elif is_alert:
                    alert_names.add(name)

                expression = rule.get("expr")
                if not isinstance(expression, str) or not expression.strip():
                    findings.append({
                        "code": "ALERT_EXPRESSION_MISSING",
                        "severity": "high",
                        "message": f"{rule_location} has no expression.",
                        "file": filename,
                    })

                if is_alert and not isinstance(rule.get("labels", {}), dict):
                    findings.append({
                        "code": "ALERT_LABELS_INVALID",
                        "severity": "high",
                        "message": f"{rule_location}.labels must be a mapping.",
                        "file": filename,
                    })

                if is_alert and not isinstance(rule.get("annotations", {}), dict):
                    findings.append({
                        "code": "ALERT_ANNOTATIONS_INVALID",
                        "severity": "high",
                        "message": f"{rule_location}.annotations must be a mapping.",
                        "file": filename,
                    })

                if is_alert and not rule.get("for"):
                    findings.append({
                        "code": "ALERT_DURATION_MISSING",
                        "severity": "info",
                        "message": (
                            f"{rule_location} has no 'for' duration. "
                            "Confirm whether immediate firing is intended."
                        ),
                        "file": filename,
                    })

        blocking = any(
            item["severity"] == "high" for item in findings
        )
        review = any(
            item["severity"] in {"medium", "low"} for item in findings
        )

        return self._result(
            "blocked" if blocking else "review_required" if review else "ready",
            findings,
        )

    @staticmethod
    def _result(
        status: str,
        findings: list[dict[str, str]],
    ) -> dict[str, Any]:
        return {
            "status": status,
            "findings": findings,
            "limitations": [
                "PromQL expressions are not parsed or executed.",
                "Metric existence and alert thresholds are not verified.",
                "Use promtool check rules for authoritative Prometheus rule validation.",
            ],
        }