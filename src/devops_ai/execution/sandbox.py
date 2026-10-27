"""Sandbox policy definitions; this module does not execute commands."""
from dataclasses import dataclass

@dataclass(frozen=True)
class SandboxPolicy:
    network_access: bool = False
    writable_paths: tuple[str, ...] = ()
    timeout_seconds: int = 30
    def __post_init__(self):
        if not 1 <= self.timeout_seconds <= 300:
            raise ValueError("timeout_seconds must be between 1 and 300")
