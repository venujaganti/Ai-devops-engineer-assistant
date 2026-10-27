from devops_ai.workflows.devops_workflow import DevOpsWorkflow


class FakeAssistant:
    def answer(self, question):
        return {"answer": f"Guidance for: {question}"}


class FakeScanner:
    def scan(self):
        return {
            "status": "completed",
            "findings": [
                {
                    "rule_id": "TEST001",
                    "severity": "medium",
                    "message": "Example finding",
                }
            ],
        }


class FakeRemediation:
    def generate(self, findings):
        return {"suggestions": len(findings)}


class FakePreflight:
    def run(self, environ=None):
        return {
            "status": "review_required",
            "summary": {"total_findings": 1},
            "findings": [],
        }


class FakeMonitoring:
    def inspect_config(self, path):
        return {"status": "ready", "findings": []}


def test_assistant_workflow():
    workflow = DevOpsWorkflow(assistant=FakeAssistant())

    result = workflow.run(
        "assistant",
        question="How do I check Kubernetes pods?",
    )

    assert result.status == "success"
    assert result.steps[0].name == "assistant"


def test_repository_scan_and_remediation():
    workflow = DevOpsWorkflow(
        repository_scanner=FakeScanner(),
        remediation=FakeRemediation(),
    )

    result = workflow.run(
        "repository_scan",
        run_remediation=True,
    )

    assert result.status == "success"
    assert [step.name for step in result.steps] == [
        "repository_scan",
        "remediation",
    ]


def test_preflight_never_claims_deployment_occurred():
    workflow = DevOpsWorkflow(deployment_preflight=FakePreflight())

    result = workflow.run("deployment_preflight")

    assert result.status == "warning"
    assert "no deployment was performed" in result.steps[0].summary


def test_monitoring_validation():
    workflow = DevOpsWorkflow(monitoring_diagnostics=FakeMonitoring())

    result = workflow.run(
        "monitoring_validation",
        monitoring_config_path="monitoring/prometheus.yml",
    )

    assert result.status == "success"


def test_unknown_task_is_blocked():
    workflow = DevOpsWorkflow()

    result = workflow.run("run_shell_command")

    assert result.status == "blocked"


def test_missing_assistant_is_reported():
    workflow = DevOpsWorkflow()

    result = workflow.run("assistant", question="Explain Terraform.")

    assert result.status == "warning"
    assert result.steps[0].status == "skipped"