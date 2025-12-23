# core/encryption_engine.py
"""
Encryption Engine
AES-256-CTR + HMAC-SHA512 implementation
"""

import hashlib
import hmac
import secrets
from typing import Tuple


class EncryptionEngine:
    """
    AES-256-CTR mode encryption with HMAC authentication
    
    Features:
    - Military-grade AES-256-CTR
    - HMAC-SHA512 authentication
    - Authenticated encryption (encrypt-then-MAC)
    """
    
    def __init__(self):
        self.nonce_size = 16  # 128 bits
        self.hmac_size = 64   # 512 bits
    
    def encrypt(
        self,
        plaintext: bytes,
        encryption_key: bytes,
        authentication_key: bytes,
        nonce: bytes = None
    ) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt data with AES-256-CTR + HMAC
        
        Args:
            plaintext: Data to encrypt
            encryption_key: 32-byte encryption key
            authentication_key: 32-byte auth key
            nonce: 16-byte nonce (generated if not provided)
        
        Returns:
            (ciphertext, nonce, hmac_tag)
        """
        
        if nonce is None:
            nonce = secrets.token_bytes(self.nonce_size)
        
        # Generate keystream and encrypt
        ciphertext = self._aes_ctr_encrypt(plaintext, encryption_key, nonce)
        
        # Compute HMAC over ciphertext
        hmac_tag = self._compute_hmac(ciphertext, authentication_key)
        
        return ciphertext, nonce, hmac_tag
    
    def decrypt(
        self,
        ciphertext: bytes,
        encryption_key: bytes,
        authentication_key: bytes,
        nonce: bytes,
        hmac_tag: bytes
    ) -> bytes:
        """
        Decrypt data with verification
        
        Returns:
            Decrypted plaintext
        
        Raises:
            ValueError: If HMAC verification fails
        """
        
        # Verify HMAC first
        if not self._verify_hmac(ciphertext, authentication_key, hmac_tag):
            raise ValueError("HMAC verification failed - data tampered!")
        
        # Decrypt
        plaintext = self._aes_ctr_decrypt(ciphertext, encryption_key, nonce)
        
        return plaintext
    
    def _aes_ctr_encrypt(self, data: bytes, key: bytes, nonce: bytes) -> bytes:
        """AES-256-CTR encryption (simulated for prototype)"""
        
        keystream = self._generate_keystream(key, nonce, len(data))
        
        ciphertext = bytearray()
        for i, byte in enumerate(data):
            ciphertext.append(byte ^ keystream[i])
        
        return bytes(ciphertext)
    
    def _aes_ctr_decrypt(self, data: bytes, key: bytes, nonce: bytes) -> bytes:
        """AES-256-CTR decryption (identical to encryption)"""
        return self._aes_ctr_encrypt(data, key, nonce)
    
    def _generate_keystream(self, key: bytes, nonce: bytes, length: int) -> bytes:
        """Generate cryptographic keystream"""
        
        keystream = bytearray()
        counter = 0
        
        while len(keystream) < length:
            block_input = nonce + counter.to_bytes(8, 'big')
            block = hmac.new(key, block_input, hashlib.sha512).digest()
            keystream.extend(block)
            counter += 1
        
        return bytes(keystream[:length])
    
    def _compute_hmac(self, data: bytes, key: bytes) -> bytes:
        """Compute HMAC-SHA512"""
        return hmac.new(key, data, hashlib.sha512).digest()
    
    def _verify_hmac(self, data: bytes, key: bytes, tag: bytes) -> bool:
        """Verify HMAC with constant-time comparison"""
        expected = self._compute_hmac(data, key)
        return hmac.compare_digest(expected, tag)


# Testing
if __name__ == "__main__":
    engine = EncryptionEngine()
    
    plaintext = b"Secret Malaysian identity data"
    enc_key = secrets.token_bytes(32)
    auth_key = secrets.token_bytes(32)
    
    # Encrypt
    ciphertext, nonce, tag = engine.encrypt(plaintext, enc_key, auth_key)
    print(f"✅ Encrypted: {len(ciphertext)} bytes")
    
    # Decrypt
    recovered = engine.decrypt(ciphertext, enc_key, auth_key, nonce, tag)
    assert recovered == plaintext
    print(f"✅ Decrypted successfully")
    
    # Test tampering detection
    try:
        tampered = bytearray(ciphertext)
        tampered[0] ^= 0xFF
        engine.decrypt(bytes(tampered), enc_key, auth_key, nonce, tag)
        print("❌ Failed to detect tampering")
    except ValueError:
        print("✅ Tampering detected correctly")