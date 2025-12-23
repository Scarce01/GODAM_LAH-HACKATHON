# api/__init__.py
"""
OBSIDIAN API Module
Three-tier API architecture for Users, Government, and Admin

Components:
- user_api: Citizen-facing API (port 5001)
- government_api: Government agency API (port 5002)
- admin_api: System administration API (port 5003)
- middleware: Authentication, logging, rate limiting
- request_validator: Request validation and sanitization

Author: OBSIDIAN Team
Version: 2.0 (Iron Vault - Three APIs)
"""

__version__ = "2.0.0"
__author__ = "OBSIDIAN Team"

from .user_api import UserAPI
from .government_api import GovernmentAPI
from .admin_api import AdminAPI
from .middleware import AuthMiddleware, LoggingMiddleware, RateLimitMiddleware
from .request_validator import RequestValidator

__all__ = [
    'UserAPI',
    'GovernmentAPI',
    'AdminAPI',
    'AuthMiddleware',
    'LoggingMiddleware',
    'RateLimitMiddleware',
    'RequestValidator'
]

# API configuration
API_CONFIG = {
    "user_api": {
        "host": "0.0.0.0",
        "port": 5001,
        "max_requests_per_minute": 60,
        "require_hardware_auth": True
    },
    "government_api": {
        "host": "0.0.0.0",
        "port": 5002,
        "max_requests_per_minute": 30,
        "require_mtls": True,
        "require_digital_signature": True
    },
    "admin_api": {
        "host": "127.0.0.1",  # Localhost only
        "port": 5003,
        "max_requests_per_minute": 10,
        "require_2fa": True
    },
    "cors_enabled": False,  # No CORS - internal network only
    "request_timeout": 30,
    "max_payload_size": 10485760  # 10 MB
}

print(f"🌐 OBSIDIAN API Module v{__version__} loaded")
print(f"   User API:       Port {API_CONFIG['user_api']['port']}")
print(f"   Government API: Port {API_CONFIG['government_api']['port']}")
print(f"   Admin API:      Port {API_CONFIG['admin_api']['port']}")