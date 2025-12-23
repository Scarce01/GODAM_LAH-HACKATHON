# communication/__init__.py
"""
OBSIDIAN Communication Module
Secure mTLS Communication Rail for Government Interactions

Components:
- communication_rail: Main mTLS implementation
- mtls_server: Server-side mutual TLS handler
- mtls_client: Client-side mutual TLS handler
- certificate_manager: PKI certificate validation
- session_key_rotation: Perfect Forward Secrecy

Author: OBSIDIAN Team
Version: 2.0 (Iron Vault - mTLS Only)
"""

__version__ = "2.0.0"
__author__ = "OBSIDIAN Team"

from .communication_rail import CommunicationRail
from .mtls_server import MTLSServer
from .mtls_client import MTLSClient
from .certificate_manager import CertificateManager
from .session_key_rotation import SessionKeyRotation

__all__ = [
    'CommunicationRail',
    'MTLSServer',
    'MTLSClient',
    'CertificateManager',
    'SessionKeyRotation'
]

# Communication configuration
COMMUNICATION_CONFIG = {
    "protocol": "mtls",
    "tls_version": "1.3",
    "cipher_suites": [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256"
    ],
    "require_client_cert": True,
    "verify_mode": "CERT_REQUIRED",
    "key_rotation_interval": 86400,  # 24 hours
    "session_timeout": 3600,  # 1 hour
    "max_connections": 100,
    "buffer_size": 8192
}

print(f"🔐 OBSIDIAN Communication Module v{__version__} loaded")
print(f"   Protocol: mTLS (Mutual TLS {COMMUNICATION_CONFIG['tls_version']})")
print(f"   Security: Perfect Forward Secrecy enabled")