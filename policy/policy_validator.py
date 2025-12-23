# policy/policy_validator.py
"""
Policy Validator
Validates policies and requests against policy rules
"""

import re
from typing import Dict, Any, Tuple, List
from datetime import datetime


class PolicyValidator:
    """
    Policy Validation Engine
    
    Validates:
    - Policy structure and format
    - Request-policy matching
    - Data authorization
    - Time validity
    """
    
    def __init__(self):
        """Initialize validator"""
        
        self.valid_purposes = [
            "Tax_Audit",
            "Identity_Verification",
            "Healthcare_Emergency",
            "Medical_Treatment",
            "License_Renewal",
            "Criminal_Investigation"
        ]
        
        self.valid_data_categories = [
            "Personal_Identity",
            "Medical_Records",
            "Financial_Records",
            "Employment_Records",
            "Address_History",
            "Education_Records",
            "Vehicle_Registration"
        ]
        
        print(f"✅ Policy Validator initialized")
        print(f"   Valid purposes: {len(self.valid_purposes)}")
        print(f"   Valid categories: {len(self.valid_data_categories)}")
    
    def validate_policy_structure(self, policy: Dict) -> Tuple[bool, List[str]]:
        """
        Validate policy structure
        
        Args:
            policy: Policy dictionary
        
        Returns:
            (is_valid, error_messages)
        """
        
        errors = []
        
        # Required fields
        required_fields = [
            "user_id",
            "agency_id",
            "agency_name",
            "purpose",
            "allowed_data_categories",
            "allowed_fields",
            "valid_from",
            "valid_until",
            "max_requests_per_year"
        ]
        
        for field in required_fields:
            if field not in policy:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate purpose
        if policy.get("purpose") not in self.valid_purposes:
            errors.append(f"Invalid purpose: {policy.get('purpose')}")
        
        # Validate data categories
        for category in policy.get("allowed_data_categories", []):
            if category not in self.valid_data_categories:
                errors.append(f"Invalid data category: {category}")
        
        # Validate dates
        try:
            valid_from = datetime.fromisoformat(policy["valid_from"].replace('Z', '+00:00'))
            valid_until = datetime.fromisoformat(policy["valid_until"].replace('Z', '+00:00'))
            
            if valid_until <= valid_from:
                errors.append("valid_until must be after valid_from")
        except Exception as e:
            errors.append(f"Invalid date format: {e}")
        
        # Validate max requests
        max_requests = policy.get("max_requests_per_year", 0)
        if not isinstance(max_requests, int) or max_requests < 1:
            errors.append("max_requests_per_year must be positive integer")
        
        return len(errors) == 0, errors
    
    def validate_agency_id(self, agency_id: str) -> Tuple[bool, str]:
        """
        Validate agency ID format
        
        Args:
            agency_id: Agency identifier
        
        Returns:
            (is_valid, error_message)
        """
        
        # Format: GOV-XXX-0000
        pattern = r'^GOV-[A-Z]+-\d{4}$'
        
        if not re.match(pattern, agency_id):
            return False, f"Invalid agency_id format. Expected: GOV-XXX-0000"
        
        return True, ""
    
    def validate_user_id(self, user_id: str) -> Tuple[bool, str]:
        """
        Validate user IC number format
        
        Args:
            user_id: User IC number
        
        Returns:
            (is_valid, error_message)
        """
        
        # Format: YYMMDD-PP-SSSS
        pattern = r'^\d{6}-\d{2}-\d{4}$'
        
        if not re.match(pattern, user_id):
            return False, "Invalid IC number format. Expected: YYMMDD-PP-SSSS"
        
        return True, ""
    
    def check_field_authorization(
        self,
        requested_field: str,
        category: str,
        allowed_fields: Dict[str, List[str]]
    ) -> bool:
        """
        Check if specific field is authorized
        
        Args:
            requested_field: Field name
            category: Data category
            allowed_fields: Allowed fields by category
        
        Returns:
            True if authorized
        """
        
        allowed_for_category = allowed_fields.get(category, [])
        return requested_field in allowed_for_category


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 POLICY VALIDATOR TESTING")
    print("="*70)
    
    validator = PolicyValidator()
    
    # Test 1: Valid policy
    print("\nTEST 1: Valid Policy Structure")
    
    valid_policy = {
        "user_id": "900101-01-1234",
        "agency_id": "GOV-IRB-0002",
        "agency_name": "LHDN",
        "purpose": "Tax_Audit",
        "allowed_data_categories": ["Financial_Records"],
        "allowed_fields": {
            "Financial_Records": ["account_balance"]
        },
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_until": "2025-12-31T23:59:59Z",
        "max_requests_per_year": 2
    }
    
    is_valid, errors = validator.validate_policy_structure(valid_policy)
    
    if is_valid:
        print(f"   ✅ Policy is valid")
    else:
        print(f"   ❌ Policy has errors:")
        for error in errors:
            print(f"      - {error}")
    
    # Test 2: Invalid policy (missing fields)
    print("\nTEST 2: Invalid Policy (Missing Fields)")
    
    invalid_policy = {
        "user_id": "900101-01-1234",
        "agency_id": "GOV-IRB-0002"
        # Missing other required fields
    }
    
    is_valid, errors = validator.validate_policy_structure(invalid_policy)
    
    print(f"   Expected errors: {len(errors)}")
    for error in errors[:3]:  # Show first 3
        print(f"      - {error}")
    
    # Test 3: Agency ID validation
    print("\nTEST 3: Agency ID Validation")
    
    test_agencies = [
        ("GOV-IRB-0002", True),
        ("GOV-KKM-0001", True),
        ("INVALID-123", False),
        ("", False)
    ]
    
    for agency_id, expected in test_agencies:
        is_valid, msg = validator.validate_agency_id(agency_id)
        status = "✅" if is_valid == expected else "❌"
        print(f"   {status} {agency_id or '(empty)'}: {is_valid}")
    
    # Test 4: Field authorization
    print("\nTEST 4: Field Authorization Check")
    
    allowed_fields = {
        "Financial_Records": ["account_balance", "tax_id"],
        "Medical_Records": ["blood_type"]
    }
    
    test_cases = [
        ("account_balance", "Financial_Records", True),
        ("tax_id", "Financial_Records", True),
        ("medical_history", "Financial_Records", False),
        ("blood_type", "Medical_Records", True)
    ]
    
    for field, category, expected in test_cases:
        is_authorized = validator.check_field_authorization(field, category, allowed_fields)
        status = "✅" if is_authorized == expected else "❌"
        print(f"   {status} {field} in {category}: {is_authorized}")
    
    print("\n✅ Policy Validator tests complete")