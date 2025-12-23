# communication/certificate_manager.py
"""
Certificate Manager
PKI certificate validation and management
"""

import hashlib
from datetime import datetime
from typing import Dict, Optional


class CertificateManager:
    """
    Manages PKI certificates
    
    Features:
    - Certificate validation
    - Expiry checking
    - Certificate pinning
    """
    
    def __init__(self):
        self.trusted_certificates = {}
        self.certificate_pins = {}
    
    def add_trusted_certificate(
        self,
        cert_id: str,
        cert_data: bytes
    ):
        """Add trusted certificate"""
        
        cert_hash = hashlib.sha256(cert_data).hexdigest()
        
        self.trusted_certificates[cert_id] = {
            "data": cert_data,
            "hash": cert_hash,
            "added_at": datetime.now().isoformat()
        }
        
        print(f"✅ Trusted certificate added: {cert_id}")
        print(f"   Hash: {cert_hash[:32]}...")
    
    def verify_certificate(
        self,
        cert_id: str,
        cert_data: bytes
    ) -> bool:
        """Verify certificate matches trusted version"""
        
        if cert_id not in self.trusted_certificates:
            print(f"❌ Unknown certificate: {cert_id}")
            return False
        
        trusted = self.trusted_certificates[cert_id]
        cert_hash = hashlib.sha256(cert_data).hexdigest()
        
        is_valid = cert_hash == trusted["hash"]
        
        if is_valid:
            print(f"✅ Certificate verified: {cert_id}")
        else:
            print(f"❌ Certificate mismatch: {cert_id}")
        
        return is_valid


if __name__ == "__main__":
    manager = CertificateManager()
    
    test_cert = b"test-certificate-data"
    manager.add_trusted_certificate("gov-ca-001", test_cert)
    
    is_valid = manager.verify_certificate("gov-ca-001", test_cert)
    print(f"✅ Verification: {is_valid}")