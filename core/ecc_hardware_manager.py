# core/ecc_hardware_manager.py
"""
ECC Hardware Manager
Manages hardware key interfaces (MyKad + Phone TEE)
"""

import hashlib
from typing import Tuple, Optional


class ECCHardwareManager:
    """
    Manages ECC hardware key operations
    
    Interfaces:
    - MyKad NFC secure element
    - Phone trusted execution environment (TEE)
    """
    
    def __init__(self):
        self.curve = "P-256"  # NIST standard
        self.key_size = 32    # 256 bits
    
    def derive_keys_from_public(
        self,
        card_public_key: bytes,
        phone_public_key: bytes,
        did: str
    ) -> Tuple[bytes, bytes]:
        """
        Derive IC_KEY and PHONE_KEY from public keys
        
        Args:
            card_public_key: Card's ECC public key (PEM format)
            phone_public_key: Phone's ECC public key (PEM format)
            did: User's decentralized identifier
        
        Returns:
            (ic_key, phone_key) - each 32 bytes
        """
        
        # HKDF derivation from public keys
        ic_key = self._hkdf_derive(
            card_public_key,
            salt=b"OBSIDIAN_IC_CARD_KEY_V1",
            info=did.encode('utf-8')
        )
        
        phone_key = self._hkdf_derive(
            phone_public_key,
            salt=b"OBSIDIAN_PHONE_KEY_V1",
            info=did.encode('utf-8')
        )
        
        return ic_key, phone_key
    
    def generate_key_fingerprint(
        self,
        ic_key: bytes,
        phone_key: bytes
    ) -> str:
        """
        Generate fingerprint of key pair
        
        Args:
            ic_key: IC card key
            phone_key: Phone key
        
        Returns:
            16-character hex fingerprint
        """
        combined = ic_key + phone_key
        fingerprint_hash = hashlib.sha256(combined).hexdigest()
        return fingerprint_hash[:16]
    
    def verify_hardware_signature(
        self,
        data: bytes,
        signature: bytes,
        public_key: bytes
    ) -> bool:
        """
        Verify signature from hardware device
        
        Args:
            data: Data that was signed
            signature: ECDSA signature
            public_key: Device's public key
        
        Returns:
            True if signature valid
        """
        # In production: use cryptography library
        # For now: simplified verification
        expected = hashlib.sha256(public_key + data).digest()
        return signature == expected[:len(signature)]
    
    def _hkdf_derive(
        self,
        input_material: bytes,
        salt: bytes,
        info: bytes
    ) -> bytes:
        """
        HKDF key derivation
        
        Args:
            input_material: Input key material
            salt: Salt value
            info: Context information
        
        Returns:
            Derived key (32 bytes)
        """
        # Extract
        prk = hashlib.sha256(salt + input_material).digest()
        
        # Expand
        okm = hashlib.sha256(prk + info + b'\x01').digest()
        
        return okm[:self.key_size]
    
    def validate_hardware_keys(
        self,
        ic_key: bytes,
        phone_key: bytes
    ) -> Tuple[bool, str]:
        """
        Validate hardware keys meet security requirements
        
        Returns:
            (is_valid, message)
        """
        
        # Check length
        if len(ic_key) != 32:
            return False, f"IC key must be 32 bytes, got {len(ic_key)}"
        
        if len(phone_key) != 32:
            return False, f"Phone key must be 32 bytes, got {len(phone_key)}"
        
        # Check not all zeros
        if ic_key == b'\x00' * 32:
            return False, "IC key cannot be all zeros"
        
        if phone_key == b'\x00' * 32:
            return False, "Phone key cannot be all zeros"
        
        # Check entropy
        ic_entropy = sum(bin(b).count('1') for b in ic_key) / (32 * 8)
        phone_entropy = sum(bin(b).count('1') for b in phone_key) / (32 * 8)
        
        if ic_entropy < 0.3 or ic_entropy > 0.7:
            return False, f"IC key has unusual entropy: {ic_entropy:.2%}"
        
        if phone_entropy < 0.3 or phone_entropy > 0.7:
            return False, f"Phone key has unusual entropy: {phone_entropy:.2%}"
        
        return True, "Hardware keys valid"


# Testing
if __name__ == "__main__":
    manager = ECCHardwareManager()
    
    # Simulate public keys
    card_pub = b"card-public-key-pem-format-here"
    phone_pub = b"phone-public-key-pem-format-here"
    did = "did:zetrix:mykad-123"
    
    # Derive keys
    ic_key, phone_key = manager.derive_keys_from_public(card_pub, phone_pub, did)
    print(f"✅ IC Key: {ic_key.hex()[:32]}...")
    print(f"✅ Phone Key: {phone_key.hex()[:32]}...")
    
    # Generate fingerprint
    fingerprint = manager.generate_key_fingerprint(ic_key, phone_key)
    print(f"✅ Fingerprint: {fingerprint}")
    
    # Validate
    is_valid, message = manager.validate_hardware_keys(ic_key, phone_key)
    print(f"✅ Validation: {message}")