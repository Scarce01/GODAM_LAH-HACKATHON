# storage/__init__.py
"""
OBSIDIAN Storage Module
PDSA Local Storage System (Replaces Cloud Storage)

Components:
- pdsa_local_storage: Main storage manager for PDSA SAN
- san_interface: SAN network protocol handler
- fragment_manager: Fragment A/B lifecycle management
- integrity_checker: Merkle tree verification

Author: OBSIDIAN Team
Version: 2.0 (Iron Vault - On-Premise)
"""

__version__ = "2.0.0"
__author__ = "OBSIDIAN Team"

from .pdsa_local_storage import PDSALocalStorage
from .san_interface import SANInterface
from .fragment_manager import FragmentManager
from .integrity_checker import IntegrityChecker

# Backward compatibility alias
CloudStorageManager = PDSALocalStorage

__all__ = [
    'PDSALocalStorage',
    'SANInterface',
    'FragmentManager',
    'IntegrityChecker',
    'CloudStorageManager'  # For backward compatibility
]

# Storage configuration
STORAGE_CONFIG = {
    "default_san_path": "/mnt/pdsa_san/fragments",
    "backup_san_path": "/mnt/pdsa_san_backup/fragments",
    "metadata_file": "fragment_metadata.json",
    "max_fragment_size": 10 * 1024 * 1024,  # 10 MB
    "enable_compression": True,
    "enable_encryption_at_rest": True,
    "replication_factor": 3,  # Number of copies
    "storage_type": "pdsa_san"
}

print(f"💾 OBSIDIAN Storage Module v{__version__} loaded")
print(f"   Storage Type: {STORAGE_CONFIG['storage_type'].upper()}")
print(f"   Location: On-Premise PDSA SAN")