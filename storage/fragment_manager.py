# storage/fragment_manager.py
"""
Fragment Manager
Manages Fragment A/B lifecycle
"""

import hashlib
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta


class FragmentManager:
    """
    Manages fragment lifecycle and relationships
    
    Tracks:
    - Fragment A location (PDSA SAN)
    - Fragment B location (Blockchain)
    - Fragment binding
    - Lifecycle states
    """
    
    def __init__(self):
        self.fragment_registry = {}
    
    def register_fragment_pair(
        self,
        did: str,
        fragment_a_path: str,
        fragment_b_hex: str,
        merkle_root: str,
        metadata: Dict
    ):
        """
        Register a fragment pair
        
        Args:
            did: User identifier
            fragment_a_path: Path to Fragment A in SAN
            fragment_b_hex: Fragment B as hex (on blockchain)
            merkle_root: Merkle root for integrity
            metadata: Additional metadata
        """
        
        self.fragment_registry[did] = {
            "fragment_a": {
                "location": "pdsa_san",
                "path": fragment_a_path,
                "size": metadata.get('fragment_a_size', 0)
            },
            "fragment_b": {
                "location": "blockchain",
                "hex": fragment_b_hex,
                "size": 32
            },
            "merkle_root": merkle_root,
            "created_at": datetime.now().isoformat(),
            "last_accessed": None,
            "access_count": 0,
            "status": "active"
        }
    
    def get_fragment_info(self, did: str) -> Optional[Dict]:
        """Get fragment information"""
        return self.fragment_registry.get(did)
    
    def record_access(self, did: str):
        """Record fragment access"""
        if did in self.fragment_registry:
            self.fragment_registry[did]['last_accessed'] = datetime.now().isoformat()
            self.fragment_registry[did]['access_count'] += 1
    
    def mark_for_deletion(self, did: str):
        """Mark fragment pair for deletion"""
        if did in self.fragment_registry:
            self.fragment_registry[did]['status'] = 'pending_deletion'
    
    def get_statistics(self) -> Dict:
        """Get fragment statistics"""
        total = len(self.fragment_registry)
        active = sum(1 for f in self.fragment_registry.values() if f['status'] == 'active')
        
        total_size = sum(
            f['fragment_a']['size'] + f['fragment_b']['size']
            for f in self.fragment_registry.values()
        )
        
        return {
            "total_fragments": total,
            "active_fragments": active,
            "total_size_bytes": total_size,
            "avg_access_count": sum(f['access_count'] for f in self.fragment_registry.values()) / max(total, 1)
        }


if __name__ == "__main__":
    manager = FragmentManager()
    
    # Register fragment
    manager.register_fragment_pair(
        did="did:zetrix:test",
        fragment_a_path="/mnt/pdsa_san/test.frag",
        fragment_b_hex="abcd1234",
        merkle_root="merkle123",
        metadata={"fragment_a_size": 1000}
    )
    
    # Get info
    info = manager.get_fragment_info("did:zetrix:test")
    print(f"✅ Fragment info: {info}")
    
    # Record access
    manager.record_access("did:zetrix:test")
    
    # Get stats
    stats = manager.get_statistics()
    print(f"✅ Statistics: {stats}")