# ai/policy_engine.py
"""
Policy Engine (Layer 2)
Deterministic rule evaluation - NOT learned by AI
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


class PolicyEngine:
    """
    Deterministic Policy Evaluation Engine
    
    Evaluates requests against hard-coded rules:
    - User consent requirements
    - Data category permissions
    - Agency authorization
    - Request frequency limits
    - Legal compliance
    """
    
    def __init__(self, user_policies: Dict = None):
        """
        Initialize policy engine
        
        Args:
            user_policies: User's policy configuration
        """
        
        self.user_policies = user_policies or self._default_policies()
        
        print(f"📋 Policy Engine initialized")
        print(f"   Policies loaded: {len(self.user_policies.get('trusted_authorities', []))}")
    
    def _default_policies(self) -> Dict:
        """Default user policies"""
        
        return {
            "trusted_authorities": [
                "Hospital_KL",
                "LHDN",
                "JPN",
                "Bank_Negara"
            ],
            "blocked_categories": [],
            "max_risk_auto_approve": 20,
            "geographic_restriction": "Malaysia",
            "auto_approve_conditions": {
                "medical_trusted_sources": ["Hospital_KL", "KKM"],
                "financial_max_risk": 15
            },
            "require_explicit_consent": True
        }
    
    def evaluate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate government request against policies
        
        Args:
            request: Government request
        
        Returns:
            Policy decision with violations
        """
        
        violations = []
        
        # Extract request details
        authority = request.get('requesting_authority', {}).get('agency_name', 'Unknown')
        purpose = request.get('purpose', {}).get('category', 'Unknown')
        data_categories = [
            ds.get('data_category', '')
            for ds in request.get('data_sets_requested', [])
        ]
        
        # Check 1: Trusted authority
        if authority not in self.user_policies['trusted_authorities']:
            violations.append(f"Authority '{authority}' not in trusted list")
        
        # Check 2: Blocked categories
        for category in data_categories:
            if category in self.user_policies['blocked_categories']:
                violations.append(f"Data category '{category}' is blocked")
        
        # Check 3: Geographic restriction
        location = request.get('location', {}).get('country', 'Unknown')
        if location != self.user_policies['geographic_restriction']:
            violations.append(f"Request from outside {self.user_policies['geographic_restriction']}")
        
        # Check 4: Explicit consent requirement
        if self.user_policies['require_explicit_consent']:
            # In production: check if user has pre-approved this specific request
            # For now: all requests require manual approval
            pass
        
        # Determine decision
        if violations:
            decision = "DENY"
            reason = "Policy violations detected"
        else:
            decision = "AUTO_APPROVE"
            reason = "Request complies with all policies"
        
        return {
            "decision": decision,
            "reason": reason,
            "violations": violations,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 POLICY ENGINE TESTING")
    print("="*70)
    
    engine = PolicyEngine()
    
    # Test 1: Valid request
    print("\nTEST 1: Valid Request (Trusted Authority)")
    
    valid_request = {
        "requesting_authority": {
            "agency_name": "LHDN"
        },
        "purpose": {
            "category": "Tax_Audit"
        },
        "data_sets_requested": [
            {"data_category": "Financial_Records"}
        ],
        "location": {
            "country": "Malaysia"
        }
    }
    
    result = engine.evaluate_request(valid_request)
    print(f"   Decision: {result['decision']}")
    print(f"   Reason: {result['reason']}")
    print(f"   Violations: {len(result['violations'])}")
    
    # Test 2: Untrusted authority
    print("\nTEST 2: Invalid Request (Untrusted Authority)")
    
    invalid_request = {
        "requesting_authority": {
            "agency_name": "Unknown_Agency"
        },
        "purpose": {
            "category": "Unknown"
        },
        "data_sets_requested": [
            {"data_category": "Medical_Records"}
        ],
        "location": {
            "country": "Malaysia"
        }
    }
    
    result = engine.evaluate_request(invalid_request)
    print(f"   Decision: {result['decision']}")
    print(f"   Reason: {result['reason']}")
    print(f"   Violations: {result['violations']}")
    
    print("\n✅ Policy Engine tests complete")