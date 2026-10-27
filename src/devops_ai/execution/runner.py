"""Execution façade deliberately disabled by default."""
from src.devops_ai.execution.approvals import require_approval

class SafeRunner:
    def __init__(self, enabled: bool = False): self.enabled = enabled
    def run(self, command, *, approved: bool = False):
        if not self.enabled:
            raise PermissionError("Command execution is disabled by policy.")
        require_approval(approved, "command execution")
        raise NotImplementedError("Execution backends must be explicitly configured and sandboxed.")
