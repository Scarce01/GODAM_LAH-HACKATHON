# core/fragmenter.py
"""
Data Fragmenter
Splits data into Fragment A (large) and Fragment B (tiny)
"""

import hashlib
import json
from typing import Dict, Tuple, Any


class DataFragmenter:
    """
    Manages data fragmentation logic
    
    Fragment A: Large encrypted payload → PDSA SAN
    Fragment B: Tiny 32-byte anchor → Blockchain
    """
    
    def __init__(self):
        self.fragment_b_size = 32  # Fixed 32 bytes
    
    def create_fragment_b(
        self,
        fragment_a: bytes,
        ic_key: bytes,
        phone_key: bytes
    ) -> bytes:
        """
        Create Fragment B binding token
        
        Args:
            fragment_a: Large encrypted fragment
            ic_key: IC card key
            phone_key: Phone key
        
        Returns:
            32-byte Fragment B
        """
        
        # Create binding data
        binding_data = (
            hashlib.sha512(fragment_a).digest() +
            hashlib.sha512(ic_key).digest() +
            hashlib.sha512(phone_key).digest()
        )
        
        # Hash to 32 bytes
        fragment_b = hashlib.sha512(binding_data).digest()[:self.fragment_b_size]
        
        return fragment_b
    
    def verify_fragment_binding(
        self,
        fragment_a: bytes,
        fragment_b: bytes,
        ic_key: bytes,
        phone_key: bytes
    ) -> bool:
        """
        Verify Fragment B is bound to Fragment A and keys
        
        Returns:
            True if binding valid
        """
        
        expected_b = self.create_fragment_b(fragment_a, ic_key, phone_key)
        
        # Constant-time comparison
        return fragment_b == expected_b
    
    def compute_merkle_root(
        self,
        fragment_a: bytes,
        fragment_b: bytes
    ) -> str:
        """
        Compute merkle root for integrity verification
        
        Args:
            fragment_a: Large fragment
            fragment_b: Tiny fragment
        
        Returns:
            128-character hex merkle root
        """
        
        # Hash both fragments
        hash_a = hashlib.sha512(fragment_a).digest()
        hash_b = hashlib.sha512(fragment_b).digest()
        
        # Combine and double-hash (Bitcoin-style)
        combined = hash_a + hash_b
        first_hash = hashlib.sha512(combined).digest()
        merkle_root = hashlib.sha512(first_hash).hexdigest()
        
        return merkle_root
    
    def verify_merkle_root(
        self,
        fragment_a: bytes,
        fragment_b: bytes,
        expected_root: str
    ) -> bool:
        """
        Verify merkle root matches
        
        Returns:
            True if merkle root valid
        """
        
        computed_root = self.compute_merkle_root(fragment_a, fragment_b)
        return computed_root == expected_root


# Testing
if __name__ == "__main__":
    fragmenter = DataFragmenter()
    
    # Test data
    fragment_a = b"large-encrypted-data-here" * 20
    ic_key = b"ic-key-32bytes-hardware!!!!!!!!"
    phone_key = b"phone-key-32bytes-hardware!!!!!"
    
    # Create Fragment B
    fragment_b = fragmenter.create_fragment_b(fragment_a, ic_key, phone_key)
    print(f"✅ Fragment A: {len(fragment_a)} bytes")
    print(f"✅ Fragment B: {len(fragment_b)} bytes")
    
    # Verify binding
    assert fragmenter.verify_fragment_binding(fragment_a, fragment_b, ic_key, phone_key)
    print(f"✅ Fragment binding verified")
    
    # Compute merkle root
    merkle = fragmenter.compute_merkle_root(fragment_a, fragment_b)
    print(f"✅ Merkle root: {merkle[:32]}...")
    
    # Verify merkle
    assert fragmenter.verify_merkle_root(fragment_a, fragment_b, merkle)
    print(f"✅ Merkle root verified")
