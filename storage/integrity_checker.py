# storage/integrity_checker.py
"""
Integrity Checker
Merkle tree verification and data integrity validation
"""

import hashlib
import hmac
from typing import Dict, List, Tuple


class IntegrityChecker:
    """
    Verifies data integrity using Merkle trees
    
    Methods:
    - Compute merkle roots
    - Verify fragment integrity
    - Batch verification
    """
    
    def __init__(self):
        self.hash_algorithm = hashlib.sha512
    
    def compute_merkle_root(
        self,
        fragment_a: bytes,
        fragment_b: bytes
    ) -> str:
        """
        Compute merkle root for fragment pair
        
        Args:
            fragment_a: Large fragment
            fragment_b: Tiny fragment
        
        Returns:
            Merkle root (hex string)
        """
        
        # Hash both fragments
        hash_a = self.hash_algorithm(fragment_a).digest()
        hash_b = self.hash_algorithm(fragment_b).digest()
        
        # Combine and double-hash (Bitcoin-style)
        combined = hash_a + hash_b
        first_hash = self.hash_algorithm(combined).digest()
        merkle_root = self.hash_algorithm(first_hash).hexdigest()
        
        return merkle_root
    
    def verify_merkle_root(
        self,
        fragment_a: bytes,
        fragment_b: bytes,
        expected_root: str
    ) -> bool:
        """
        Verify merkle root matches expected value
        
        Returns:
            True if valid
        """
        
        computed_root = self.compute_merkle_root(fragment_a, fragment_b)
        return hmac.compare_digest(computed_root, expected_root)
    
    def verify_fragment_hash(
        self,
        fragment: bytes,
        expected_hash: str
    ) -> bool:
        """
        Verify individual fragment hash
        
        Args:
            fragment: Fragment data
            expected_hash: Expected SHA-256 hash
        
        Returns:
            True if hash matches
        """
        
        computed_hash = hashlib.sha256(fragment).hexdigest()
        return hmac.compare_digest(computed_hash, expected_hash)
    
    def batch_verify(
        self,
        fragments: List[Tuple[bytes, bytes, str]]
    ) -> Dict[int, bool]:
        """
        Verify multiple fragment pairs
        
        Args:
            fragments: List of (fragment_a, fragment_b, merkle_root) tuples
        
        Returns:
            Dictionary mapping index to verification result
        """
        
        results = {}
        
        for i, (frag_a, frag_b, merkle) in enumerate(fragments):
            is_valid = self.verify_merkle_root(frag_a, frag_b, merkle)
            results[i] = is_valid
        
        return results
    
    def generate_integrity_report(
        self,
        fragment_a: bytes,
        fragment_b: bytes,
        merkle_root: str
    ) -> Dict:
        """
        Generate detailed integrity report
        
        Returns:
            Integrity report dictionary
        """
        
        computed_root = self.compute_merkle_root(fragment_a, fragment_b)
        is_valid = hmac.compare_digest(computed_root, merkle_root)
        
        return {
            "merkle_root_valid": is_valid,
            "expected_merkle": merkle_root,
            "computed_merkle": computed_root,
            "fragment_a_hash": hashlib.sha256(fragment_a).hexdigest(),
            "fragment_b_hash": hashlib.sha256(fragment_b).hexdigest(),
            "fragment_a_size": len(fragment_a),
            "fragment_b_size": len(fragment_b),
            "verification_algorithm": "SHA-512 Double Hash"
        }


if __name__ == "__main__":
    checker = IntegrityChecker()
    
    # Test data
    frag_a = b"large-fragment-data" * 50
    frag_b = b"tiny-fragment-32bytes-exactly!!"
    
    # Compute merkle
    merkle = checker.compute_merkle_root(frag_a, frag_b)
    print(f"✅ Merkle root: {merkle[:32]}...")
    
    # Verify
    is_valid = checker.verify_merkle_root(frag_a, frag_b, merkle)
    print(f"✅ Verification: {is_valid}")
    
    # Generate report
    report = checker.generate_integrity_report(frag_a, frag_b, merkle)
    print(f"✅ Report: {report['merkle_root_valid']}")
