from devops_ai.workflows.devops_workflow import DevOpsWorkflow


class FakeAssistant:
    def answer(self, question):
        return {
            "answer": "Example response",
            "api_key": "do-not-disclose",
            "notes": "token=example-sensitive-value",
        }


class RecordingScanner:
    def __init__(self):
        self.called = False

    def scan(self):
        self.called = True
        return {"findings": []}


def test_secret_key_fields_are_redacted():
    workflow = DevOpsWorkflow(assistant=FakeAssistant())

    result = workflow.run("assistant", question="Test")

    serialized = str(result.to_dict())
    assert "do-not-disclose" not in serialized
    assert "example-sensitive-value" not in serialized
    assert "[REDACTED]" in serialized


def test_unknown_task_does_not_call_scanner():
    scanner = RecordingScanner()
    workflow = DevOpsWorkflow(repository_scanner=scanner)

    result = workflow.run("arbitrary_task")

    assert result.status == "blocked"
    assert scanner.called is False


def test_oversized_question_is_rejected():
    workflow = DevOpsWorkflow()

    result = workflow.run("assistant", question="x" * 10_001)

    assert result.status == "blocked"