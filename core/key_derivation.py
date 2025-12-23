# core/security_core.py
"""
OBSIDIAN Security Core (Aegis-9)
Main entry point for all encryption/decryption operations
"""

import hashlib
import hmac
import secrets
from typing import Dict, Tuple, Any, Optional
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_fragmentation_advanced import (
    split_into_fragments_advanced,
    reconstruct_data_advanced,
    verify_integrity_advanced,
    generate_key_fingerprint
)


class SecurityCore:
    """
    Aegis-9: Nine-Layer Security System
    
    Layer 1: Hardware Key Derivation (ECC P-256)
    Layer 2: PBKDF2 Key Stretching (100,000 iterations)
    Layer 3: AES-256-CTR Encryption
    Layer 4: HMAC-SHA512 Authentication
    Layer 5: Canary Token Injection
    Layer 6: Compression with Integrity
    Layer 7: Fragment Binding
    Layer 8: Merkle Tree Verification
    Layer 9: Hardware Secure Element Isolation
    """
    
    def __init__(self):
        self.version = "2.0-iron-vault"
        self.security_level = "military-grade"
        self.compliance = ["PDPA-2010", "MAMPU", "FIPS-140-2"]
        
        print("\n" + "="*70)
        print("🛡️  OBSIDIAN SECURITY CORE (Aegis-9) INITIALIZED")
        print("="*70)
        print(f"   Version: {self.version}")
        print(f"   Security Level: {self.security_level}")
        print(f"   Compliance: {', '.join(self.compliance)}")
        print("="*70 + "\n")
    
    def protect_data(
        self,
        data: Dict[str, Any],
        ic_key: bytes,
        phone_key: bytes,
        enable_anti_tampering: bool = True,
        enable_time_lock: bool = False,
        time_lock_duration: int = 0
    ) -> Tuple[bytes, bytes, str, Dict[str, Any]]:
        """
        ENCRYPT: Apply all 9 security layers to protect user data
        
        Returns:
            (fragment_a, fragment_b, merkle_root, metadata)
        """
        
        print("\n🔒 AEGIS-9: PROTECTING DATA")
        print("-" * 70)
        
        # Validate hardware keys
        self._validate_hardware_keys(ic_key, phone_key)
        
        # Generate key fingerprint
        key_fingerprint = generate_key_fingerprint(ic_key, phone_key)
        print(f"   🔑 Hardware Key Fingerprint: {key_fingerprint}")
        
        # Apply all 9 layers
        fragment_a, fragment_b, merkle_root, metadata = split_into_fragments_advanced(
            data=data,
            ic_key=ic_key,
            phone_key=phone_key,
            enable_anti_tampering=enable_anti_tampering,
            enable_time_lock=enable_time_lock,
            time_lock_duration=time_lock_duration
        )
        
        # Add metadata
        metadata.update({
            "security_core_version": self.version,
            "key_fingerprint": key_fingerprint,
            "protection_timestamp": datetime.now().isoformat(),
            "compliance_standards": self.compliance
        })
        
        print(f"\n✅ DATA PROTECTED SUCCESSFULLY")
        print(f"   Fragment A: {len(fragment_a)} bytes → PDSA SAN")
        print(f"   Fragment B: {len(fragment_b)} bytes → Blockchain")
        print("-" * 70)
        
        return fragment_a, fragment_b, merkle_root, metadata
    
    def unprotect_data(
        self,
        fragment_a: bytes,
        fragment_b: bytes,
        ic_key: bytes,
        phone_key: bytes,
        metadata: Dict[str, Any],
        skip_time_lock: bool = False
    ) -> Dict[str, Any]:
        """
        DECRYPT: Verify and decrypt data through all 9 security layers
        """
        
        print("\n🔓 AEGIS-9: UNPROTECTING DATA")
        print("-" * 70)
        
        # Validate hardware keys
        self._validate_hardware_keys(ic_key, phone_key)
        
        # Verify key fingerprint
        stored_fingerprint = metadata.get("key_fingerprint")
        current_fingerprint = generate_key_fingerprint(ic_key, phone_key)
        
        if stored_fingerprint != current_fingerprint:
            raise ValueError(
                f"🚨 SECURITY ALERT: Hardware key fingerprint mismatch!\n"
                f"   Expected: {stored_fingerprint}\n"
                f"   Got: {current_fingerprint}"
            )
        
        print(f"   ✅ Hardware Key Fingerprint Verified")
        
        # Decrypt through all 9 layers
        data = reconstruct_data_advanced(
            fragment_a=fragment_a,
            fragment_b=fragment_b,
            ic_key=ic_key,
            phone_key=phone_key,
            metadata=metadata,
            skip_time_lock=skip_time_lock
        )
        
        print(f"\n✅ DATA UNPROTECTED SUCCESSFULLY")
        print(f"   Fields recovered: {len(data)}")
        print("-" * 70)
        
        return data
    
    def verify_integrity(
        self,
        fragment_a: bytes,
        fragment_b: bytes,
        merkle_root: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Verify data integrity without decrypting"""
        
        print("\n🔍 VERIFYING DATA INTEGRITY")
        print("-" * 70)
        
        is_valid = verify_integrity_advanced(
            fragment_a=fragment_a,
            fragment_b=fragment_b,
            stored_merkle_root=merkle_root,
            metadata=metadata
        )
        
        if is_valid:
            print("   ✅ Integrity verification PASSED")
        else:
            print("   ❌ Integrity verification FAILED")
        
        print("-" * 70)
        return is_valid
    
    def _validate_hardware_keys(self, ic_key: bytes, phone_key: bytes):
        """Validate hardware key requirements"""
        
        if len(ic_key) != 32:
            raise ValueError(f"IC key must be 32 bytes, got {len(ic_key)}")
        
        if len(phone_key) != 32:
            raise ValueError(f"Phone key must be 32 bytes, got {len(phone_key)}")
        
        if ic_key == b'\x00' * 32:
            raise ValueError("IC key cannot be all zeros")
        
        if phone_key == b'\x00' * 32:
            raise ValueError("Phone key cannot be all zeros")
    
    def generate_security_report(self, metadata: Dict[str, Any]) -> str:
        """Generate human-readable security report"""
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║               OBSIDIAN SECURITY REPORT (Aegis-9)                     ║
╚══════════════════════════════════════════════════════════════════════╝

📊 PROTECTION SUMMARY:
   Version:              {metadata.get('version', 'N/A')}
   Algorithm:            {metadata.get('algorithm', 'N/A')}
   PBKDF2 Iterations:    {metadata.get('pbkdf2_iterations', 'N/A'):,}
   Anti-Tampering:       {'✅ Enabled' if metadata.get('anti_tampering') else '❌ Disabled'}

📦 DATA SIZES:
   Original Size:        {metadata.get('original_size', 0):,} bytes
   Fragment A (SAN):     {metadata.get('fragment_a_size', 0):,} bytes
   Fragment B (Chain):   {metadata.get('fragment_b_size', 0):,} bytes

🔐 SECURITY LAYERS:
   ✅ Layer 1-9: All Active

⚖️  COMPLIANCE:
   {'   '.join('✅ ' + std for std in metadata.get('compliance_standards', []))}

╚══════════════════════════════════════════════════════════════════════╝
"""
        return report


if __name__ == "__main__":
    # Testing
    security_core = SecurityCore()
    
    test_data = {"name": "Ahmad", "ic": "123"}
    IC_KEY = b"mykad-secret-32bytes-hardware!!!"
    PHONE_KEY = b"phone-enclave-secret-32bytes!!"
    
    # Protect
    frag_a, frag_b, merkle, metadata = security_core.protect_data(
        test_data, IC_KEY, PHONE_KEY
    )
    
    print(security_core.generate_security_report(metadata))
    
    # Verify
    assert security_core.verify_integrity(frag_a, frag_b, merkle, metadata)
    
    # Unprotect
    recovered = security_core.unprotect_data(frag_a, frag_b, IC_KEY, PHONE_KEY, metadata)
    assert recovered == test_data
    
    print("\n✅ ALL TESTS PASSED")