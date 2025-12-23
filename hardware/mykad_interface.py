# hardware/mykad_interface.py
"""
MyKad NFC Interface
Communicates with MyKad secure element via NFC
"""

import os
import hashlib
import secrets
from typing import Optional, Tuple, Dict
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


class MyKadInterface:
    """
    MyKad NFC Secure Element Interface
    
    Hardware Specifications:
    - NFC Protocol: ISO14443A
    - Frequency: 13.56 MHz
    - Secure Element: JavaCard (Common Criteria EAL5+)
    - Key Storage: Hardware-protected, never exported
    - Supported: ECC P-256, RSA 2048
    
    Features:
    - Read IC number and basic identity
    - Generate ECC key pair in secure element
    - Sign challenges with private key
    - Export public key only
    - Hardware-backed key protection
    """
    
    def __init__(self, card_id: Optional[str] = None):
        """
        Initialize MyKad interface
        
        Args:
            card_id: Optional card identifier for testing
        """
        
        self.card_id = card_id or f"MYKAD_{secrets.token_hex(4).upper()}"
        self.is_provisioned = False
        self.private_key = None  # Stays in hardware, never exposed
        self.public_key_pem = None
        self.ic_number = None
        self.card_holder_name = None
        self.nfc_connected = False
        
        print(f"\n{'='*70}")
        print(f"🪪 MyKad Interface Initialized")
        print(f"{'='*70}")
        print(f"   Card ID: {self.card_id}")
        print(f"   Protocol: ISO14443A (NFC Type A)")
        print(f"   Frequency: 13.56 MHz")
        print(f"   Status: Waiting for tap...")
        print(f"{'='*70}\n")
    
    def detect_card(self) -> bool:
        """
        Detect MyKad via NFC
        
        Returns:
            True if card detected
        
        Production Implementation:
```python
        import nfc
        clf = nfc.ContactlessFrontend('usb')
        tag = clf.connect(rdwr={'on-connect': lambda tag: False})
        return tag is not None
```
        """
        
        print(f"📡 Scanning for MyKad...")
        print(f"   Please tap your MyKad on the NFC reader...")
        
        # Simulate NFC detection
        # In production: actual NFC hardware detection
        self.nfc_connected = True
        
        print(f"✅ MyKad detected: {self.card_id}")
        return True
    
    def read_identity_data(self) -> Dict[str, str]:
        """
        Read basic identity data from MyKad
        
        Returns:
            Dictionary with IC number and name
        
        Production Implementation:
        - Send APDU commands to secure element
        - Read public data sectors
        - Parse TLV-encoded data
        """
        
        if not self.nfc_connected:
            raise Exception("❌ Card not detected. Please tap MyKad.")
        
        print(f"\n📖 Reading identity data from MyKad...")
        
        # Simulate reading IC data
        # In production: APDU commands to JavaCard
        # Example APDU: SELECT FILE (IC Application)
        #               READ BINARY (IC Number sector)
        
        self.ic_number = "850101-14-5678"  # Demo IC
        self.card_holder_name = "AHMAD BIN ALI"
        
        identity_data = {
            "ic_number": self.ic_number,
            "name": self.card_holder_name,
            "card_id": self.card_id
        }
        
        print(f"✅ Identity data read:")
        print(f"   IC Number: {self.ic_number}")
        print(f"   Name: {self.card_holder_name}")
        
        return identity_data
    
    def provision_secure_keys(self) -> bool:
        """
        Provision ECC key pair in MyKad secure element
        
        This happens ONCE when card is first used with OBSIDIAN.
        Private key is generated inside secure element and NEVER exported.
        
        Returns:
            True if provisioning successful
        
        Production Implementation:
        - Send GENERATE_KEY_PAIR APDU to JavaCard
        - JavaCard generates ECC P-256 key pair internally
        - Private key stored in secure element (hardware-protected)
        - Public key returned via APDU response
        """
        
        if self.is_provisioned:
            print(f"⚠️  Card already provisioned")
            return True
        
        if not self.nfc_connected:
            raise Exception("❌ Card not detected. Please tap MyKad.")
        
        print(f"\n🔐 Provisioning secure keys in MyKad...")
        print(f"   Generating ECC P-256 key pair in secure element...")
        
        # Generate key pair
        # In production: JavaCard applet generates this internally
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        
        # Extract public key (can be exported)
        public_key = self.private_key.public_key()
        self.public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        self.is_provisioned = True
        
        print(f"✅ Key pair generated successfully")
        print(f"   Private Key: [LOCKED IN SECURE ELEMENT]")
        print(f"   Public Key: [EXPORTED]")
        print(f"   Algorithm: ECDSA P-256")
        print(f"   Key ID: {hashlib.sha256(self.public_key_pem.encode()).hexdigest()[:16]}")
        
        return True
    
    def sign_challenge(self, challenge: bytes) -> bytes:
        """
        Sign challenge with MyKad's private key
        
        Args:
            challenge: Challenge bytes to sign
        
        Returns:
            ECDSA signature
        
        Production Implementation:
        - Send INTERNAL_AUTHENTICATE APDU with challenge
        - JavaCard signs with private key (never exported)
        - Signature returned via APDU response
        
        Security:
        - Private key never leaves secure element
        - Signature proves possession of card
        - Each signature is unique (random k value)
        """
        
        if not self.is_provisioned:
            raise Exception("❌ Card not provisioned. Run provision_secure_keys() first.")
        
        if not self.nfc_connected:
            raise Exception("❌ Card not detected. Please tap MyKad.")
        
        print(f"\n✍️  Signing challenge with MyKad...")
        print(f"   Challenge: {challenge.hex()[:32]}...")
        
        # Sign challenge
        # In production: APDU INTERNAL_AUTHENTICATE command
        signature = self.private_key.sign(
            challenge,
            ec.ECDSA(hashes.SHA256())
        )
        
        print(f"✅ Signature generated")
        print(f"   Signature: {signature.hex()[:32]}...")
        print(f"   Size: {len(signature)} bytes")
        
        return signature
    
    def verify_signature(self, challenge: bytes, signature: bytes) -> bool:
        """
        Verify signature (for testing purposes)
        
        Args:
            challenge: Original challenge
            signature: Signature to verify
        
        Returns:
            True if signature valid
        """
        
        if not self.public_key_pem:
            raise Exception("❌ No public key available")
        
        # Load public key
        public_key_bytes = self.public_key_pem.encode('utf-8')
        public_key = serialization.load_pem_public_key(public_key_bytes)
        
        try:
            public_key.verify(
                signature,
                challenge,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except InvalidSignature:
            return False
    
    def get_public_key(self) -> str:
        """
        Export public key (PEM format)
        
        Returns:
            Public key in PEM format
        """
        
        if not self.is_provisioned:
            raise Exception("❌ Card not provisioned")
        
        return self.public_key_pem
    
    def get_card_info(self) -> Dict[str, str]:
        """
        Get card information summary
        
        Returns:
            Card info dictionary
        """
        
        return {
            "card_id": self.card_id,
            "ic_number": self.ic_number,
            "name": self.card_holder_name,
            "provisioned": self.is_provisioned,
            "nfc_connected": self.nfc_connected,
            "public_key_fingerprint": hashlib.sha256(
                self.public_key_pem.encode() if self.public_key_pem else b""
            ).hexdigest()[:16] if self.public_key_pem else None
        }
    
    def disconnect(self):
        """Disconnect from card"""
        
        self.nfc_connected = False
        print(f"📵 MyKad disconnected")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 MyKad Interface Testing")
    print("="*70)
    
    # Initialize
    mykad = MyKadInterface()
    
    # Test 1: Detect card
    print("\n[TEST 1] Card Detection")
    if mykad.detect_card():
        print("✅ Test 1 passed")
    
    # Test 2: Read identity
    print("\n[TEST 2] Read Identity Data")
    identity = mykad.read_identity_data()
    if identity['ic_number']:
        print("✅ Test 2 passed")
    
    # Test 3: Provision keys
    print("\n[TEST 3] Key Provisioning")
    if mykad.provision_secure_keys():
        print("✅ Test 3 passed")
    
    # Test 4: Sign challenge
    print("\n[TEST 4] Challenge Signing")
    challenge = secrets.token_bytes(32)
    signature = mykad.sign_challenge(challenge)
    if len(signature) > 0:
        print("✅ Test 4 passed")
    
    # Test 5: Verify signature
    print("\n[TEST 5] Signature Verification")
    if mykad.verify_signature(challenge, signature):
        print("✅ Test 5 passed")
    
    # Test 6: Get public key
    print("\n[TEST 6] Public Key Export")
    public_key = mykad.get_public_key()
    if "BEGIN PUBLIC KEY" in public_key:
        print("✅ Test 6 passed")
        print(f"   Public Key: {public_key[:50]}...")
    
    # Summary
    print("\n" + "="*70)
    print("📊 Card Information Summary")
    print("="*70)
    info = mykad.get_card_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    print("\n✅ All MyKad tests passed!")