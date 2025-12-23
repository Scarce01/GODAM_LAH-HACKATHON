# blockchain/__init__.py
"""
OBSIDIAN Blockchain Module
Private Zetrix Blockchain for Fragment B Storage

Components:
- blockchain_optimized: Fragment B storage (existing)
- zetrix_private_node: Private blockchain node manager
- consensus_engine: PBFT consensus for private chain
- smart_contracts: On-chain policy contracts

Author: OBSIDIAN Team
Version: 2.0 (Iron Vault - Private Chain)
"""

__version__ = "2.0.0"
__author__ = "OBSIDIAN Team"

from .blockchain_optimized import (
    IdentityBlockchain,
    IdentityParticipant,
    IdentityAnchorTransaction,
    ConsentLogTransaction,
    Block
)
from .zetrix_private_node import ZetrixPrivateNode
from .consensus_engine import PBFTConsensus
from .smart_contract_manager import SmartContractManager

__all__ = [
    'IdentityBlockchain',
    'IdentityParticipant',
    'IdentityAnchorTransaction',
    'ConsentLogTransaction',
    'Block',
    'ZetrixPrivateNode',
    'PBFTConsensus',
    'SmartContractManager'
]

# Blockchain configuration
BLOCKCHAIN_CONFIG = {
    "network_type": "private",
    "consensus": "pbft",
    "min_nodes": 3,
    "block_time": 3,  # seconds
    "difficulty": 2,
    "max_block_size": 1048576,  # 1 MB
    "chain_id": "obsidian-pdsa-mainnet",
    "genesis_timestamp": "2025-01-01T00:00:00Z"
}

print(f"⛓️  OBSIDIAN Blockchain Module v{__version__} loaded")
print(f"   Network: Private Zetrix ({BLOCKCHAIN_CONFIG['network_type']})")
print(f"   Consensus: {BLOCKCHAIN_CONFIG['consensus'].upper()}")