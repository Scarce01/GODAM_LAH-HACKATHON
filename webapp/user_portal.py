# webapp/user_portal.py
"""
User Portal - Citizen-facing web interface
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
import sys
import os
from datetime import datetime, timedelta
import secrets

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.security_core import SecurityCore
from storage.pdsa_local_storage import PDSALocalStorage
from blockchain.zetrix_private_node import ZetrixPrivateNode
from ai.obsidian_orchestrator import OBSIDIANOrchestrator
from policy.bilateral_policy_storage import BilateralPolicyStorage


class UserPortalApp:
    """
    User Portal Application
    
    Features:
    - View personal identity data
    - Manage consent policies
    - Review government requests
    - Approve/deny data access
    - View consent history
    - Manage emergency policies
    """
    
    def __init__(self, config: dict = None):
        """Initialize user portal"""
        
        self.app = Flask(__name__, template_folder='templates')
        self.app.secret_key = secrets.token_hex(32)
        
        # Session configuration
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SESSION_PERMANENT'] = False
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
        Session(self.app)
        
        # Initialize subsystems
        self.security = SecurityCore()
        self.storage = PDSALocalStorage()
        self.blockchain = ZetrixPrivateNode()
        self.ai = OBSIDIANOrchestrator()
        self.policy_storage = BilateralPolicyStorage()
        
        # Register routes
        self._register_routes()
        
        print(f"\n{'='*70}")
        print(f"🌐 USER PORTAL INITIALIZED")
        print(f"{'='*70}")
        print(f"   Access: http://localhost:8000")
        print(f"   Session Timeout: 30 minutes")
        print(f"   SSL: Enabled")
        print(f"{'='*70}\n")
    
    def _register_routes(self):
        """Register all web routes"""
        
        # ==================== MAIN PAGES ====================
        
        @self.app.route('/')
        def index():
            """Landing page"""
            return render_template('user_index.html')
        
        @self.app.route('/dashboard')
        def dashboard():
            """User dashboard (requires login)"""
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user_id = session['user_id']
            
            # Get user statistics
            stats = {
                'pending_requests': self._get_pending_requests_count(user_id),
                'active_policies': len(self.policy_storage.get_user_policies(user_id)),
                'total_consents': self._get_consent_count(user_id),
                'last_access': self._get_last_access_time(user_id)
            }
            
            return render_template('user_dashboard.html', stats=stats, user_id=user_id)
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Login page"""
            
            if request.method == 'GET':
                return render_template('user_login.html')
            
            # POST: Handle login
            ic_number = request.form.get('ic_number')
            
            # In production: verify hardware authentication
            # For demo: simple IC validation
            if ic_number and len(ic_number) == 14:
                session['user_id'] = ic_number
                session['login_time'] = datetime.now().isoformat()
                return redirect(url_for('dashboard'))
            
            return render_template('user_login.html', error="Invalid IC number")
        
        @self.app.route('/logout')
        def logout():
            """Logout"""
            session.clear()
            return redirect(url_for('index'))
        
        # ==================== DATA MANAGEMENT ====================
        
        @self.app.route('/my-data')
        def my_data():
            """View personal data"""
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user_id = session['user_id']
            
            # In production: require hardware authentication here
            # For demo: show placeholder
            
            return render_template('my_data.html', user_id=user_id)
        
        @self.app.route('/api/view-data', methods=['POST'])
        def api_view_data():
            """API endpoint to view data (requires hardware auth)"""
            
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            user_id = session['user_id']
            
            # Verify hardware authentication
            card_auth = request.json.get('card_auth')
            biometric_auth = request.json.get('biometric_auth')
            
            if not card_auth or not biometric_auth:
                return jsonify({
                    'error': 'Hardware authentication required',
                    'required': ['MyKad tap', 'Biometric scan']
                }), 403
            
            # In production: verify actual signatures
            # For demo: simulate data retrieval
            
            demo_data = {
                'name': 'Ahmad Bin Ali',
                'ic_number': user_id,
                'blood_type': 'O+',
                'address': '12, Jalan Ampang, 50450 KL',
                'phone': '+6012-3456789',
                'last_updated': '2025-12-15T10:30:00Z'
            }
            
            return jsonify({
                'success': True,
                'data': demo_data,
                'retrieved_at': datetime.now().isoformat()
            })
        
        # ==================== POLICY MANAGEMENT ====================
        
        @self.app.route('/policies')
        def policies():
            """View and manage policies"""
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user_id = session['user_id']
            policies = self.policy_storage.get_user_policies(user_id)
            
            return render_template('policies.html', policies=policies)
        
        @self.app.route('/policies/create', methods=['GET', 'POST'])
        def create_policy():
            """Create new policy"""
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            if request.method == 'GET':
                return render_template('create_policy.html')
            
            # POST: Create policy
            user_id = session['user_id']
            
            policy_data = {
                'user_id': user_id,
                'agency_id': request.form.get('agency_id'),
                'agency_name': request.form.get('agency_name'),
                'purpose': request.form.get('purpose'),
                'allowed_data_categories': request.form.getlist('data_categories'),
                'valid_from': request.form.get('valid_from'),
                'valid_until': request.form.get('valid_until'),
                'max_requests_per_year': int(request.form.get('max_requests', 5)),
                'notification_required': request.form.get('notification') == 'yes',
                'manual_approval_required': request.form.get('manual_approval') == 'yes'
            }
            
            result = self.policy_storage.create_user_policy(policy_data)
            
            if result['success']:
                return redirect(url_for('policies'))
            
            return render_template('create_policy.html', error="Failed to create policy")
        
        @self.app.route('/policies/revoke/<policy_id>', methods=['POST'])
        def revoke_policy(policy_id):
            """Revoke a policy"""
            
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            user_id = session['user_id']
            result = self.policy_storage.revoke_policy(user_id, policy_id)
            
            return jsonify(result)
        
        # ==================== REQUEST MANAGEMENT ====================
        
        @self.app.route('/requests')
        def requests():
            """View pending requests"""
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user_id = session['user_id']
            
            # Get pending requests (in production: from database)
            pending_requests = self._get_pending_requests(user_id)
            
            return render_template('requests.html', requests=pending_requests)
        
        @self.app.route('/requests/<request_id>')
        def request_details(request_id):
            """View request details with AI analysis"""
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user_id = session['user_id']
            
            # Get request details
            gov_request = self._get_request_by_id(request_id)
            
            if not gov_request:
                return "Request not found", 404
            
            # Get AI analysis
            analysis = self.ai.process_government_request(gov_request)
            
            return render_template(
                'request_details.html',
                request=gov_request,
                analysis=analysis
            )
        
        @self.app.route('/api/approve-request', methods=['POST'])
        def api_approve_request():
            """Approve a request (requires hardware auth)"""
            
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            user_id = session['user_id']
            request_id = request.json.get('request_id')
            
            # Verify hardware authentication
            card_auth = request.json.get('card_auth')
            biometric_auth = request.json.get('biometric_auth')
            
            if not card_auth or not biometric_auth:
                return jsonify({
                    'error': 'Hardware authentication required'
                }), 403
            
            # Log consent to blockchain
            consent_result = self._log_consent(user_id, request_id, 'APPROVED')
            
            return jsonify({
                'success': True,
                'message': 'Request approved',
                'blockchain_tx': consent_result['tx_hash'],
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/deny-request', methods=['POST'])
        def api_deny_request():
            """Deny a request"""
            
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            user_id = session['user_id']
            request_id = request.json.get('request_id')
            
            # Log denial to blockchain
            consent_result = self._log_consent(user_id, request_id, 'DENIED')
            
            return jsonify({
                'success': True,
                'message': 'Request denied',
                'blockchain_tx': consent_result['tx_hash'],
                'timestamp': datetime.now().isoformat()
            })
        
        # ==================== CONSENT HISTORY ====================
        
        @self.app.route('/history')
        def history():
            """View consent history"""
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user_id = session['user_id']
            
            # Get consent history from blockchain
            consent_logs = self._get_consent_history(user_id)
            
            return render_template('history.html', logs=consent_logs)
        
        # ==================== EMERGENCY SETTINGS ====================
        
        @self.app.route('/emergency')
        def emergency():
            """Emergency policy settings"""
            
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user_id = session['user_id']
            
            # Get current emergency policies
            emergency_policies = self._get_emergency_policies(user_id)
            
            return render_template('emergency.html', policies=emergency_policies)
    
    # ==================== HELPER METHODS ====================
    
    def _get_pending_requests_count(self, user_id: str) -> int:
        """Get count of pending requests"""
        # In production: query database
        return 2  # Demo
    
    def _get_consent_count(self, user_id: str) -> int:
        """Get total consent count"""
        # In production: query blockchain
        return 15  # Demo
    
    def _get_last_access_time(self, user_id: str) -> str:
        """Get last data access time"""
        # In production: query from logs
        return "2025-12-15 14:30"  # Demo
    
    def _get_pending_requests(self, user_id: str) -> list:
        """Get pending requests"""
        # Demo data
        return [
            {
                'request_id': 'REQ-2025-TAX001',
                'agency_name': 'Lembaga Hasil Dalam Negeri',
                'purpose': 'Tax_Audit',
                'timestamp': '2025-12-22T10:30:00Z',
                'status': 'PENDING'
            },
            {
                'request_id': 'REQ-2025-MED002',
                'agency_name': 'Hospital Kuala Lumpur',
                'purpose': 'Medical_Treatment',
                'timestamp': '2025-12-22T14:15:00Z',
                'status': 'PENDING'
            }
        ]
    
    def _get_request_by_id(self, request_id: str) -> dict:
        """Get request by ID"""
        # Demo data
        if request_id == 'REQ-2025-TAX001':
            return {
                'request_id': request_id,
                'target_user_id': session.get('user_id'),
                'requesting_authority': {
                    'agency_id': 'GOV-IRB-0002',
                    'agency_name': 'Lembaga Hasil Dalam Negeri',
                    'officer_name': 'Ahmad Ibrahim'
                },
                'purpose': {
                    'category': 'Tax_Audit',
                    'detailed_reason': 'Annual tax audit for FY2024'
                },
                'data_sets_requested': [
                    {
                        'data_category': 'Financial_Records',
                        'fields': ['account_balance', 'transaction_history_12months']
                    }
                ],
                'retention_period': {
                    'duration_days': 2555
                },
                'timestamp': '2025-12-22T10:30:00Z'
            }
        return None
    
    def _log_consent(self, user_id: str, request_id: str, decision: str) -> dict:
        """Log consent decision to blockchain"""
        
        # In production: actual blockchain transaction
        tx_hash = f"0x{secrets.token_hex(32)}"
        
        return {
            'success': True,
            'tx_hash': tx_hash,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_consent_history(self, user_id: str) -> list:
        """Get consent history from blockchain"""
        
        # Demo data
        return [
            {
                'request_id': 'REQ-2025-TAX001',
                'agency': 'LHDN',
                'purpose': 'Tax_Audit',
                'decision': 'APPROVED',
                'timestamp': '2025-12-22T10:45:00Z',
                'blockchain_tx': '0xabc123...'
            },
            {
                'request_id': 'REQ-2025-JPJ001',
                'agency': 'JPJ',
                'purpose': 'License_Renewal',
                'decision': 'APPROVED',
                'timestamp': '2025-11-15T09:20:00Z',
                'blockchain_tx': '0xdef456...'
            }
        ]
    
    def _get_emergency_policies(self, user_id: str) -> list:
        """Get emergency policies"""
        
        # Demo data
        return [
            {
                'policy_id': 'POL-2024-MED-001',
                'agency_name': 'Kementerian Kesihatan Malaysia',
                'purpose': 'Healthcare_Emergency',
                'auto_approve': True,
                'active': True
            }
        ]
    
    def run(self, host='0.0.0.0', port=8000, debug=False):
        """Run the web application"""
        
        print(f"\n{'='*70}")
        print(f"🚀 STARTING USER PORTAL")
        print(f"{'='*70}")
        print(f"   URL: http://{host}:{port}")
        print(f"   Debug: {debug}")
        print(f"\n   Press CTRL+C to stop")
        print(f"{'='*70}\n")
        
        self.app.run(host=host, port=port, debug=debug)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    app = UserPortalApp()
    app.run(debug=True)