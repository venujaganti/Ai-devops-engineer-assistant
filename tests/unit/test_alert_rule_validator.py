from devops_ai.monitoring.alert_rule_validator import AlertRuleValidator


def test_valid_alert_rule():
    content = """
groups:
  - name: application
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status="500"}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: Application error rate is elevated
"""

    result = AlertRuleValidator().validate_text(content)

    assert result["status"] == "ready"
    assert result["findings"] == []


def test_missing_alert_groups_are_blocked():
    result = AlertRuleValidator().validate_text("groups: []")

    assert result["status"] == "blocked"
    assert result["findings"][0]["code"] == "ALERT_GROUPS_MISSING"


def test_alert_without_expression_is_blocked():
    content = """
groups:
  - name: application
    rules:
      - alert: MissingExpression
"""

    result = AlertRuleValidator().validate_text(content)

    assert any(
        item["code"] == "ALERT_EXPRESSION_MISSING"
        for item in result["findings"]
    )
    assert result["status"] == "blocked"


def test_duplicate_alert_names_are_flagged():
    content = """
groups:
  - name: application
    rules:
      - alert: HighErrorRate
        expr: up == 0
      - alert: HighErrorRate
        expr: up == 0
"""

    result = AlertRuleValidator().validate_text(content)

    assert any(
        item["code"] == "ALERT_RULE_DUPLICATE"
        for item in result["findings"]
    )