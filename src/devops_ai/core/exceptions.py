class DevOpsAssistantError(Exception):
    """Base exception for the DevOps assistant."""


class ConfigurationError(DevOpsAssistantError):
    """Raised when application configuration is invalid."""


class IntegrationError(DevOpsAssistantError):
    """Raised when an external integration fails."""


class ExecutionDeniedError(DevOpsAssistantError):
    """Raised when a command is rejected by security policy."""


class GeminiConfigurationError(ConfigurationError):
    """Raised when Gemini credentials or settings are missing."""


class GeminiServiceError(IntegrationError):
    """Raised when Gemini cannot return a usable response."""