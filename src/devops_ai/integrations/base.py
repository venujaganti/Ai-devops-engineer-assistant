from dataclasses import asdict, dataclass, field


@dataclass
class IntegrationResult:
    tool: str
    operation: str
    success: bool
    summary: str
    output: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)