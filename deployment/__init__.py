# deployment/__init__.py
"""
OBSIDIAN Deployment Module
Docker, Kubernetes, and infrastructure automation

Components:
- docker_builder: Docker image builder
- kubernetes_deployer: K8s deployment manager
- ansible_playbook: Automated provisioning
- monitoring_setup: Prometheus + Grafana
- backup_manager: Automated backups
- security_hardening: Security configuration
- load_balancer: HAProxy/Nginx setup
- database_migration: Schema migrations

Author: OBSIDIAN Team
Version: 2.0 (Iron Vault - Production Deployment)
"""

__version__ = "2.0.0"
__author__ = "OBSIDIAN Team"

from .docker_builder import DockerBuilder
from .kubernetes_deployer import KubernetesDeployer
from .ansible_playbook import AnsiblePlaybook
from .monitoring_setup import MonitoringSetup
from .backup_manager import BackupManager
from .security_hardening import SecurityHardening
from .load_balancer import LoadBalancer
from .database_migration import DatabaseMigration

__all__ = [
    'DockerBuilder',
    'KubernetesDeployer',
    'AnsiblePlaybook',
    'MonitoringSetup',
    'BackupManager',
    'SecurityHardening',
    'LoadBalancer',
    'DatabaseMigration'
]

# Deployment configuration
DEPLOYMENT_CONFIG = {
    "environment": "production",
    "region": "ap-southeast-1",  # Singapore (closest to Malaysia)
    "high_availability": True,
    "replicas": {
        "api": 3,
        "webapp": 2,
        "blockchain": 5,  # Minimum for consensus
        "storage": 3  # RAID configuration
    },
    "backup": {
        "enabled": True,
        "frequency": "daily",
        "retention_days": 90
    },
    "monitoring": {
        "enabled": True,
        "alerting": True,
        "log_retention_days": 30
    }
}

print(f"🚀 OBSIDIAN Deployment Module v{__version__} loaded")
print(f"   Environment: {DEPLOYMENT_CONFIG['environment']}")
print(f"   Region: {DEPLOYMENT_CONFIG['region']}")
print(f"   High Availability: {DEPLOYMENT_CONFIG['high_availability']}")