"""Secret-safe environment configuration validation."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any


_ENV_NAME_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{0,127}$")


@dataclass(frozen=True)
class EnvironmentFinding:
    """A safe-to-display environment validation finding."""

    code: str
    severity: str
    message: str
    variable: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EnvironmentValidator:
    """Validate environment-variable presence without exposing values."""

    def __init__(
        self,
        required_variables: tuple[str, ...] = (),
        optional_variables: tuple[str, ...] = (),
    ) -> None:
        self.required_variables = tuple(required_variables)
        self.optional_variables = tuple(optional_variables)

        all_names = self.required_variables + self.optional_variables
        invalid = [name for name in all_names if not self._valid_name(name)]
        if invalid:
            raise ValueError(
                "Invalid environment variable names: " + ", ".join(invalid)
            )

        if len(set(all_names)) != len(all_names):
            raise ValueError("Environment variable names must not be duplicated.")

    @staticmethod
    def _valid_name(name: str) -> bool:
        return bool(_ENV_NAME_PATTERN.fullmatch(name))

    def validate(
        self,
        environ: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        """Return presence status only. Never return environment values."""
        source = os.environ if environ is None else environ
        findings: list[EnvironmentFinding] = []

        for name in self.required_variables:
            if not source.get(name, "").strip():
                findings.append(
                    EnvironmentFinding(
                        code="ENV_REQUIRED_MISSING",
                        severity="high",
                        message=f"Required environment variable {name} is missing.",
                        variable=name,
                    )
                )

        for name in self.optional_variables:
            if not source.get(name, "").strip():
                findings.append(
                    EnvironmentFinding(
                        code="ENV_OPTIONAL_MISSING",
                        severity="info",
                        message=f"Optional environment variable {name} is not set.",
                        variable=name,
                    )
                )

        return {
            "status": (
                "blocked"
                if any(item.severity == "high" for item in findings)
                else "ready"
            ),
            "checked_required": len(self.required_variables),
            "checked_optional": len(self.optional_variables),
            "findings": [item.to_dict() for item in findings],
            "limitations": [
                "Checks variable presence only, not correctness or connectivity.",
                "Does not read .env files or print environment variable values.",
                "Does not verify whether credentials are valid or expired.",
            ],
        }