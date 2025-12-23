# api/request_validator.py
"""
Request Validator
Validates and sanitizes API requests
"""

import re
from typing import Dict, Any, Tuple


class RequestValidator:
    """
    Request validation and sanitization
    
    Validates:
    - JSON schema compliance
    - Field types and formats
    - SQL injection prevention
    - XSS prevention
    """
    
    @staticmethod
    def validate_did(did: str) -> Tuple[bool, str]:
        """
        Validate DID format
        
        Args:
            did: Decentralized identifier
        
        Returns:
            (is_valid, error_message)
        """
        
        if not did:
            return False, "DID is required"
        
        # DID format: did:zetrix:mykad-{IC_NUMBER}
        pattern = r'^did:zetrix:mykad-[0-9]{12}$'
        
        if not re.match(pattern, did):
            return False, "Invalid DID format"
        
        return True, ""
    
    @staticmethod
    def validate_government_request(request_data: Dict) -> Tuple[bool, str]:
        """
        Validate government data access request
        
        Args:
            request_data: Request dictionary
        
        Returns:
            (is_valid, error_message)
        """
        
        # Required fields
        required_fields = [
            'target_user_id',
            'requesting_authority',
            'purpose',
            'data_sets_requested'
        ]
        
        for field in required_fields:
            if field not in request_data:
                return False, f"Missing required field: {field}"
        
        # Validate authority
        authority = request_data.get('requesting_authority', {})
        if 'agency_id' not in authority:
            return False, "Missing agency_id in requesting_authority"
        
        # Validate agency_id format
        agency_id = authority.get('agency_id')
        if not re.match(r'^GOV-[A-Z]+-\d{4}$', agency_id):
            return False, "Invalid agency_id format"
        
        return True, ""
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize text input
        
        Args:
            text: User input
        
        Returns:
            Sanitized text
        """
        
        # Remove potential SQL injection
        dangerous_patterns = [
            r"('|(--)|;|\/\*|\*\/|xp_|sp_)",
            r"(<script|<iframe|javascript:)"
        ]
        
        sanitized = text
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()


if __name__ == "__main__":
    validator = RequestValidator()
    
    # Test DID validation
    print("Testing DID validation:")
    test_dids = [
        ("did:zetrix:mykad-123456789012", True),
        ("did:zetrix:invalid", False),
        ("", False)
    ]
    
    for did, expected in test_dids:
        is_valid, msg = validator.validate_did(did)
        status = "✅" if is_valid == expected else "❌"
        print(f"  {status} {did or '(empty)'}")
    
    print("\n✅ Validator tests complete")
