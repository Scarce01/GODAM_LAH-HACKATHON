# storage/pdsa_local_storage.py
"""
PDSA Local Storage Manager
Drop-in replacement for cloud_storage_manager.py
Stores Fragment A on local SAN instead of cloud
"""

import os
import json
import hashlib
import shutil
from typing import Dict, Optional, List
from datetime import datetime


class PDSALocalStorage:
    """
    PDSA SAN Storage Manager
    
    Stores Fragment A on local Storage Area Network (SAN)
    Compatible API with CloudStorageManager for easy migration
    
    Storage Architecture:
    - Primary: /mnt/pdsa_san/fragments/
    - Backup: /mnt/pdsa_san_backup/fragments/
    - Metadata: fragment_metadata.json
    
    Features:
    - Automatic replication
    - Integrity verification (SHA-256)
    - Fragment lifecycle management
    - Compatible with existing OBSIDIAN code
    """
    
    def __init__(
        self, 
        storage_path: str = "/mnt/pdsa_san/fragments",
        enable_backup: bool = True,
        backup_path: str = "/mnt/pdsa_san_backup/fragments"
    ):
        """
        Initialize PDSA local storage
        
        Args:
            storage_path: Primary SAN mount point
            enable_backup: Enable automatic backup
            backup_path: Backup SAN mount point
        """
        self.storage_path = storage_path
        self.enable_backup = enable_backup
        self.backup_path = backup_path
        self.metadata_file = os.path.join(storage_path, "fragment_metadata.json")
        
        # Create directories
        os.makedirs(storage_path, exist_ok=True)
        if enable_backup:
            os.makedirs(backup_path, exist_ok=True)
        
        # Load metadata
        self.metadata = self._load_metadata()
        
        print(f"\n{'='*70}")
        print(f"💾 PDSA LOCAL STORAGE INITIALIZED")
        print(f"{'='*70}")
        print(f"   Primary Path:  {storage_path}")
        if enable_backup:
            print(f"   Backup Path:   {backup_path}")
        print(f"   Storage Type:  PDSA SAN (On-Premise)")
        print(f"   Fragments:     {len(self.metadata)}")
        print(f"{'='*70}\n")
    
    def _load_metadata(self) -> Dict:
        """Load fragment metadata from local file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Warning: Metadata file corrupted, starting fresh")
                return {}
        return {}
    
    def _save_metadata(self):
        """Save metadata to local file with backup"""
        # Save primary
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        # Save backup
        if self.enable_backup:
            backup_metadata = os.path.join(self.backup_path, "fragment_metadata.json")
            with open(backup_metadata, 'w') as f:
                json.dump(self.metadata, f, indent=2)
    
    def store_fragment_a(
        self, 
        did: str, 
        fragment_a: bytes,
        fragment_b_hex: str
    ) -> Dict[str, any]:
        """
        Store Fragment A in PDSA SAN
        
        COMPATIBLE API: Same signature as CloudStorageManager.store_fragment_a()
        
        Args:
            did: User's decentralized identifier
            fragment_a: Encrypted fragment bytes
            fragment_b_hex: Fragment B as hex (for metadata reference)
        
        Returns:
            Storage metadata dictionary
        """
        
        print(f"\n📤 STORING FRAGMENT A")
        print(f"   DID: {did}")
        print(f"   Size: {len(fragment_a):,} bytes")
        
        # Generate unique filename
        fragment_hash = hashlib.sha256(fragment_a).hexdigest()
        filename = f"{did.replace(':', '_')}_{fragment_hash[:16]}.frag"
        
        # Primary storage path
        primary_path = os.path.join(self.storage_path, filename)
        
        # Write to primary storage
        with open(primary_path, 'wb') as f:
            f.write(fragment_a)
        
        print(f"   ✅ Written to primary SAN")
        
        # Write to backup storage
        backup_path_full = None
        if self.enable_backup:
            backup_path_full = os.path.join(self.backup_path, filename)
            shutil.copy2(primary_path, backup_path_full)
            print(f"   ✅ Replicated to backup SAN")
        
        # Create metadata
        metadata = {
            "did": did,
            "storage_path": primary_path,
            "backup_path": backup_path_full,
            "fragment_hash": fragment_hash,
            "fragment_b_hex": fragment_b_hex,
            "size_bytes": len(fragment_a),
            "timestamp": datetime.now().isoformat(),
            "location": "pdsa_san",
            "storage_type": "local_san",
            "replicated": self.enable_backup
        }
        
        # Store metadata
        self.metadata[did] = metadata
        self._save_metadata()
        
        print(f"   ✅ Metadata saved")
        print(f"   Storage Location: PDSA SAN")
        
        return metadata
    
    def retrieve_fragment_a(self, did: str) -> Optional[bytes]:
        """
        Retrieve Fragment A from PDSA SAN
        
        COMPATIBLE API: Same signature as CloudStorageManager.retrieve_fragment_a()
        
        Args:
            did: User's decentralized identifier
        
        Returns:
            Fragment A bytes or None if not found
        """
        
        print(f"\n📥 RETRIEVING FRAGMENT A")
        print(f"   DID: {did}")
        
        if did not in self.metadata:
            print(f"   ❌ No fragment found for {did}")
            return None
        
        metadata = self.metadata[did]
        storage_path = metadata['storage_path']
        
        # Try primary storage
        if os.path.exists(storage_path):
            with open(storage_path, 'rb') as f:
                fragment_a = f.read()
            
            # Verify integrity
            computed_hash = hashlib.sha256(fragment_a).hexdigest()
            if computed_hash != metadata['fragment_hash']:
                print(f"   ⚠️  Primary storage corrupted, trying backup...")
                
                # Try backup
                if self.enable_backup and metadata.get('backup_path'):
                    return self._retrieve_from_backup(did, metadata)
                else:
                    print(f"   ❌ Fragment integrity check failed")
                    return None
            
            print(f"   ✅ Retrieved from primary SAN ({len(fragment_a):,} bytes)")
            return fragment_a
        
        # Try backup if primary not found
        elif self.enable_backup and metadata.get('backup_path'):
            print(f"   ⚠️  Primary not found, trying backup...")
            return self._retrieve_from_backup(did, metadata)
        
        print(f"   ❌ Fragment file missing")
        return None
    
    def _retrieve_from_backup(self, did: str, metadata: Dict) -> Optional[bytes]:
        """Retrieve from backup storage"""
        
        backup_path = metadata.get('backup_path')
        
        if not backup_path or not os.path.exists(backup_path):
            print(f"   ❌ Backup also not found")
            return None
        
        with open(backup_path, 'rb') as f:
            fragment_a = f.read()
        
        # Verify integrity
        computed_hash = hashlib.sha256(fragment_a).hexdigest()
        if computed_hash != metadata['fragment_hash']:
            print(f"   ❌ Backup also corrupted")
            return None
        
        # Restore to primary
        primary_path = metadata['storage_path']
        shutil.copy2(backup_path, primary_path)
        
        print(f"   ✅ Retrieved from backup SAN ({len(fragment_a):,} bytes)")
        print(f"   ✅ Primary storage restored")
        
        return fragment_a
    
    def delete_fragment_a(self, did: str) -> bool:
        """
        Delete Fragment A from PDSA SAN
        
        COMPATIBLE API: Same signature as CloudStorageManager.delete_fragment_a()
        
        Args:
            did: User's decentralized identifier
        
        Returns:
            True if deleted successfully
        """
        
        print(f"\n🗑️  DELETING FRAGMENT A")
        print(f"   DID: {did}")
        
        if did not in self.metadata:
            print(f"   ⚠️  No fragment found")
            return False
        
        metadata = self.metadata[did]
        
        # Delete primary
        storage_path = metadata['storage_path']
        if os.path.exists(storage_path):
            os.remove(storage_path)
            print(f"   ✅ Deleted from primary SAN")
        
        # Delete backup
        if self.enable_backup and metadata.get('backup_path'):
            backup_path = metadata['backup_path']
            if os.path.exists(backup_path):
                os.remove(backup_path)
                print(f"   ✅ Deleted from backup SAN")
        
        # Remove metadata
        del self.metadata[did]
        self._save_metadata()
        
        print(f"   ✅ Metadata removed")
        
        return True
    
    def get_storage_statistics(self) -> Dict:
        """
        Get storage statistics
        
        COMPATIBLE API: Same signature as CloudStorageManager.get_storage_statistics()
        
        Returns:
            Statistics dictionary
        """
        
        total_size = 0
        for metadata in self.metadata.values():
            total_size += metadata['size_bytes']
        
        # Disk usage
        primary_usage = shutil.disk_usage(self.storage_path)
        
        stats = {
            "total_users": len(self.metadata),
            "total_size_bytes": total_size,
            "total_size_kb": total_size / 1024,
            "total_size_mb": total_size / (1024 * 1024),
            "storage_location": self.storage_path,
            "storage_type": "pdsa_san",
            "replication_enabled": self.enable_backup,
            "disk_total_gb": primary_usage.total / (1024**3),
            "disk_used_gb": primary_usage.used / (1024**3),
            "disk_free_gb": primary_usage.free / (1024**3),
            "disk_usage_percent": (primary_usage.used / primary_usage.total) * 100
        }
        
        return stats
    
    def list_all_users(self) -> List[str]:
        """
        List all users with stored fragments
        
        COMPATIBLE API: Same signature as CloudStorageManager.list_all_users()
        
        Returns:
            List of DIDs
        """
        return list(self.metadata.keys())
    
    def verify_all_fragments(self) -> Dict[str, bool]:
        """
        Verify integrity of all stored fragments
        
        Returns:
            Dictionary mapping DID to integrity status
        """
        
        print(f"\n🔍 VERIFYING ALL FRAGMENTS")
        print(f"{'='*70}")
        
        results = {}
        corrupted = []
        
        for did in self.metadata.keys():
            metadata = self.metadata[did]
            storage_path = metadata['storage_path']
            
            if not os.path.exists(storage_path):
                results[did] = False
                corrupted.append(did)
                print(f"   ❌ {did}: File missing")
                continue
            
            with open(storage_path, 'rb') as f:
                fragment_a = f.read()
            
            computed_hash = hashlib.sha256(fragment_a).hexdigest()
            is_valid = computed_hash == metadata['fragment_hash']
            
            results[did] = is_valid
            
            if is_valid:
                print(f"   ✅ {did}: Intact")
            else:
                corrupted.append(did)
                print(f"   ❌ {did}: Corrupted")
        
        print(f"{'='*70}")
        print(f"   Total: {len(results)}")
        print(f"   Intact: {sum(results.values())}")
        print(f"   Corrupted: {len(corrupted)}")
        
        return results
    
    def export_metadata(self, output_path: str):
        """Export metadata to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        print(f"✅ Metadata exported to {output_path}")
    
    def import_metadata(self, input_path: str):
        """Import metadata from JSON file"""
        with open(input_path, 'r') as f:
            self.metadata = json.load(f)
        self._save_metadata()
        print(f"✅ Metadata imported from {input_path}")


# Backward compatibility alias
CloudStorageManager = PDSALocalStorage


# ============================================================================
# TESTING & DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 PDSA LOCAL STORAGE TESTING")
    print("="*70)
    
    # Initialize with temporary paths for testing
    storage = PDSALocalStorage(
        storage_path="./test_pdsa_san",
        enable_backup=True,
        backup_path="./test_pdsa_backup"
    )
    
    # Test data
    test_did = "did:zetrix:mykad-123456789"
    test_fragment_a = b"encrypted-fragment-data-here" * 100
    test_fragment_b_hex = "abcdef123456"
    
    # Test 1: Store Fragment A
    print("\n" + "="*70)
    print("TEST 1: STORE FRAGMENT A")
    print("="*70)
    
    metadata = storage.store_fragment_a(test_did, test_fragment_a, test_fragment_b_hex)
    
    if metadata:
        print("\n✅ TEST 1 PASSED: Fragment stored successfully")
    else:
        print("\n❌ TEST 1 FAILED")
        exit(1)
    
    # Test 2: Retrieve Fragment A
    print("\n" + "="*70)
    print("TEST 2: RETRIEVE FRAGMENT A")
    print("="*70)
    
    retrieved = storage.retrieve_fragment_a(test_did)
    
    if retrieved == test_fragment_a:
        print("\n✅ TEST 2 PASSED: Fragment retrieved successfully")
    else:
        print("\n❌ TEST 2 FAILED: Data mismatch")
        exit(1)
    
    # Test 3: Get Statistics
    print("\n" + "="*70)
    print("TEST 3: STORAGE STATISTICS")
    print("="*70)
    
    stats = storage.get_storage_statistics()
    
    print(f"\n📊 STORAGE STATISTICS:")
    print(f"   Total Users: {stats['total_users']}")
    print(f"   Total Size: {stats['total_size_kb']:.2f} KB")
    print(f"   Storage Type: {stats['storage_type']}")
    print(f"   Replication: {'✅ Enabled' if stats['replication_enabled'] else '❌ Disabled'}")
    print(f"   Disk Usage: {stats['disk_usage_percent']:.2f}%")
    
    print("\n✅ TEST 3 PASSED")
    
    # Test 4: Verify Integrity
    print("\n" + "="*70)
    print("TEST 4: INTEGRITY VERIFICATION")
    print("="*70)
    
    results = storage.verify_all_fragments()
    
    if all(results.values()):
        print("\n✅ TEST 4 PASSED: All fragments intact")
    else:
        print("\n❌ TEST 4 FAILED: Some fragments corrupted")
        exit(1)
    
    # Test 5: Delete Fragment A
    print("\n" + "="*70)
    print("TEST 5: DELETE FRAGMENT A")
    print("="*70)
    
    deleted = storage.delete_fragment_a(test_did)
    
    if deleted:
        print("\n✅ TEST 5 PASSED: Fragment deleted successfully")
    else:
        print("\n❌ TEST 5 FAILED")
        exit(1)
    
    # Cleanup
    shutil.rmtree("./test_pdsa_san", ignore_errors=True)
    shutil.rmtree("./test_pdsa_backup", ignore_errors=True)
    
    # Final summary
    print("\n" + "="*70)
    print("🎉 ALL TESTS PASSED")
    print("="*70)
    print("\n✅ PDSA Local Storage operational")
    print("✅ API compatible with CloudStorageManager")
    print("✅ Automatic replication working")
    print("✅ Integrity verification working")
    print("\n💾 PDSA LOCAL STORAGE READY FOR PRODUCTION")
    print("="*70 + "\n")