# blockchain/consensus_engine.py
"""
PBFT Consensus Engine
Practical Byzantine Fault Tolerance for private blockchain
"""

from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class ConsensusPhase(Enum):
    """PBFT consensus phases"""
    PRE_PREPARE = "pre-prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    COMMITTED = "committed"


class PBFTConsensus:
    """
    Practical Byzantine Fault Tolerance Consensus
    
    Requirements:
    - Minimum 3f + 1 nodes (where f = max faulty nodes)
    - 2f + 1 matching messages to proceed
    
    Phases:
    1. Pre-Prepare: Primary proposes block
    2. Prepare: Nodes verify and broadcast
    3. Commit: Nodes commit if 2f+1 prepare messages
    4. Committed: Block added to chain
    """
    
    def __init__(self, node_id: str, total_nodes: int = 3):
        """
        Initialize PBFT consensus
        
        Args:
            node_id: This node's identifier
            total_nodes: Total number of nodes in network
        """
        
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.max_faulty = (total_nodes - 1) // 3
        self.quorum_size = 2 * self.max_faulty + 1
        
        # Consensus state
        self.current_view = 0
        self.sequence_number = 0
        self.messages = {
            ConsensusPhase.PRE_PREPARE: [],
            ConsensusPhase.PREPARE: [],
            ConsensusPhase.COMMIT: []
        }
        
        print(f"\n{'='*70}")
        print(f"🤝 PBFT CONSENSUS INITIALIZED")
        print(f"{'='*70}")
        print(f"   Node ID:          {node_id}")
        print(f"   Total Nodes:      {total_nodes}")
        print(f"   Max Faulty:       {self.max_faulty}")
        print(f"   Quorum Size:      {self.quorum_size}")
        print(f"   Byzantine Fault:  Can tolerate {self.max_faulty} faulty nodes")
        print(f"{'='*70}\n")
    
    def propose_block(self, block_data: Dict) -> Dict:
        """
        Phase 1: Pre-Prepare (Primary node proposes block)
        
        Args:
            block_data: Block to propose
        
        Returns:
            Pre-prepare message
        """
        
        self.sequence_number += 1
        
        message = {
            "phase": ConsensusPhase.PRE_PREPARE.value,
            "view": self.current_view,
            "sequence": self.sequence_number,
            "block_data": block_data,
            "node_id": self.node_id,
            "timestamp": datetime.now().isoformat()
        }
        
        self.messages[ConsensusPhase.PRE_PREPARE].append(message)
        
        print(f"📤 PRE-PREPARE: Proposing block #{self.sequence_number}")
        
        return message
    
    def verify_and_prepare(self, pre_prepare_msg: Dict) -> Optional[Dict]:
        """
        Phase 2: Prepare (Replica nodes verify and broadcast)
        
        Args:
            pre_prepare_msg: Pre-prepare message from primary
        
        Returns:
            Prepare message or None if invalid
        """
        
        # Verify message
        if not self._verify_pre_prepare(pre_prepare_msg):
            print(f"❌ PREPARE: Invalid pre-prepare message")
            return None
        
        # Create prepare message
        message = {
            "phase": ConsensusPhase.PREPARE.value,
            "view": pre_prepare_msg["view"],
            "sequence": pre_prepare_msg["sequence"],
            "node_id": self.node_id,
            "timestamp": datetime.now().isoformat()
        }
        
        self.messages[ConsensusPhase.PREPARE].append(message)
        
        print(f"✅ PREPARE: Verified block #{pre_prepare_msg['sequence']}")
        
        return message
    
    def check_prepare_quorum(self, sequence: int) -> bool:
        """
        Check if we have 2f+1 prepare messages
        
        Args:
            sequence: Block sequence number
        
        Returns:
            True if quorum reached
        """
        
        matching_messages = [
            msg for msg in self.messages[ConsensusPhase.PREPARE]
            if msg["sequence"] == sequence
        ]
        
        has_quorum = len(matching_messages) >= self.quorum_size
        
        if has_quorum:
            print(f"🎯 PREPARE QUORUM: {len(matching_messages)}/{self.quorum_size} reached")
        
        return has_quorum
    
    def commit_block(self, sequence: int) -> Dict:
        """
        Phase 3: Commit (Node commits if prepare quorum reached)
        
        Args:
            sequence: Block sequence number
        
        Returns:
            Commit message
        """
        
        message = {
            "phase": ConsensusPhase.COMMIT.value,
            "sequence": sequence,
            "node_id": self.node_id,
            "timestamp": datetime.now().isoformat()
        }
        
        self.messages[ConsensusPhase.COMMIT].append(message)
        
        print(f"📝 COMMIT: Committing block #{sequence}")
        
        return message
    
    def check_commit_quorum(self, sequence: int) -> bool:
        """
        Check if we have 2f+1 commit messages
        
        Args:
            sequence: Block sequence number
        
        Returns:
            True if quorum reached
        """
        
        matching_messages = [
            msg for msg in self.messages[ConsensusPhase.COMMIT]
            if msg["sequence"] == sequence
        ]
        
        has_quorum = len(matching_messages) >= self.quorum_size
        
        if has_quorum:
            print(f"🎯 COMMIT QUORUM: {len(matching_messages)}/{self.quorum_size} reached")
            print(f"✅ BLOCK #{sequence} COMMITTED TO CHAIN")
        
        return has_quorum
    
    def _verify_pre_prepare(self, message: Dict) -> bool:
        """Verify pre-prepare message validity"""
        
        # Check required fields
        required_fields = ["phase", "view", "sequence", "block_data"]
        if not all(field in message for field in required_fields):
            return False
        
        # Check view number
        if message["view"] != self.current_view:
            return False
        
        # Check sequence number
        if message["sequence"] <= 0:
            return False
        
        return True
    
    def get_consensus_state(self) -> Dict:
        """Get current consensus state"""
        
        return {
            "current_view": self.current_view,
            "sequence_number": self.sequence_number,
            "quorum_size": self.quorum_size,
            "pre_prepare_count": len(self.messages[ConsensusPhase.PRE_PREPARE]),
            "prepare_count": len(self.messages[ConsensusPhase.PREPARE]),
            "commit_count": len(self.messages[ConsensusPhase.COMMIT])
        }


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 PBFT CONSENSUS TESTING")
    print("="*70)
    
    # Create 3 nodes
    node1 = PBFTConsensus("node-1", total_nodes=3)
    node2 = PBFTConsensus("node-2", total_nodes=3)
    node3 = PBFTConsensus("node-3", total_nodes=3)
    
    # Test block data
    test_block = {
        "transactions": ["tx1", "tx2"],
        "previous_hash": "abc123"
    }
    
    print("\n" + "="*70)
    print("TEST: PBFT CONSENSUS FLOW")
    print("="*70)
    
    # Phase 1: Pre-Prepare (Node 1 is primary)
    print("\n--- PHASE 1: PRE-PREPARE ---")
    pre_prepare = node1.propose_block(test_block)
    
    # Phase 2: Prepare (All nodes verify)
    print("\n--- PHASE 2: PREPARE ---")
    prepare1 = node1.verify_and_prepare(pre_prepare)
    prepare2 = node2.verify_and_prepare(pre_prepare)
    prepare3 = node3.verify_and_prepare(pre_prepare)
    
    # Simulate message broadcast (add to all nodes)
    for node in [node1, node2, node3]:
        node.messages[ConsensusPhase.PREPARE].extend([prepare1, prepare2, prepare3])
    
    # Check quorum
    has_prepare_quorum = node1.check_prepare_quorum(1)
    
    if has_prepare_quorum:
        print("\n--- PHASE 3: COMMIT ---")
        
        # All nodes commit
        commit1 = node1.commit_block(1)
        commit2 = node2.commit_block(1)
        commit3 = node3.commit_block(1)
        
        # Simulate message broadcast
        for node in [node1, node2, node3]:
            node.messages[ConsensusPhase.COMMIT].extend([commit1, commit2, commit3])
        
        # Check commit quorum
        has_commit_quorum = node1.check_commit_quorum(1)
        
        if has_commit_quorum:
            print("\n✅ ALL TESTS PASSED")
            print("✅ Block committed with Byzantine consensus")
        else:
            print("\n❌ COMMIT QUORUM FAILED")
    else:
        print("\n❌ PREPARE QUORUM FAILED")
    
    # Show state
    print("\n📊 CONSENSUS STATE:")
    state = node1.get_consensus_state()
    for key, value in state.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*70)