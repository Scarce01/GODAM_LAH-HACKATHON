# policy/__init__.py
"""
OBSIDIAN Policy Module
Bilateral policy management between users and government agencies

Components:
- bilateral_policy_storage: User-Government policy agreements
- policy_validator: Request validation against policies
- schema_validator: JSON schema validation
- policy_contract_manager: Smart contract integration

Author: OBSIDIAN Team
Version: 2.0 (Iron Vault - Enhanced Policies)
"""

__version__ = "2.0.0"
__author__ = "OBSIDIAN Team"

from .bilateral_policy_storage import BilateralPolicyStorage
from .policy_validator import PolicyValidator
from .schema_validator import SchemaValidator
from .policy_contract_manager import PolicyContractManager

__all__ = [
    'BilateralPolicyStorage',
    'PolicyValidator',
    'SchemaValidator',
    'PolicyContractManager'
]

# Policy configuration
POLICY_CONFIG = {
    "default_deny_all": True,
    "require_user_signature": True,
    "require_agency_signature": True,
    "max_policy_duration_days": 1825,  # 5 years
    "min_policy_duration_days": 30,
    "max_requests_per_year": 100,
    "enable_auto_renewal": False,
    "policy_version": "2.0"
}

print(f"📜 OBSIDIAN Policy Module v{__version__} loaded")
print(f"   Default: Deny All ({POLICY_CONFIG['default_deny_all']})")
print(f"   Signatures Required: User + Agency")
print(f"   Max Duration: {POLICY_CONFIG['max_policy_duration_days']} days")