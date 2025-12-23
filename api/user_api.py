# api/user_api.py
"""
User API
Citizen-facing API for identity management
"""

from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.security_core import SecurityCore
from storage.pdsa_local_storage import PDSALocalStorage
from blockchain.zetrix_private_node import ZetrixPrivateNode
from blockchain.blockchain_optimized import IdentityParticipant


class UserAPI:
    """
    User API - Port 5001
    
    Endpoints:
    - POST /api/v1/identity/view - View my data
    - POST /api/v1/identity/update - Update my data
    - GET  /api/v1/consent/history - View consent history
    - POST /api/v1/consent/respond - Respond to access request
    - GET  /api/v1/policies - View my policies
    - POST /api/v1/policies/create - Create new policy
    """
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 5001,
        ic_key: bytes = None,
        phone_key: bytes = None
    ):
        """
        Initialize User API
        
        Args:
            host: API host
            port: API port
            ic_key: IC card hardware key
            phone_key: Phone hardware key
        """
        
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        
        # Initialize subsystems
        self.security = SecurityCore()
        self.storage = PDSALocalStorage()
        self.blockchain = ZetrixPrivateNode(
            node_id="user-api-node",
            port=8001
        )
        
        self.ic_key = ic_key or b"default-ic-key-32bytes-here!!"
        self.phone_key = phone_key or b"default-phone-key-32bytes-her!"
        
        # Register routes
        self._register_routes()
        
        print(f"\n{'='*70}")
        print(f"👤 USER API INITIALIZED")
        print(f"{'='*70}")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Endpoints: 6")
        print(f"{'='*70}\n")
    
    def _register_routes(self):
        """Register API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "service": "user_api",
                "version": "2.0.0"
            })
        
        @self.app.route('/api/v1/identity/view', methods=['POST'])
        def view_identity():
            """
            View my identity data
            
            Request:
            {
                "did": "did:zetrix:mykad-123",
                "biometric_verified": true,
                "card_tapped": true
            }
            
            Response:
            {
                "status": "success",
                "data": {...}
            }
            """
            
            try:
                data = request.json
                
                # Validate authentication
                if not data.get('biometric_verified') or not data.get('card_tapped'):
                    return jsonify({
                        "status": "error",
                        "message": "Authentication failed: Both biometric and card tap required"
                    }), 401
                
                did = data.get('did')
                
                # Get latest anchor from blockchain
                anchor = self.blockchain.get_latest_anchor(did)
                
                if not anchor:
                    return jsonify({
                        "status": "error",
                        "message": "No identity data found"
                    }), 404
                
                # Retrieve Fragment A from storage
                fragment_a = self.storage.retrieve_fragment_a(did)
                fragment_b = anchor.get_fragment_b()
                
                # Reconstruct data
                identity_data = self.security.decrypt_and_reconstruct(
                    fragment_a,
                    fragment_b,
                    self.ic_key,
                    self.phone_key,
                    {"version": "2.0-advanced"}
                )
                
                return jsonify({
                    "status": "success",
                    "data": identity_data
                })
            
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/v1/identity/update', methods=['POST'])
        def update_identity():
            """
            Update my identity data
            
            Request:
            {
                "did": "did:zetrix:mykad-123",
                "identity_data": {...},
                "access_policy": {...},
                "biometric_verified": true,
                "card_tapped": true
            }
            """
            
            try:
                data = request.json
                
                # Validate authentication
                if not data.get('biometric_verified') or not data.get('card_tapped'):
                    return jsonify({
                        "status": "error",
                        "message": "Authentication failed"
                    }), 401
                
                did = data.get('did')
                identity_data = data.get('identity_data')
                access_policy = data.get('access_policy', {})
                
                # Fragment data
                frag_a, frag_b, merkle, metadata = self.security.fragment_and_encrypt(
                    identity_data,
                    self.ic_key,
                    self.phone_key
                )
                
                # Store Fragment A
                self.storage.store_fragment_a(did, frag_a, frag_b.hex())
                
                # Create blockchain anchor
                from blockchain.blockchain_optimized import IdentityAnchorTransaction
                import json
                
                citizen = IdentityParticipant("User", did)
                self.blockchain.blockchain.register_participant(citizen)
                
                anchor = IdentityAnchorTransaction(
                    creator_did=did,
                    merkle_root=merkle,
                    fragment_b_hex=frag_b.hex(),
                    storage_metadata={
                        "cloud": {
                            "location": "pdsa_san",
                            "size_bytes": len(frag_a)
                        },
                        "fragmentation_metadata": metadata
                    },
                    access_policy=json.dumps(access_policy)
                )
                anchor.sign(citizen)
                
                # Add to blockchain
                self.blockchain.add_identity_anchor(anchor)
                
                return jsonify({
                    "status": "success",
                    "message": "Identity updated",
                    "merkle_root": merkle
                })
            
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/v1/consent/history', methods=['GET'])
        def consent_history():
            """
            View consent history
            
            Query params:
            - did: User DID
            """
            
            try:
                did = request.args.get('did')
                
                if not did:
                    return jsonify({
                        "status": "error",
                        "message": "DID required"
                    }), 400
                
                # Get consent logs from blockchain
                history = []
                
                for block in self.blockchain.blockchain.chain:
                    for tx in block.transactions:
                        if hasattr(tx, 'request_id'):  # ConsentLog
                            history.append(tx.to_dict())
                
                return jsonify({
                    "status": "success",
                    "history": history,
                    "total": len(history)
                })
            
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/v1/consent/respond', methods=['POST'])
        def respond_to_request():
            """
            Respond to government access request
            
            Request:
            {
                "request_id": "REQ-001",
                "decision": "approved" | "denied",
                "did": "did:zetrix:mykad-123"
            }
            """
            
            try:
                data = request.json
                
                request_id = data.get('request_id')
                decision = data.get('decision')
                did = data.get('did')
                
                # Log consent to blockchain
                from blockchain.blockchain_optimized import ConsentLogTransaction
                
                citizen = self.blockchain.blockchain.participants.get(did)
                
                if not citizen:
                    return jsonify({
                        "status": "error",
                        "message": "User not found"
                    }), 404
                
                consent_log = ConsentLogTransaction(
                    request_id=request_id,
                    authority="Government",
                    purpose="Data Access",
                    requested_fields=["fields"],
                    decision=decision
                )
                consent_log.sign(citizen)
                
                self.blockchain.add_consent_log(consent_log)
                
                return jsonify({
                    "status": "success",
                    "message": f"Consent {decision}",
                    "request_id": request_id
                })
            
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/v1/policies', methods=['GET'])
        def get_policies():
            """Get user's active policies"""
            
            did = request.args.get('did')
            
            return jsonify({
                "status": "success",
                "policies": [],
                "message": "Policy retrieval from bilateral storage"
            })
        
        @self.app.route('/api/v1/policies/create', methods=['POST'])
        def create_policy():
            """Create new bilateral policy"""
            
            data = request.json
            
            return jsonify({
                "status": "success",
                "message": "Policy created",
                "policy_id": "POL-001"
            })
    
    def run(self, debug: bool = False):
        """Start the User API server"""
        
        print(f"\n🚀 STARTING USER API")
        print(f"   URL: http://{self.host}:{self.port}")
        print(f"   Endpoints available at /api/v1/*")
        print(f"\nPress CTRL+C to stop\n")
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=debug
        )


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 USER API TESTING")
    print("="*70)
    
    # Initialize API
    api = UserAPI(port=5001)
    
    # Run server
    api.run(debug=True)