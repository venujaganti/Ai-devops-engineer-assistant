from devops_ai.workflows.devops_workflow import DevOpsWorkflow


class FakeAssistant:
    def answer(self, question):
        return {"answer": "Check your application logs and health endpoint."}


class FakeScanner:
    def scan(self):
        return {
            "status": "completed",
            "findings": [
                {
                    "rule_id": "CONTAINER_LATEST_TAG",
                    "severity": "medium",
                    "message": "A mutable image tag was detected.",
                }
            ],
        }


class FakeRemediation:
    def generate(self, findings):
        return {
            "items": [
                {
                    "title": "Pin the container base image",
                    "requires_manual_review": True,
                }
            ]
        }


class FakePreflight:
    def run(self, environ=None):
        return {
            "status": "review_required",
            "summary": {"total_findings": 1, "blocking_findings": 0},
            "findings": [],
        }


def test_end_to_end_diagnostic_workflow():
    workflow = DevOpsWorkflow(
        assistant=FakeAssistant(),
        repository_scanner=FakeScanner(),
        remediation=FakeRemediation(),
        deployment_preflight=FakePreflight(),
    )

    result = workflow.run(
        "repository_scan",
        question="How can I improve container security?",
        run_remediation=True,
        run_deployment_preflight=True,
        environ={},
    )

    data = result.to_dict()

    assert data["status"] == "warning"
    assert [step["name"] for step in data["steps"]] == [
        "repository_scan",
        "remediation",
        "deployment_preflight",
    ]
    assert "No shell commands" in data["limitations"][0]