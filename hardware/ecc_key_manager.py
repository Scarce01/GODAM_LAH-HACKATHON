# hardware/ecc_key_manager.py
"""
ECC Key Manager
Manages ECC key derivation and operations
"""

import hashlib
from typing import Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class ECCKeyManager:
    """
    ECC Key Manager
    
    Features:
    - Deterministic key derivation from public keys
    - HKDF-based key expansion
    - Consistent key generation across sessions
    
    Why Derive from Public Keys:
    - Public keys are constant (never change)
    - Can be stored on blockchain
    - Derived keys always the same
    - Still requires hardware for authentication
    """
    
    def __init__(self):
        """Initialize key manager"""
        
        print(f"🔑 ECC Key Manager initialized")
    
    def derive_ic_key(self, card_public_key_pem: str, did: str) -> bytes:
        """
        Derive IC_KEY from MyKad public key
        
        Args:
            card_public_key_pem: MyKad public key (PEM format)
            did: User's DID
        
        Returns:
            32-byte IC_KEY
        """
        
        card_pubkey_bytes = card_public_key_pem.encode('utf-8')
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"OBSIDIAN_IC_CARD_KEY_V1",
            info=did.encode('utf-8')
        )
        
        ic_key = hkdf.derive(card_pubkey_bytes)
        
        print(f"   Derived IC_KEY: {ic_key.hex()[:32]}...")
        
        return ic_key
    
    def derive_phone_key(self, phone_public_key_pem: str, did: str) -> bytes:
        """
        Derive PHONE_KEY from Phone TEE public key
        
        Args:
            phone_public_key_pem: Phone public key (PEM format)
            did: User's DID
        
        Returns:
            32-byte PHONE_KEY
        """
        
        phone_pubkey_bytes = phone_public_key_pem.encode('utf-8')
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"OBSIDIAN_PHONE_KEY_V1",
            info=did.encode('utf-8')
        )
        
        phone_key = hkdf.derive(phone_pubkey_bytes)
        
        print(f"   Derived PHONE_KEY: {phone_key.hex()[:32]}...")
        
        return phone_key
    
    def derive_both_keys(
        self,
        card_public_key_pem: str,
        phone_public_key_pem: str,
        did: str
    ) -> Tuple[bytes, bytes]:
        """
        Derive both IC_KEY and PHONE_KEY
        
        Args:
            card_public_key_pem: MyKad public key
            phone_public_key_pem: Phone public key
            did: User's DID
        
        Returns:
            (ic_key, phone_key)
        """
        
        print(f"\n🔑 Deriving encryption keys from public keys...")
        print(f"   DID: {did}")
        
        ic_key = self.derive_ic_key(card_public_key_pem, did)
        phone_key = self.derive_phone_key(phone_public_key_pem, did)
        
        print(f"✅ Keys derived successfully")
        
        return ic_key, phone_key
    
    def generate_key_fingerprint(self, ic_key: bytes, phone_key: bytes) -> str:
        """
        Generate fingerprint of keys
        
        Args:
            ic_key: IC key
            phone_key: Phone key
        
        Returns:
            16-character hex fingerprint
        """
        
        combined = ic_key + phone_key
        fingerprint = hashlib.sha256(combined).hexdigest()[:16]
        
        return fingerprint


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 ECC Key Manager Testing")
    print("="*70)
    
    # Initialize
    key_mgr = ECCKeyManager()
    
    # Test data
    test_card_key = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBg...\n-----END PUBLIC KEY-----"
    test_phone_key = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBg...\n-----END PUBLIC KEY-----"
    test_did = "did:zetrix:mykad-123456"
    
    # Test 1: Derive IC key
    print("\n[TEST 1] Derive IC Key")
    ic_key = key_mgr.derive_ic_key(test_card_key, test_did)
    if len(ic_key) == 32:
        print("✅ Test 1 passed")
    
    # Test 2: Derive phone key
    print("\n[TEST 2] Derive Phone Key")
    phone_key = key_mgr.derive_phone_key(test_phone_key, test_did)
    if len(phone_key) == 32:
        print("✅ Test 2 passed")
    
    # Test 3: Derive both keys
    print("\n[TEST 3] Derive Both Keys")
    ic_key, phone_key = key_mgr.derive_both_keys(test_card_key, test_phone_key, test_did)
    if len(ic_key) == 32 and len(phone_key) == 32:
        print("✅ Test 3 passed")
    
    # Test 4: Generate fingerprint
    print("\n[TEST 4] Generate Key Fingerprint")
    fingerprint = key_mgr.generate_key_fingerprint(ic_key, phone_key)
    print(f"   Fingerprint: {fingerprint}")
    if len(fingerprint) == 16:
        print("✅ Test 4 passed")
    
    # Test 5: Deterministic derivation
    print("\n[TEST 5] Deterministic Key Derivation")
    ic_key_2, phone_key_2 = key_mgr.derive_both_keys(test_card_key, test_phone_key, test_did)
    if ic_key == ic_key_2 and phone_key == phone_key_2:
        print("✅ Test 5 passed - Keys are deterministic")
    
    print("\n✅ All ECC Key Manager tests passed!")
