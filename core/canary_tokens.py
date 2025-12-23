# core/canary_tokens.py
"""
Canary Token Manager
Anti-tampering detection system
"""

import hashlib
import hmac
import secrets
from typing import Tuple


class CanaryTokenManager:
    """
    Manages canary tokens for tampering detection
    
    How it works:
    - Inserts random tokens into encrypted data
    - Verifies tokens on decryption
    - Any modification corrupts tokens → detection
    """
    
    def __init__(self):
        self.token_size = 16  # 128 bits per token
        self.num_tokens = 3   # Number of canaries
    
    def inject_tokens(self, data: bytes) -> Tuple[bytes, bytes]:
        """
        Inject canary tokens into data
        
        Args:
            data: Original data
        
        Returns:
            (data_with_canaries, verification_hash)
        """
        
        # Generate random canary tokens
        canaries = [secrets.token_bytes(self.token_size) for _ in range(self.num_tokens)]
        
        # Split data into chunks
        chunk_size = len(data) // self.num_tokens
        chunks = []
        
        for i in range(self.num_tokens):
            start = i * chunk_size
            if i == self.num_tokens - 1:
                chunks.append(data[start:])
            else:
                chunks.append(data[start:start + chunk_size])
        
        # Interleave chunks and canaries
        result = bytearray()
        for i in range(self.num_tokens):
            result.extend(chunks[i])
            result.extend(canaries[i])
        
        # Create verification hash
        verification = hashlib.sha256(b''.join(canaries)).digest()
        
        return bytes(result), verification
    
    def verify_and_extract(
        self,
        data_with_canaries: bytes,
        verification: bytes,
        original_length: int
    ) -> bytes:
        """
        Verify canaries and extract original data
        
        Args:
            data_with_canaries: Data with embedded tokens
            verification: Expected verification hash
            original_length: Original data length
        
        Returns:
            Original data without canaries
        
        Raises:
            ValueError: If canaries are corrupted
        """
        
        # Calculate chunk size
        chunk_size = original_length // self.num_tokens
        
        # Extract chunks and canaries
        chunks = []
        canaries = []
        offset = 0
        
        for i in range(self.num_tokens):
            # Get chunk
            if i == self.num_tokens - 1:
                remaining = original_length - (chunk_size * (self.num_tokens - 1))
                chunks.append(data_with_canaries[offset:offset + remaining])
                offset += remaining
            else:
                chunks.append(data_with_canaries[offset:offset + chunk_size])
                offset += chunk_size
            
            # Get canary
            canaries.append(data_with_canaries[offset:offset + self.token_size])
            offset += self.token_size
        
        # Verify canaries
        computed_verification = hashlib.sha256(b''.join(canaries)).digest()
        
        if not hmac.compare_digest(verification, computed_verification):
            raise ValueError("🚨 Canary tokens corrupted - data has been tampered!")
        
        # Reconstruct original data
        return b''.join(chunks)


# Testing
if __name__ == "__main__":
    manager = CanaryTokenManager()
    
    original_data = b"This is secret Malaysian identity data that must be protected"
    
    # Inject canaries
    protected, verification = manager.inject_tokens(original_data)
    print(f"✅ Original: {len(original_data)} bytes")
    print(f"✅ Protected: {len(protected)} bytes")
    
    # Verify and extract
    recovered = manager.verify_and_extract(protected, verification, len(original_data))
    assert recovered == original_data
    print(f"✅ Canaries verified, data recovered")
    
    # Test tampering detection
    try:
        tampered = bytearray(protected)
        tampered[50] ^= 0xFF
        manager.verify_and_extract(bytes(tampered), verification, len(original_data))
        print("❌ Failed to detect tampering")
    except ValueError as e:
        print(f"✅ Tampering detected: {str(e)[:50]}...")