import pytest

from devops_ai.workflows.workflow_result import WorkflowResult, WorkflowStep


def test_workflow_step_serializes():
    step = WorkflowStep(
        name="repository_scan",
        status="success",
        summary="Scan completed.",
        details={"files_scanned": 12},
    )

    assert step.to_dict()["details"]["files_scanned"] == 12


def test_invalid_step_status_is_rejected():
    with pytest.raises(ValueError):
        WorkflowStep(
            name="scan",
            status="unknown",
            summary="Invalid status.",
        )


def test_workflow_result_serializes_steps():
    result = WorkflowResult(
        workflow_id="test-workflow",
        status="success",
        summary="Workflow completed.",
        steps=[
            WorkflowStep(
                name="assistant",
                status="success",
                summary="Answer generated.",
            )
        ],
    )

    data = result.to_dict()

    assert data["workflow_id"] == "test-workflow"
    assert len(data["steps"]) == 1
    assert data["steps"][0]["name"] == "assistant"


def test_empty_workflow_id_is_rejected():
    with pytest.raises(ValueError):
        WorkflowResult(
            workflow_id="",
            status="success",
            summary="Invalid result.",
        )