"""Explicit approval gate for potentially impactful actions."""
def require_approval(approved: bool, action: str = "operation") -> None:
    if not approved:
        raise PermissionError(f"Human approval is required before {action}.")
