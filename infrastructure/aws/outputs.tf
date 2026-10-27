output "instance_id" {
  description = "EC2 instance ID."
  value       = aws_instance.app.id
}

output "application_url" {
  description = "Streamlit application URL."
  value       = "http://${aws_instance.app.public_dns}:8501"
}

output "grafana_url" {
  description = "Grafana URL; reachable only if grafana_allowed_cidr is configured."
  value       = "http://${aws_instance.app.public_dns}:3000"
}

output "prometheus_access_note" {
  description = "Prometheus binds to EC2 loopback and is not exposed publicly. Use SSM port forwarding if required."
  value       = "Use AWS Systems Manager port forwarding to localhost:9090 for private Prometheus access."
}
