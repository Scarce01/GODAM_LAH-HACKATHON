# blockchain/smart_contract_manager.py
"""
Smart Contract Manager
Manages on-chain policy contracts
"""

import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime


class SmartContractManager:
    """
    Manages smart contracts on private blockchain
    
    Contract Types:
    - PolicyContract: User-Government bilateral policies
    - ConsentContract: Automated consent validation
    - AccessControl: Data access permissions
    """
    
    def __init__(self):
        self.contracts = {}
        self.contract_id_counter = 0
    
    def deploy_policy_contract(
        self,
        user_did: str,
        agency_id: str,
        policy_data: Dict
    ) -> str:
        """
        Deploy bilateral policy contract
        
        Args:
            user_did: User's DID
            agency_id: Government agency ID
            policy_data: Policy terms
        
        Returns:
            Contract ID
        """
        
        self.contract_id_counter += 1
        contract_id = f"CONTRACT-{self.contract_id_counter:06d}"
        
        contract = {
            "contract_id": contract_id,
            "contract_type": "policy",
            "user_did": user_did,
            "agency_id": agency_id,
            "policy_data": policy_data,
            "deployed_at": datetime.now().isoformat(),
            "status": "active",
            "hash": self._compute_contract_hash(policy_data)
        }
        
        self.contracts[contract_id] = contract
        
        print(f"📜 POLICY CONTRACT DEPLOYED")
        print(f"   Contract ID: {contract_id}")
        print(f"   User: {user_did}")
        print(f"   Agency: {agency_id}")
        
        return contract_id
    
    def verify_policy_contract(
        self,
        contract_id: str,
        request_data: Dict
    ) -> bool:
        """
        Verify request against policy contract
        
        Args:
            contract_id: Contract to verify against
            request_data: Government request
        
        Returns:
            True if request complies with policy
        """
        
        if contract_id not in self.contracts:
            print(f"❌ Contract {contract_id} not found")
            return False
        
        contract = self.contracts[contract_id]
        policy = contract["policy_data"]
        
        # Verify agency
        if request_data.get("agency_id") != contract["agency_id"]:
            print(f"❌ Agency mismatch")
            return False
        
        # Verify purpose
        allowed_purposes = policy.get("allowed_purposes", [])
        if request_data.get("purpose") not in allowed_purposes:
            print(f"❌ Purpose not allowed")
            return False
        
        # Verify data categories
        requested_categories = request_data.get("data_categories", [])
        allowed_categories = policy.get("allowed_data_categories", [])
        
        if not all(cat in allowed_categories for cat in requested_categories):
            print(f"❌ Some data categories not allowed")
            return False
        
        print(f"✅ Request complies with contract {contract_id}")
        return True
    
    def revoke_contract(self, contract_id: str) -> bool:
        """Revoke a contract"""
        
        if contract_id not in self.contracts:
            return False
        
        self.contracts[contract_id]["status"] = "revoked"
        self.contracts[contract_id]["revoked_at"] = datetime.now().isoformat()
        
        print(f"🗑️  Contract {contract_id} revoked")
        return True
    
    def get_contract(self, contract_id: str) -> Optional[Dict]:
        """Get contract details"""
        return self.contracts.get(contract_id)
    
    def list_active_contracts(self, user_did: str) -> List[Dict]:
        """List all active contracts for a user"""
        
        return [
            contract for contract in self.contracts.values()
            if contract["user_did"] == user_did and contract["status"] == "active"
        ]
    
    def _compute_contract_hash(self, contract_data: Dict) -> str:
        """Compute hash of contract for integrity"""
        
        contract_json = json.dumps(contract_data, sort_keys=True)
        return hashlib.sha256(contract_json.encode()).hexdigest()


if __name__ == "__main__":
    manager = SmartContractManager()
    
    # Deploy policy contract
    policy = {
        "allowed_purposes": ["Tax_Audit"],
        "allowed_data_categories": ["Financial_Records"],
        "max_requests_per_year": 2
    }
    
    contract_id = manager.deploy_policy_contract(
        user_did="did:zetrix:test",
        agency_id="GOV-IRB-0002",
        policy_data=policy
    )
    
    # Verify request
    request = {
        "agency_id": "GOV-IRB-0002",
        "purpose": "Tax_Audit",
        "data_categories": ["Financial_Records"]
    }
    
    is_valid = manager.verify_policy_contract(contract_id, request)
    print(f"\n✅ Contract verification: {is_valid}")
    
    # List contracts
    contracts = manager.list_active_contracts("did:zetrix:test")
    print(f"✅ Active contracts: {len(contracts)}")
