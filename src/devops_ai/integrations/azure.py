"""Azure CLI integration adapter."""
from src.devops_ai.integrations.cloud import CloudCLIIntegration

class AzureIntegration(CloudCLIIntegration):
    def check_cli(self):
        return super().check_cli("azure")
