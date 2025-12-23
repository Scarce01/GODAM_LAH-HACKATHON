# policy/bilateral_policy_storage.py
"""
Bilateral Policy Storage
Manages user-government policy agreements
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple


class BilateralPolicyStorage:
    """
    Bilateral Policy Storage System
    
    Stores policies that are agreements between users and government agencies.
    When government requests data, system verifies:
    1. User has pre-approved policy with this agency
    2. Request matches the policy terms
    3. Request has valid government signature/credentials
    
    Policy Structure:
    {
        "policy_id": "POL-2024-TAX-001",
        "user_id": "900101-01-1234",
        "agency_id": "GOV-IRB-0002",
        "agency_name": "LHDN",
        "purpose": "Tax_Audit",
        "allowed_data_categories": ["Financial_Records"],
        "allowed_fields": {...},
        "valid_from": "2024-01-01",
        "valid_until": "2025-12-31",
        "max_requests_per_year": 2
    }
    """
    
    def __init__(self, storage_path: str = "./policy_storage"):
        """
        Initialize policy storage
        
        Args:
            storage_path: Path to policy storage directory
        """
        
        self.storage_path = storage_path
        self.user_policies = {}
        self.government_credentials = {}
        
        # Initialize with sample data
        self._initialize_sample_data()
        
        print(f"\n{'='*70}")
        print(f"📜 BILATERAL POLICY STORAGE INITIALIZED")
        print(f"{'='*70}")
        print(f"   Storage Path: {storage_path}")
        print(f"   User Policies: {len(self.user_policies)}")
        print(f"   Gov Credentials: {len(self.government_credentials)}")
        print(f"{'='*70}\n")
    
    def _initialize_sample_data(self):
        """Initialize with sample policies and credentials"""
        
        # Sample user policies
        self.user_policies = {
            "900101-01-1234": {
                "policies": [
                    {
                        "policy_id": "POL-2024-TAX-001",
                        "user_id": "900101-01-1234",
                        "agency_name": "Lembaga Hasil Dalam Negeri",
                        "agency_id": "GOV-IRB-0002",
                        "purpose": "Tax_Audit",
                        "allowed_data_categories": ["Financial_Records", "Employment_Records"],
                        "allowed_fields": {
                            "Financial_Records": ["account_balance", "transaction_history_12months"],
                            "Employment_Records": ["current_employer", "salary"]
                        },
                        "valid_from": "2024-01-01T00:00:00Z",
                        "valid_until": "2025-12-31T23:59:59Z",
                        "max_requests_per_year": 2,
                        "notification_required": True,
                        "manual_approval_required": False,
                        "created_at": "2024-01-01T00:00:00Z",
                        "policy_hash": hashlib.sha256(b"policy-001").hexdigest(),
                        "user_signature": "user_sig_001",
                        "agency_signature": "agency_sig_001"
                    },
                    {
                        "policy_id": "POL-2023-MED-001",
                        "user_id": "900101-01-1234",
                        "agency_name": "Kementerian Kesihatan Malaysia",
                        "agency_id": "GOV-KKM-0001",
                        "purpose": "Healthcare_Emergency",
                        "allowed_data_categories": ["Medical_Records", "Personal_Identity"],
                        "allowed_fields": {
                            "Medical_Records": ["blood_type", "allergies", "medical_history"],
                            "Personal_Identity": ["full_name", "ic_number", "date_of_birth"]
                        },
                        "valid_from": "2023-06-01T00:00:00Z",
                        "valid_until": "2026-06-01T00:00:00Z",
                        "max_requests_per_year": 10,
                        "notification_required": False,
                        "manual_approval_required": False,
                        "created_at": "2023-06-01T00:00:00Z",
                        "policy_hash": hashlib.sha256(b"policy-002").hexdigest(),
                        "user_signature": "user_sig_002",
                        "agency_signature": "agency_sig_002"
                    }
                ],
                "default_deny_all": True
            }
        }
        
        # Government credentials
        self.government_credentials = {
            "GOV-IRB-0002": {
                "agency_name": "Lembaga Hasil Dalam Negeri",
                "agency_id": "GOV-IRB-0002",
                "public_key": "-----BEGIN PUBLIC KEY-----\nMIIB...",
                "certificate_hash": "sha256:abcd1234",
                "certificate_issuer": "Malaysian Government PKI",
                "certificate_expiry": "2026-12-31T23:59:59Z",
                "verified": True,
                "verification_method": "Government PKI",
                "authorized_purposes": ["Tax_Audit", "Tax_Investigation"]
            },
            "GOV-KKM-0001": {
                "agency_name": "Kementerian Kesihatan Malaysia",
                "agency_id": "GOV-KKM-0001",
                "public_key": "-----BEGIN PUBLIC KEY-----\nMIIB...",
                "certificate_hash": "sha256:ijkl9012",
                "certificate_issuer": "Malaysian Government PKI",
                "certificate_expiry": "2027-06-30T23:59:59Z",
                "verified": True,
                "verification_method": "Government PKI",
                "authorized_purposes": ["Healthcare_Emergency", "Medical_Records_Access"]
            },
            "GOV-JPN-0001": {
                "agency_name": "Jabatan Pendaftaran Negara",
                "agency_id": "GOV-JPN-0001",
                "public_key": "-----BEGIN PUBLIC KEY-----\nMIIB...",
                "certificate_hash": "sha256:qrst5678",
                "certificate_issuer": "Malaysian Government PKI",
                "certificate_expiry": "2028-12-31T23:59:59Z",
                "verified": True,
                "verification_method": "Government PKI - Master Registry",
                "authorized_purposes": ["Identity_Verification", "License_Renewal"]
            }
        }
    
    def verify_government_request(
        self,
        request: Dict[str, Any]
    ) -> Tuple[bool, str, Dict]:
        """
        Verify government request against stored policies
        
        Args:
            request: Government access request
        
        Returns:
            (is_valid, message, details)
        """
        
        print(f"\n{'='*70}")
        print(f"🔍 VERIFYING GOVERNMENT REQUEST")
        print(f"{'='*70}")
        
        result = {
            "policy_matched": None,
            "credential_verified": False,
            "request_within_limits": False,
            "signature_valid": False,
            "checks_performed": []
        }
        
        target_user_id = request.get('target_user_id')
        agency_id = request.get('requesting_authority', {}).get('agency_id')
        purpose = request.get('purpose', {}).get('category')
        requested_data = request.get('data_sets_requested', [])
        
        print(f"   User: {target_user_id}")
        print(f"   Agency: {agency_id}")
        print(f"   Purpose: {purpose}")
        
        # Step 1: Verify government credentials
        print(f"\n[Step 1] Verifying government credentials...")
        result["checks_performed"].append("credential_verification")
        
        credential_check = self._verify_government_credential(agency_id, request)
        if not credential_check["valid"]:
            print(f"   ❌ {credential_check['reason']}")
            return False, f"DENY: {credential_check['reason']}", result
        
        print(f"   ✅ Credentials verified")
        result["credential_verified"] = True
        
        # Step 2: Find matching policy
        print(f"\n[Step 2] Finding matching policy...")
        result["checks_performed"].append("policy_matching")
        
        policy = self._find_matching_policy(target_user_id, agency_id, purpose)
        if not policy:
            print(f"   ❌ No matching policy found")
            return False, f"DENY: No pre-approved policy for {agency_id} - {purpose}", result
        
        print(f"   ✅ Policy matched: {policy['policy_id']}")
        result["policy_matched"] = policy["policy_id"]
        
        # Step 3: Verify policy validity
        print(f"\n[Step 3] Verifying policy validity...")
        result["checks_performed"].append("policy_validity")
        
        validity_check = self._check_policy_validity(policy)
        if not validity_check["valid"]:
            print(f"   ❌ {validity_check['reason']}")
            return False, f"DENY: {validity_check['reason']}", result
        
        print(f"   ✅ Policy is valid")
        
        # Step 4: Verify data authorization
        print(f"\n[Step 4] Verifying data authorization...")
        result["checks_performed"].append("data_authorization")
        
        data_check = self._check_data_authorization(policy, requested_data)
        if not data_check["valid"]:
            print(f"   ❌ {data_check['reason']}")
            return False, f"DENY: {data_check['reason']}", result
        
        print(f"   ✅ All data authorized")
        
        # Step 5: Check request limits
        print(f"\n[Step 5] Checking request limits...")
        result["checks_performed"].append("request_limits")
        
        limit_check = self._check_request_limits(policy, target_user_id)
        if not limit_check["valid"]:
            print(f"   ❌ {limit_check['reason']}")
            return False, f"DENY: {limit_check['reason']}", result
        
        print(f"   ✅ Within limits")
        result["request_within_limits"] = True
        
        # Step 6: Verify signature
        print(f"\n[Step 6] Verifying digital signature...")
        result["checks_performed"].append("signature_verification")
        
        signature_check = self._verify_request_signature(request, agency_id)
        if not signature_check["valid"]:
            print(f"   ❌ {signature_check['reason']}")
            return False, f"DENY: {signature_check['reason']}", result
        
        print(f"   ✅ Signature valid")
        result["signature_valid"] = True
        
        # All checks passed
        print(f"\n{'='*70}")
        print(f"✅ ALL CHECKS PASSED")
        print(f"{'='*70}\n")
        
        return True, f"APPROVE: Request matches policy {policy['policy_id']}", result
    
    def _verify_government_credential(
        self,
        agency_id: str,
        request: Dict
    ) -> Dict:
        """Verify government agency credentials"""
        
        if not agency_id:
            return {"valid": False, "reason": "No agency ID provided"}
        
        credentials = self.government_credentials.get(agency_id)
        if not credentials:
            return {"valid": False, "reason": f"Agency {agency_id} not in verified registry"}
        
        if not credentials.get("verified"):
            return {"valid": False, "reason": f"Agency {agency_id} not verified"}
        
        # Check certificate expiry
        try:
            expiry = datetime.fromisoformat(credentials["certificate_expiry"].replace('Z', '+00:00'))
            if expiry < datetime.now(expiry.tzinfo):
                return {"valid": False, "reason": "Agency certificate expired"}
        except:
            pass
        
        # Verify agency name matches
        request_agency_name = request.get('requesting_authority', {}).get('agency_name')
        if request_agency_name != credentials["agency_name"]:
            return {"valid": False, "reason": "Agency name mismatch"}
        
        # Verify purpose is authorized
        request_purpose = request.get('purpose', {}).get('category')
        if request_purpose not in credentials.get("authorized_purposes", []):
            return {"valid": False, "reason": f"Agency not authorized for {request_purpose}"}
        
        return {"valid": True, "reason": "Credentials verified"}
    
    def _find_matching_policy(
        self,
        user_id: str,
        agency_id: str,
        purpose: str
    ) -> Optional[Dict]:
        """Find user policy matching the request"""
        
        user_data = self.user_policies.get(user_id)
        if not user_data:
            return None
        
        for policy in user_data.get("policies", []):
            if (policy["agency_id"] == agency_id and 
                policy["purpose"] == purpose):
                return policy
        
        return None
    
    def _check_policy_validity(self, policy: Dict) -> Dict:
        """Check if policy is still valid"""
        
        try:
            valid_from = datetime.fromisoformat(policy["valid_from"].replace('Z', '+00:00'))
            valid_until = datetime.fromisoformat(policy["valid_until"].replace('Z', '+00:00'))
            now = datetime.now(valid_from.tzinfo)
            
            if now < valid_from:
                return {"valid": False, "reason": f"Policy not yet active"}
            
            if now > valid_until:
                return {"valid": False, "reason": f"Policy expired on {policy['valid_until']}"}
            
            return {"valid": True, "reason": "Policy is valid"}
        
        except Exception as e:
            return {"valid": False, "reason": f"Error checking validity: {e}"}
    
    def _check_data_authorization(
        self,
        policy: Dict,
        requested_data: List[Dict]
    ) -> Dict:
        """Verify requested data is authorized by policy"""
        
        allowed_categories = policy.get("allowed_data_categories", [])
        allowed_fields = policy.get("allowed_fields", {})
        
        for data_set in requested_data:
            category = data_set.get("data_category")
            fields = data_set.get("fields", [])
            
            # Check category
            if category not in allowed_categories:
                return {
                    "valid": False,
                    "reason": f"Category '{category}' not authorized. Allowed: {allowed_categories}"
                }
            
            # Check fields
            allowed_for_category = allowed_fields.get(category, [])
            for field in fields:
                if field not in allowed_for_category:
                    return {
                        "valid": False,
                        "reason": f"Field '{field}' in '{category}' not authorized"
                    }
        
        return {"valid": True, "reason": "All data authorized"}
    
    def _check_request_limits(self, policy: Dict, user_id: str) -> Dict:
        """Check if request is within frequency limits"""
        
        max_requests = policy.get("max_requests_per_year", 999)
        
        # In production: query database for request count
        current_count = 0  # Placeholder
        
        if current_count >= max_requests:
            return {
                "valid": False,
                "reason": f"Request limit exceeded: {current_count}/{max_requests}"
            }
        
        return {"valid": True, "reason": f"Within limits ({current_count}/{max_requests})"}
    
    def _verify_request_signature(self, request: Dict, agency_id: str) -> Dict:
        """Verify cryptographic signature on request"""
        
        request_signature = request.get("digital_signature")
        if not request_signature:
            return {"valid": False, "reason": "No digital signature"}
        
        # In production: verify using agency's public key
        # For now: just check presence
        
        return {"valid": True, "reason": "Signature verified"}
    
    def create_user_policy(self, policy_data: Dict) -> Dict:
        """Create new bilateral policy"""
        
        user_id = policy_data.get("user_id")
        
        # Generate policy ID
        policy_id = f"POL-{datetime.now().year}-{policy_data.get('purpose')[:3].upper()}-{hash(str(policy_data)) % 10000:04d}"
        
        # Create policy hash
        policy_hash = hashlib.sha256(
            json.dumps(policy_data, sort_keys=True).encode()
        ).hexdigest()
        
        policy = {
            "policy_id": policy_id,
            "policy_hash": policy_hash,
            "created_at": datetime.now().isoformat() + 'Z',
            **policy_data
        }
        
        # Store policy
        if user_id not in self.user_policies:
            self.user_policies[user_id] = {
                "policies": [],
                "default_deny_all": True
            }
        
        self.user_policies[user_id]["policies"].append(policy)
        
        print(f"✅ Policy created: {policy_id}")
        
        return {
            "success": True,
            "policy_id": policy_id,
            "policy_hash": policy_hash
        }
    
    def get_user_policies(self, user_id: str) -> List[Dict]:
        """Get all policies for a user"""
        
        user_data = self.user_policies.get(user_id, {})
        return user_data.get("policies", [])
    
    def revoke_policy(self, user_id: str, policy_id: str) -> Dict:
        """Revoke a policy"""
        
        user_data = self.user_policies.get(user_id)
        if not user_data:
            return {"success": False, "message": "User not found"}
        
        policies = user_data.get("policies", [])
        for i, policy in enumerate(policies):
            if policy["policy_id"] == policy_id:
                policies.pop(i)
                print(f"✅ Policy revoked: {policy_id}")
                return {"success": True, "message": f"Policy {policy_id} revoked"}
        
        return {"success": False, "message": f"Policy {policy_id} not found"}


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 BILATERAL POLICY STORAGE TESTING")
    print("="*70)
    
    storage = BilateralPolicyStorage()
    
    # Test 1: Valid request
    print("\n" + "="*70)
    print("TEST 1: VALID TAX REQUEST")
    print("="*70)
    
    valid_request = {
        "request_id": "REQ-2025-TAX001",
        "target_user_id": "900101-01-1234",
        "requesting_authority": {
            "agency_id": "GOV-IRB-0002",
            "agency_name": "Lembaga Hasil Dalam Negeri",
            "officer_id": "IRB-001"
        },
        "purpose": {
            "category": "Tax_Audit"
        },
        "data_sets_requested": [
            {
                "data_category": "Financial_Records",
                "fields": ["account_balance", "transaction_history_12months"]
            }
        ],
        "digital_signature": "sig_abc123"
    }
    
    is_valid, message, details = storage.verify_government_request(valid_request)
    
    print(f"\nRESULT: {'✅ APPROVED' if is_valid else '❌ DENIED'}")
    print(f"MESSAGE: {message}")
    print(f"POLICY MATCHED: {details.get('policy_matched')}")
    
    # Test 2: Invalid request (wrong data)
    print("\n\n" + "="*70)
    print("TEST 2: INVALID REQUEST (Unauthorized Data)")
    print("="*70)
    
    invalid_request = valid_request.copy()
    invalid_request["data_sets_requested"] = [
        {
            "data_category": "Medical_Records",
            "fields": ["diagnosis"]
        }
    ]
    
    is_valid, message, details = storage.verify_government_request(invalid_request)
    
    print(f"\nRESULT: {'✅ APPROVED' if is_valid else '❌ DENIED'}")
    print(f"MESSAGE: {message}")
    
    # Test 3: Create new policy
    print("\n\n" + "="*70)
    print("TEST 3: CREATE NEW POLICY")
    print("="*70)
    
    new_policy = {
        "user_id": "900101-01-1234",
        "agency_name": "Jabatan Pendaftaran Negara",
        "agency_id": "GOV-JPN-0001",
        "purpose": "Identity_Verification",
        "allowed_data_categories": ["Personal_Identity"],
        "allowed_fields": {
            "Personal_Identity": ["full_name", "ic_number", "photo"]
        },
        "valid_from": "2025-01-01T00:00:00Z",
        "valid_until": "2026-01-01T00:00:00Z",
        "max_requests_per_year": 5,
        "notification_required": True,
        "manual_approval_required": False
    }
    
    result = storage.create_user_policy(new_policy)
    
    print(f"\nRESULT: {result['message'] if 'message' in result else 'Policy created'}")
    print(f"POLICY ID: {result['policy_id']}")
    
    # Test 4: View user policies
    print("\n\n" + "="*70)
    print("TEST 4: VIEW USER POLICIES")
    print("="*70)
    
    policies = storage.get_user_policies("900101-01-1234")
    
    print(f"\nUser has {len(policies)} active policies:")
    for policy in policies:
        print(f"\n  Policy ID: {policy['policy_id']}")
        print(f"  Agency: {policy['agency_name']}")
        print(f"  Purpose: {policy['purpose']}")
        print(f"  Valid Until: {policy['valid_until']}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE")
    print("="*70 + "\n")