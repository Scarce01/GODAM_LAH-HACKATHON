# hardware/__init__.py
"""
OBSIDIAN Hardware Integration Module
MyKad NFC and Phone Secure Enclave interfaces

Components:
- mykad_interface: MyKad NFC secure element interface
- phone_tee_interface: Phone Trusted Execution Environment
- hardware_authenticator: Combined hardware authentication
- ecc_key_manager: ECC key management for hardware

Author: OBSIDIAN Team
Version: 2.0 (Iron Vault - Hardware Security)
"""

__version__ = "2.0.0"
__author__ = "OBSIDIAN Team"

from .mykad_interface import MyKadInterface
from .phone_tee_interface import PhoneTEEInterface
from .hardware_authenticator import HardwareAuthenticator
from .ecc_key_manager import ECCKeyManager

__all__ = [
    'MyKadInterface',
    'PhoneTEEInterface',
    'HardwareAuthenticator',
    'ECCKeyManager'
]

# Hardware configuration
HARDWARE_CONFIG = {
    "mykad": {
        "protocol": "ISO14443A",
        "frequency": "13.56MHz",
        "data_rate": "106kbps",
        "secure_element": "JavaCard",
        "key_algorithm": "ECC_P256",
        "timeout_ms": 5000
    },
    "phone_tee": {
        "android_keystore": "AndroidKeyStore",
        "ios_secure_enclave": "SecureEnclave",
        "key_algorithm": "ECC_P256",
        "biometric_required": True,
        "key_protection": "STRONGBOX_BACKED"
    },
    "authentication": {
        "require_both": True,
        "challenge_size": 32,
        "signature_algorithm": "ECDSA_SHA256",
        "max_retry_attempts": 3
    }
}

print(f"🔐 OBSIDIAN Hardware Module v{__version__} loaded")
print(f"   MyKad: NFC ISO14443A @ 13.56MHz")
print(f"   Phone TEE: ECC P-256 + Biometric")
print(f"   Authentication: Dual-factor required")