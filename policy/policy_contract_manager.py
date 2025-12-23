# policy/policy_contract_manager.py
"""
Policy Contract Manager
Integrates policies with blockchain smart contracts
"""

import hashlib
import json
from typing import Dict, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from blockchain.smart_contract_manager import SmartContractManager


class PolicyContractManager:
    """
    Policy-Blockchain Integration
    
    Features:
    - Deploy policies as smart contracts
    - Verify requests against on-chain policies
    - Immutable policy storage
    """
    
    def __init__(self):
        """Initialize policy contract manager"""
        
        self.contract_manager = SmartContractManager()
        self.policy_to_contract = {}  # policy_id -> contract_id mapping
        
        print(f"📜 Policy Contract Manager initialized")
    
    def deploy_policy_contract(
        self,
        policy: Dict
    ) -> str:
        """
        Deploy policy as blockchain smart contract
        
        Args:
            policy: Policy dictionary
        
        Returns:
            Contract ID
        """
        
        user_did = policy.get("user_id")
        agency_id = policy.get("agency_id")
        
        # Deploy contract
        contract_id = self.contract_manager.deploy_policy_contract(
            user_did=user_did,
            agency_id=agency_id,
            policy_data=policy
        )
        
        # Map policy to contract
        policy_id = policy.get("policy_id")
        if policy_id:
            self.policy_to_contract[policy_id] = contract_id
        
        print(f"✅ Policy deployed as contract: {contract_id}")
        
        return contract_id
    
    def verify_against_contract(
        self,
        policy_id: str,
        request: Dict
    ) -> bool:
        """
        Verify request against blockchain policy contract
        
        Args:
            policy_id: Policy ID
            request: Government request
        
        Returns:
            True if request complies
        """
        
        contract_id = self.policy_to_contract.get(policy_id)
        
        if not contract_id:
            print(f"❌ No contract found for policy {policy_id}")
            return False
        
        # Verify via smart contract
        is_valid = self.contract_manager.verify_policy_contract(
            contract_id,
            request
        )
        
        return is_valid
    
    def get_contract_for_policy(self, policy_id: str) -> Optional[str]:
        """Get contract ID for policy"""
        return self.policy_to_contract.get(policy_id)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 POLICY CONTRACT MANAGER TESTING")
    print("="*70)
    
    manager = PolicyContractManager()
    
    # Test policy
    test_policy = {
        "policy_id": "POL-TEST-001",
        "user_id": "did:zetrix:test",
        "agency_id": "GOV-IRB-0002",
        "purpose": "Tax_Audit",
        "allowed_data_categories": ["Financial_Records"],
        "allowed_purposes": ["Tax_Audit"]
    }
    
    # Deploy as contract
    print("\nDeploying policy as smart contract...")
    contract_id = manager.deploy_policy_contract(test_policy)
    
    # Test verification
    print("\nVerifying request against contract...")
    test_request = {
        "agency_id": "GOV-IRB-0002",
        "purpose": "Tax_Audit",
        "data_categories": ["Financial_Records"]
    }
    
    is_valid = manager.verify_against_contract("POL-TEST-001", test_request)
    print(f"   {'✅' if is_valid else '❌'} Request verification: {is_valid}")
    
    print("\n✅ Policy Contract Manager tests complete")
