# policy/schema_validator.py
"""
Schema Validator
JSON schema validation for requests and policies
"""

import json
from typing import Dict, Any, Tuple


class SchemaValidator:
    """
    JSON Schema Validator
    
    Validates:
    - Government request schema
    - Policy schema
    - Consent schema
    """
    
    def __init__(self):
        """Initialize schema validator"""
        
        self.request_schema = self._load_request_schema()
        self.policy_schema = self._load_policy_schema()
        
        print(f"📋 Schema Validator initialized")
    
    def _load_request_schema(self) -> Dict:
        """Load government request schema"""
        
        return {
            "type": "object",
            "required": [
                "request_id",
                "target_user_id",
                "requesting_authority",
                "purpose",
                "data_sets_requested"
            ],
            "properties": {
                "request_id": {"type": "string"},
                "target_user_id": {"type": "string"},
                "requesting_authority": {
                    "type": "object",
                    "required": ["agency_id", "agency_name"],
                    "properties": {
                        "agency_id": {"type": "string"},
                        "agency_name": {"type": "string"},
                        "officer_id": {"type": "string"}
                    }
                },
                "purpose": {
                    "type": "object",
                    "required": ["category"],
                    "properties": {
                        "category": {"type": "string"}
                    }
                },
                "data_sets_requested": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["data_category", "fields"],
                        "properties": {
                            "data_category": {"type": "string"},
                            "fields": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    
    def _load_policy_schema(self) -> Dict:
        """Load policy schema"""
        
        return {
            "type": "object",
            "required": [
                "user_id",
                "agency_id",
                "purpose",
                "allowed_data_categories"
            ]
        }
    
    def validate_request(self, request: Dict) -> Tuple[bool, str]:
        """
        Validate government request
        
        Args:
            request: Request dictionary
        
        Returns:
            (is_valid, error_message)
        """
        
        # Check required fields
        for field in self.request_schema["required"]:
            if field not in request:
                return False, f"Missing required field: {field}"
        
        # Validate requesting_authority
        authority = request.get("requesting_authority", {})
        for field in ["agency_id", "agency_name"]:
            if field not in authority:
                return False, f"Missing field in requesting_authority: {field}"
        
        # Validate purpose
        purpose = request.get("purpose", {})
        if "category" not in purpose:
            return False, "Missing purpose.category"
        
        # Validate data_sets_requested
        data_sets = request.get("data_sets_requested", [])
        if not isinstance(data_sets, list) or len(data_sets) == 0:
            return False, "data_sets_requested must be non-empty array"
        
        for i, data_set in enumerate(data_sets):
            if "data_category" not in data_set:
                return False, f"Missing data_category in data_sets_requested[{i}]"
            if "fields" not in data_set:
                return False, f"Missing fields in data_sets_requested[{i}]"
        
        return True, "Valid"
    
    def validate_policy(self, policy: Dict) -> Tuple[bool, str]:
        """
        Validate policy
        
        Args:
            policy: Policy dictionary
        
        Returns:
            (is_valid, error_message)
        """
        
        for field in self.policy_schema["required"]:
            if field not in policy:
                return False, f"Missing required field: {field}"
        
        return True, "Valid"


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 SCHEMA VALIDATOR TESTING")
    print("="*70)
    
    validator = SchemaValidator()
    
    # Test 1: Valid request
    print("\nTEST 1: Valid Request")
    
    valid_request = {
        "request_id": "REQ-001",
        "target_user_id": "900101-01-1234",
        "requesting_authority": {
            "agency_id": "GOV-IRB-0002",
            "agency_name": "LHDN"
        },
        "purpose": {
            "category": "Tax_Audit"
        },
        "data_sets_requested": [
            {
                "data_category": "Financial_Records",
                "fields": ["account_balance"]
            }
        ]
    }
    
    is_valid, msg = validator.validate_request(valid_request)
    print(f"   {'✅' if is_valid else '❌'} {msg}")
    
    # Test 2: Invalid request (missing fields)
    print("\nTEST 2: Invalid Request (Missing Fields)")
    
    invalid_request = {
        "request_id": "REQ-002"
        # Missing other fields
    }
    
    is_valid, msg = validator.validate_request(invalid_request)
    print(f"   {'✅' if is_valid else '❌'} {msg}")
    
    # Test 3: Valid policy
    print("\nTEST 3: Valid Policy")
    
    valid_policy = {
        "user_id": "900101-01-1234",
        "agency_id": "GOV-IRB-0002",
        "purpose": "Tax_Audit",
        "allowed_data_categories": ["Financial_Records"]
    }
    
    is_valid, msg = validator.validate_policy(valid_policy)
    print(f"   {'✅' if is_valid else '❌'} {msg}")
    
    print("\n✅ Schema Validator tests complete")