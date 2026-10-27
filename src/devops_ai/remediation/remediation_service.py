
import json

from src.devops_ai.ai.gemini_client import GeminiClient

from .patch_validator import validate_proposed_patch
from .prompts import build_remediation_prompt
from .schemas import RemediationReport, parse_remediation_response


class RemediationService:
    def __init__(self, gemini_client: GeminiClient) -> None:
        self.gemini_client = gemini_client

    def analyze(
        self,
        findings: list[dict],
        file_context: dict[str, str] | None = None,
    ) -> RemediationReport:
        if not findings:
            return RemediationReport(
                summary="No findings were supplied for analysis.",
                items=[],
                limitations=["No repository findings were analyzed."],
            )

        prompt = build_remediation_prompt(findings, file_context)

        # Reuse the existing Phase 3 public API.
        raw_response = self.gemini_client.generate_reply(
            message=prompt,
            history=[],
        )

        if not isinstance(raw_response, str):
            raise ValueError("Gemini returned an unexpected response type")

        if len(raw_response) > 30000:
            raise ValueError("Gemini response exceeded the allowed size")

        # Accept plain JSON only. Do not execute or interpret model-generated code.
        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise ValueError("Gemini did not return valid JSON") from exc

        report = parse_remediation_response(data)

        # Reject unsafe-looking paths in proposed patches before displaying them.
        for item in report.items:
            valid, reason = validate_proposed_patch(item.patch)
            if not valid:
                raise ValueError(
                    f"Patch rejected for {item.rule_id}: {reason}"
                )

        return report
