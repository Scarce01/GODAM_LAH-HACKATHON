# webapp/__init__.py
"""
OBSIDIAN Web Application Module
User and Government portals for identity management

Components:
- user_portal: Citizen-facing web interface
- government_portal: Agency request submission
- admin_dashboard: System administration
- api_gateway: Unified API routing
- templates: HTML/CSS/JS templates

Author: OBSIDIAN Team
Version: 2.0 (Iron Vault - Enhanced Web Interface)
"""

__version__ = "2.0.0"
__author__ = "OBSIDIAN Team"

from .user_portal import UserPortalApp
from .government_portal import GovernmentPortalApp
from .admin_dashboard import AdminDashboardApp
from .api_gateway import APIGateway

__all__ = [
    'UserPortalApp',
    'GovernmentPortalApp',
    'AdminDashboardApp',
    'APIGateway'
]

# Web application configuration
WEBAPP_CONFIG = {
    "user_portal": {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": False,
        "ssl_enabled": True,
        "session_timeout": 1800  # 30 minutes
    },
    "government_portal": {
        "host": "0.0.0.0",
        "port": 8001,
        "debug": False,
        "ssl_enabled": True,
        "require_mtls": True,
        "session_timeout": 3600  # 1 hour
    },
    "admin_dashboard": {
        "host": "127.0.0.1",
        "port": 8002,
        "debug": False,
        "ssl_enabled": True,
        "require_2fa": True,
        "session_timeout": 900  # 15 minutes
    },
    "api_gateway": {
        "host": "0.0.0.0",
        "port": 8080,
        "rate_limit": "100/minute",
        "cors_enabled": False
    }
}

print(f"🌐 OBSIDIAN Web Application Module v{__version__} loaded")
print(f"   User Portal: Port {WEBAPP_CONFIG['user_portal']['port']}")
print(f"   Government Portal: Port {WEBAPP_CONFIG['government_portal']['port']}")
print(f"   Admin Dashboard: Port {WEBAPP_CONFIG['admin_dashboard']['port']}")