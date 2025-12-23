# core/__init__.py
"""
OBSIDIAN Core Security Module
Nine-layer military-grade security system (Aegis-9)

Components:
- security_core: Main encryption/decryption interface
- key_derivation: PBKDF2 + HKDF key management
- encryption_engine: AES-256-CTR implementation
- canary_tokens: Anti-tampering detection
- ecc_hardware_manager: Hardware key integration
- fragmenter: Data splitting logic

Author: OBSIDIAN Team
Version: 2.0 (Iron Vault)
"""

__version__ = "2.0.0"
__author__ = "OBSIDIAN Team"

from .security_core import SecurityCore
from .key_derivation import KeyDerivationEngine
from .encryption_engine import EncryptionEngine
from .canary_tokens import CanaryTokenManager
from .ecc_hardware_manager import ECCHardwareManager
from .fragmenter import DataFragmenter

__all__ = [
    'SecurityCore',
    'KeyDerivationEngine',
    'EncryptionEngine',
    'CanaryTokenManager',
    'ECCHardwareManager',
    'DataFragmenter'
]

# Security configuration
SECURITY_CONFIG = {
    "pbkdf2_iterations": 100000,
    "aes_mode": "CTR",
    "aes_key_size": 256,
    "hmac_algorithm": "SHA512",
    "salt_size": 32,
    "nonce_size": 16,
    "fragment_b_size": 32,
    "canary_token_size": 16,
    "compression_level": 9
}

# Compliance standards
COMPLIANCE_STANDARDS = [
    "PDPA-2010",          # Personal Data Protection Act (Malaysia)
    "MAMPU",              # Malaysian Administrative Modernisation
    "FIPS-140-2",         # Federal Information Processing Standard
    "NSA-SUITE-B",        # NSA Suite B Cryptography
    "ISO-27001"           # Information Security Management
]

print(f"🛡️  OBSIDIAN Core Security Module v{__version__} loaded")
print(f"   Compliance: {', '.join(COMPLIANCE_STANDARDS)}")