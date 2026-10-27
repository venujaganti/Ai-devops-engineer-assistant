import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandAssessment:
    command: str
    risk_level: str
    reasons: tuple[str, ...]
    requires_human_review: bool = True


HIGH_RISK_PATTERNS = (
    (r"\brm\s+-rf\b", "Recursive forced deletion"),
    (r"\bterraform\s+destroy\b", "Infrastructure destruction"),
    (r"\bkubectl\s+delete\b", "Kubernetes resource deletion"),
    (r"\bhelm\s+uninstall\b", "Helm release removal"),
    (r"\bdocker\s+system\s+prune\b", "Container cleanup"),
    (r"\bpodman\s+system\s+prune\b", "Container cleanup"),
    (r"\bdrop\s+database\b", "Database destruction"),
    (r"\bDELETE\s+FROM\b", "Database row deletion"),
    (r"\baws\s+.*\b(delete|terminate|detach)\b", "Cloud resource mutation"),
    (r"\baz\s+.*\b(delete|remove)\b", "Azure resource mutation"),
    (r"\bgcloud\s+.*\b(delete|remove)\b", "Google Cloud resource mutation"),
)

MEDIUM_RISK_PATTERNS = (
    (r"\bterraform\s+apply\b", "Infrastructure changes"),
    (r"\bkubectl\s+apply\b", "Kubernetes resource changes"),
    (r"\bhelm\s+upgrade\b", "Kubernetes release changes"),
    (r"\bpodman\s+run\b", "Container execution"),
    (r"\bdocker\s+run\b", "Container execution"),
    (r"\bkubectl\s+exec\b", "Command inside a running container"),
    (r"\bsystemctl\s+(restart|stop)\b", "Service interruption"),
    (r"\bchmod\b", "Filesystem permission changes"),
    (r"\bchown\b", "Filesystem ownership changes"),
)


def assess_command(command: str) -> CommandAssessment:
    if not isinstance(command, str) or not command.strip():
        raise ValueError("Command must not be empty")

    if len(command) > 4000:
        raise ValueError("Command exceeds the allowed length")

    reasons = []

    for pattern, reason in HIGH_RISK_PATTERNS:
        if re.search(pattern, command, flags=re.IGNORECASE):
            reasons.append(reason)

    if reasons:
        return CommandAssessment(
            command=command,
            risk_level="high",
            reasons=tuple(dict.fromkeys(reasons)),
        )

    for pattern, reason in MEDIUM_RISK_PATTERNS:
        if re.search(pattern, command, flags=re.IGNORECASE):
            reasons.append(reason)

    if reasons:
        return CommandAssessment(
            command=command,
            risk_level="medium",
            reasons=tuple(dict.fromkeys(reasons)),
        )

    return CommandAssessment(
        command=command,
        risk_level="low",
        reasons=("No known high-risk pattern detected; manual review is still required",),
    )