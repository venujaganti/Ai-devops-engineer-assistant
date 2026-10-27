"""Google Cloud CLI integration adapter."""
from src.devops_ai.integrations.cloud import CloudCLIIntegration

class GCPIntegration(CloudCLIIntegration):
    def check_cli(self):
        return super().check_cli("gcp")
