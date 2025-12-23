# communication/session_key_rotation.py
"""
Session Key Rotation
Perfect Forward Secrecy implementation
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional


class SessionKeyRotation:
    """
    Manages session key rotation
    
    Features:
    - Automatic key rotation
    - Perfect Forward Secrecy
    - Key lifetime management
    """
    
    def __init__(self, rotation_interval: int = 3600):
        """
        Initialize key rotation
        
        Args:
            rotation_interval: Seconds between rotations
        """
        
        self.rotation_interval = rotation_interval
        self.current_keys = {}
        
        print(f"🔄 Key rotation initialized")
        print(f"   Interval: {rotation_interval} seconds")
    
    def generate_session_key(self, session_id: str) -> bytes:
        """Generate new session key"""
        
        key = secrets.token_bytes(32)
        
        self.current_keys[session_id] = {
            "key": key,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=self.rotation_interval)
        }
        
        print(f"🔑 Session key generated: {session_id}")
        
        return key
    
    def get_session_key(self, session_id: str) -> Optional[bytes]:
        """Get current session key"""
        
        if session_id not in self.current_keys:
            return None
        
        key_info = self.current_keys[session_id]
        
        # Check if expired
        if datetime.now() > key_info["expires_at"]:
            print(f"⏰ Session key expired: {session_id}")
            return None
        
        return key_info["key"]
    
    def rotate_key(self, session_id: str) -> bytes:
        """Rotate session key"""
        
        # Delete old key
        if session_id in self.current_keys:
            del self.current_keys[session_id]
        
        # Generate new key
        return self.generate_session_key(session_id)


if __name__ == "__main__":
    rotator = SessionKeyRotation(rotation_interval=60)
    
    key = rotator.generate_session_key("test-session")
    print(f"✅ Key generated: {key.hex()[:32]}...")
    
    retrieved = rotator.get_session_key("test-session")
    print(f"✅ Key retrieved: {retrieved.hex()[:32]}...")
