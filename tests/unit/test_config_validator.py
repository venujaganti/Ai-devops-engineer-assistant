
from src.devops_ai.integrations.config_validator import (
    validate_json,
    validate_terraform,
)


def test_invalid_json_is_reported():
    findings = validate_json('{"broken": }', "settings.json")

    assert findings
    assert findings[0].rule_id == "CFG-JSON-001"


def test_valid_json_has_no_findings():
    assert validate_json('{"enabled": true}', "settings.json") == []


def test_terraform_unbalanced_braces_are_reported():
    findings = validate_terraform(
        'resource "example" "demo" {\n name = "demo"\n',
        "main.tf",
    )

    assert any(item.rule_id == "CFG-TF-001" for item in findings)


def test_possible_public_cidr_is_flagged():
    findings = validate_terraform(
        'resource "example" "demo" {\n cidr_blocks = ["0.0.0.0/0"]\n}',
        "network.tf",
    )

    assert any(item.rule_id == "SEC-TF-002" for item in findings)
