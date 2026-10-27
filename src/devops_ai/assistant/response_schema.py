from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class CommandRecommendation:
    command: str
    purpose: str
    risk_level: str
    requires_approval: bool = True


@dataclass
class AssistantResponse:
    category: str
    summary: str
    diagnosis: list[str] = field(default_factory=list)
    recommended_steps: list[str] = field(default_factory=list)
    commands: list[CommandRecommendation] = field(default_factory=list)
    validation_steps: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)