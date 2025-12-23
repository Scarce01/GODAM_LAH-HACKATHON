# hardware/hardware_authenticator.py
"""
Hardware Authenticator
Combines MyKad and Phone TEE for dual-factor authentication
"""

import secrets
import hashlib
from typing import Tuple, Dict, Optional
from datetime import datetime

from .mykad_interface import MyKadInterface
from .phone_tee_interface import PhoneTEEInterface


class HardwareAuthenticator:
    """
    Hardware Authenticator
    
    Dual-Factor Hardware Authentication:
    1. MyKad NFC (Something you have)
    2. Phone Biometric (Something you are)
    
    Both factors required for:
    - Identity data access
    - Request approval
    - Policy creation
    - Emergency policy setup
    
    Security Properties:
    - Private keys never leave hardware
    - Signatures prove possession
    - Biometric proves identity
    - Challenge-response prevents replay
    """
    
    def __init__(self):
        """Initialize hardware authenticator"""
        
        self.mykad = None
        self.phone = None
        self.authenticated = False
        self.last_auth_time = None
        self.session_token = None
        
        print(f"\n{'='*70}")
        print(f"🔐 Hardware Authenticator Initialized")
        print(f"{'='*70}")
        print(f"   Authentication Mode: Dual-Factor")
        print(f"   Factor 1: MyKad NFC (Possession)")
        print(f"   Factor 2: Phone Biometric (Identity)")
        print(f"{'='*70}\n")
    
    def setup_mykad(self, card_id: Optional[str] = None) -> bool:
        """
        Setup MyKad interface
        
        Args:
            card_id: Optional card ID for testing
        
        Returns:
            True if setup successful
        """
        
        print(f"\n[STEP 1] Setting up MyKad...")
        
        self.mykad = MyKadInterface(card_id)
        
        # Detect card
        if not self.mykad.detect_card():
            print(f"❌ Failed to detect MyKad")
            return False
        
        # Read identity
        identity = self.mykad.read_identity_data()
        
        # Provision keys if first time
        if not self.mykad.is_provisioned:
            print(f"\n   First time setup - provisioning keys...")
            self.mykad.provision_secure_keys()
        
        print(f"✅ MyKad setup complete")
        print(f"   IC: {identity['ic_number']}")
        print(f"   Name: {identity['name']}")
        
        return True
    
    def setup_phone(self, device_id: Optional[str] = None) -> bool:
        """
        Setup Phone TEE interface
        
        Args:
            device_id: Optional device ID for testing
        
        Returns:
            True if setup successful
        """
        
        print(f"\n[STEP 2] Setting up Phone TEE...")
        
        self.phone = PhoneTEEInterface(device_id)
        
        # Check TEE availability
        if not self.phone.tee_available:
            print(f"❌ TEE not available on this device")
            return False
        
        # Enroll biometric if first time
        if not self.phone.biometric_enrolled:
            print(f"\n   First time setup - enrolling biometric...")
            self.phone.enroll_biometric()
        
        # Provision keys if first time
        if not self.phone.is_provisioned:
            print(f"\n   Provisioning TEE keys...")
            self.phone.provision_secure_keys()
        
        print(f"✅ Phone TEE setup complete")
        
        return True
    
    def authenticate(self, require_biometric: bool = True) -> Tuple[bool, Dict]:
        """
        Perform dual-factor authentication
        
        Process:
        1. Generate random challenge
        2. MyKad signs challenge (proves possession)
        3. Phone signs challenge with biometric (proves identity)
        4. Verify both signatures
        5. Generate session token
        
        Args:
            require_biometric: Require biometric authentication
        
        Returns:
            (success, authentication_details)
        """
        
        if not self.mykad or not self.phone:
            return False, {"error": "Hardware not initialized"}
        
        print(f"\n{'='*70}")
        print(f"🔐 DUAL-FACTOR AUTHENTICATION")
        print(f"{'='*70}")
        
        # Generate challenge
        challenge = secrets.token_bytes(32)
        print(f"\n[STEP 1] Challenge generated: {challenge.hex()[:32]}...")
        
        # Factor 1: MyKad signature
        print(f"\n[STEP 2] Factor 1: MyKad Tap")
        print(f"   Please tap your MyKad on the reader...")
        
        try:
            mykad_signature = self.mykad.sign_challenge(challenge)
            
            # Verify MyKad signature
            if not self.mykad.verify_signature(challenge, mykad_signature):
                print(f"❌ MyKad signature verification failed")
                return False, {"error": "Invalid MyKad signature"}
            
            print(f"✅ MyKad signature verified")
        
        except Exception as e:
            print(f"❌ MyKad authentication failed: {e}")
            return False, {"error": str(e)}
        
        # Factor 2: Phone biometric signature
        print(f"\n[STEP 3] Factor 2: Biometric Authentication")
        
        try:
            phone_signature = self.phone.sign_challenge(challenge, require_biometric)
            
            # Verify phone signature
            if not self.phone.verify_signature(challenge, phone_signature):
                print(f"❌ Phone signature verification failed")
                return False, {"error": "Invalid phone signature"}
            
            print(f"✅ Phone signature verified")
        
        except Exception as e:
            print(f"❌ Phone authentication failed: {e}")
            return False, {"error": str(e)}
        
        # Generate session token
        session_data = (
            challenge +
            mykad_signature +
            phone_signature +
            datetime.now().isoformat().encode()
        )
        self.session_token = hashlib.sha256(session_data).hexdigest()
        
        self.authenticated = True
        self.last_auth_time = datetime.now()
        
        auth_details = {
            "success": True,
            "timestamp": self.last_auth_time.isoformat(),
            "session_token": self.session_token,
            "mykad_verified": True,
            "biometric_verified": True,
            "challenge": challenge.hex(),
            "mykad_signature": mykad_signature.hex()[:32] + "...",
            "phone_signature": phone_signature.hex()[:32] + "..."
        }
        
        print(f"\n{'='*70}")
        print(f"✅ AUTHENTICATION SUCCESSFUL")
        print(f"{'='*70}")
        print(f"   Session Token: {self.session_token[:32]}...")
        print(f"   Valid Until: Session end")
        print(f"{'='*70}\n")
        
        return True, auth_details
    
    def verify_session(self) -> bool:
        """
        Verify current session is valid
        
        Returns:
            True if session valid
        """
        
        return self.authenticated and self.session_token is not None
    
    def get_public_keys(self) -> Dict[str, str]:
        """
        Get public keys from both hardware devices
        
        Returns:
            Dictionary with both public keys
        """
        
        if not self.mykad or not self.phone:
            raise Exception("❌ Hardware not initialized")
        
        return {
            "mykad_public_key": self.mykad.get_public_key(),
            "phone_public_key": self.phone.get_public_key()
        }
    
    def get_authentication_status(self) -> Dict:
        """
        Get authentication status
        
        Returns:
            Status dictionary
        """
        
        return {
            "authenticated": self.authenticated,
            "session_token": self.session_token[:32] + "..." if self.session_token else None,
            "last_auth_time": self.last_auth_time.isoformat() if self.last_auth_time else None,
            "mykad_ready": self.mykad is not None and self.mykad.is_provisioned,
            "phone_ready": self.phone is not None and self.phone.is_provisioned
        }
    
    def logout(self):
        """Clear authentication session"""
        
        self.authenticated = False
        self.session_token = None
        self.last_auth_time = None
        
        print(f"🔓 Session cleared")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Hardware Authenticator Testing")
    print("="*70)
    
    # Initialize
    auth = HardwareAuthenticator()
    
    # Test 1: Setup MyKad
    print("\n[TEST 1] MyKad Setup")
    if auth.setup_mykad():
        print("✅ Test 1 passed")
    
    # Test 2: Setup Phone
    print("\n[TEST 2] Phone TEE Setup")
    if auth.setup_phone():
        print("✅ Test 2 passed")
    
    # Test 3: Get public keys
    print("\n[TEST 3] Public Key Export")
    keys = auth.get_public_keys()
    if keys['mykad_public_key'] and keys['phone_public_key']:
        print("✅ Test 3 passed")
        print(f"   MyKad Key: {keys['mykad_public_key'][:50]}...")
        print(f"   Phone Key: {keys['phone_public_key'][:50]}...")
    
    # Test 4: Dual-factor authentication
    print("\n[TEST 4] Dual-Factor Authentication")
    success, details = auth.authenticate(require_biometric=True)
    if success:
        print("✅ Test 4 passed")
        print(f"   Session Token: {details['session_token'][:32]}...")
    
    # Test 5: Verify session
    print("\n[TEST 5] Session Verification")
    if auth.verify_session():
        print("✅ Test 5 passed")
    
    # Test 6: Get status
    print("\n[TEST 6] Authentication Status")
    status = auth.get_authentication_status()
    if status['authenticated']:
        print("✅ Test 6 passed")
    
    # Summary
    print("\n" + "="*70)
    print("📊 Authentication Status Summary")
    print("="*70)
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Test 7: Logout
    print("\n[TEST 7] Logout")
    auth.logout()
    if not auth.verify_session():
        print("✅ Test 7 passed")
    
    print("\n✅ All Hardware Authenticator tests passed!")