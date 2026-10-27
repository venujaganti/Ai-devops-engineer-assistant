"""AWS CLI integration adapter."""
from src.devops_ai.integrations.cloud import CloudCLIIntegration

class AWSIntegration(CloudCLIIntegration):
    def check_cli(self):
        return super().check_cli("aws")
