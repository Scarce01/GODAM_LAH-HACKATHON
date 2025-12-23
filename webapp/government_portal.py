# webapp/government_portal.py
"""
Government Portal - Agency request submission interface
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
import sys
import os
from datetime import datetime, timedelta
import secrets

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api.government_api import GovernmentAPI
from policy.bilateral_policy_storage import BilateralPolicyStorage
from ai.integrated_risk_analyzer import IntegratedRiskAnalyzer


class GovernmentPortalApp:
    """
    Government Portal Application
    
    Features:
    - Submit data access requests
    - Track request status
    - View approved data
    - Manage agency credentials
    - View audit logs
    """
    
    def __init__(self, config: dict = None):
        """Initialize government portal"""
        
        self.app = Flask(__name__, template_folder='templates')
        self.app.secret_key = secrets.token_hex(32)
        
        # Session configuration
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SESSION_PERMANENT'] = False
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
        Session(self.app)
        
        # Initialize subsystems
        self.gov_api = GovernmentAPI()
        self.policy_storage = BilateralPolicyStorage()
        self.risk_analyzer = IntegratedRiskAnalyzer()
        
        # Register routes
        self._register_routes()
        
        print(f"\n{'='*70}")
        print(f"🏛️ GOVERNMENT PORTAL INITIALIZED")
        print(f"{'='*70}")
        print(f"   Access: https://gov.obsidian.my:8001")
        print(f"   mTLS: Required")
        print(f"   Session Timeout: 1 hour")
        print(f"{'='*70}\n")
    
    def _register_routes(self):
        """Register all web routes"""
        
        # ==================== MAIN PAGES ====================
        
        @self.app.route('/')
        def index():
            """Landing page"""
            return render_template('gov_index.html')
        
        @self.app.route('/dashboard')
        def dashboard():
            """Agency dashboard"""
            
            if 'agency_id' not in session:
                return redirect(url_for('login'))
            
            agency_id = session['agency_id']
            
            stats = {
                'pending_requests': 5,
                'approved_today': 12,
                'denied_today': 2,
                'total_this_month': 145
            }
            
            return render_template('gov_dashboard.html', stats=stats, agency_id=agency_id)
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Login with government credentials"""
            
            if request.method == 'GET':
                return render_template('gov_login.html')
            
            # POST: Verify mTLS certificate
            agency_id = request.form.get('agency_id')
            officer_id = request.form.get('officer_id')
            
            # In production: verify client certificate
            # For demo: simple validation
            if agency_id and agency_id.startswith('GOV-'):
                session['agency_id'] = agency_id
                session['officer_id'] = officer_id
                session['agency_name'] = self._get_agency_name(agency_id)
                return redirect(url_for('dashboard'))
            
            return render_template('gov_login.html', error="Invalid credentials")
        
        @self.app.route('/logout')
        def logout():
            """Logout"""
            session.clear()
            return redirect(url_for('index'))
        
        # ==================== REQUEST SUBMISSION ====================
        
        @self.app.route('/submit-request', methods=['GET', 'POST'])
        def submit_request():
            """Submit new data access request"""
            
            if 'agency_id' not in session:
                return redirect(url_for('login'))
            
            if request.method == 'GET':
                return render_template('submit_request.html')
            
            # POST: Submit request
            agency_id = session['agency_id']
            
            gov_request = {
                'request_id': f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'target_user_id': request.form.get('target_user_id'),
                'requesting_authority': {
                    'agency_id': agency_id,
                    'agency_name': session['agency_name'],
                    'officer_id': session['officer_id'],
                    'officer_name': request.form.get('officer_name')
                },
                'purpose': {
                    'category': request.form.get('purpose'),
                    'detailed_reason': request.form.get('reason')
                },
                'data_sets_requested': [
                    {
                        'data_category': cat,
                        'fields': request.form.getlist(f'fields_{cat}')
                    }
                    for cat in request.form.getlist('data_categories')
                ],
                'retention_period': {
                    'duration_days': int(request.form.get('retention_days', 365))
                },
                'timestamp': datetime.now().isoformat() + 'Z',
                'digital_signature': self._generate_signature(agency_id)
            }
            
            # Submit via API
            result = self._submit_request_to_api(gov_request)
            
            if result['success']:
                return redirect(url_for('request_status', request_id=result['request_id']))
            
            return render_template('submit_request.html', error=result.get('error'))
        
        @self.app.route('/requests')
        def requests():
            """View all requests"""
            
            if 'agency_id' not in session:
                return redirect(url_for('login'))
            
            agency_id = session['agency_id']
            
            # Get agency's requests
            request_list = self._get_agency_requests(agency_id)
            
            return render_template('gov_requests.html', requests=request_list)
        
        @self.app.route('/request/<request_id>')
        def request_status(request_id):
            """View request status and details"""
            
            if 'agency_id' not in session:
                return redirect(url_for('login'))
            
            # Get request details
            req_details = self._get_request_details(request_id)
            
            if not req_details:
                return "Request not found", 404
            
            return render_template('request_status.html', request=req_details)
        
        # ==================== DATA RETRIEVAL ====================
        
        @self.app.route('/retrieve-data/<request_id>')
        def retrieve_data(request_id):
            """Retrieve approved data"""
            
            if 'agency_id' not in session:
                return redirect(url_for('login'))
            
            # Verify request is approved
            req_details = self._get_request_details(request_id)
            
            if req_details['status'] != 'APPROVED':
                return "Request not approved", 403
            
            # Get data
            data = self._retrieve_approved_data(request_id)
            
            return render_template('retrieved_data.html', request=req_details, data=data)
        
        @self.app.route('/api/download-data/<request_id>')
        def api_download_data(request_id):
            """Download data as JSON"""
            
            if 'agency_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            data = self._retrieve_approved_data(request_id)
            
            return jsonify({
                'request_id': request_id,
                'retrieved_at': datetime.now().isoformat(),
                'data': data
            })
        
        # ==================== CREDENTIALS ====================
        
        @self.app.route('/credentials')
        def credentials():
            """View agency credentials"""
            
            if 'agency_id' not in session:
                return redirect(url_for('login'))
            
            agency_id = session['agency_id']
            
            # Get credential details
            creds = self.policy_storage.government_credentials.get(agency_id, {})
            
            return render_template('credentials.html', credentials=creds)
        
        # ==================== AUDIT LOGS ====================
        
        @self.app.route('/audit-logs')
        def audit_logs():
            """View audit logs"""
            
            if 'agency_id' not in session:
                return redirect(url_for('login'))
            
            agency_id = session['agency_id']
            
            # Get audit logs
            logs = self._get_audit_logs(agency_id)
            
            return render_template('audit_logs.html', logs=logs)
    
    # ==================== HELPER METHODS ====================
    
    def _get_agency_name(self, agency_id: str) -> str:
        """Get agency name from ID"""
        
        agency_map = {
            'GOV-IRB-0002': 'Lembaga Hasil Dalam Negeri',
            'GOV-KKM-0001': 'Kementerian Kesihatan Malaysia',
            'GOV-JPN-0001': 'Jabatan Pendaftaran Negara',
            'GOV-PDRM-0003': 'Polis Diraja Malaysia'
        }
        
        return agency_map.get(agency_id, 'Unknown Agency')
    
    def _generate_signature(self, agency_id: str) -> str:
        """Generate digital signature"""
        # In production: actual cryptographic signature
        return f"sig_{secrets.token_hex(16)}"
    
    def _submit_request_to_api(self, gov_request: dict) -> dict:
        """Submit request via API"""
        
        # In production: call actual API
        # For demo: simulate success
        
        return {
            'success': True,
            'request_id': gov_request['request_id'],
            'status': 'PENDING'
        }
    
    def _get_agency_requests(self, agency_id: str) -> list:
        """Get all requests from agency"""
        
        # Demo data
        return [
            {
                'request_id': 'REQ-2025-001',
                'target_user': '900101-01-****',
                'purpose': 'Tax_Audit',
                'status': 'APPROVED',
                'submitted': '2025-12-20T10:00:00Z'
            },
            {
                'request_id': 'REQ-2025-002',
                'target_user': '850505-08-****',
                'purpose': 'Tax_Audit',
                'status': 'PENDING',
                'submitted': '2025-12-22T09:30:00Z'
            }
        ]
    
    def _get_request_details(self, request_id: str) -> dict:
        """Get request details"""
        
        # Demo data
        return {
            'request_id': request_id,
            'target_user_id': '900101-01-****',
            'status': 'APPROVED',
            'submitted': '2025-12-20T10:00:00Z',
            'approved': '2025-12-20T10:45:00Z',
            'purpose': 'Tax_Audit',
            'data_categories': ['Financial_Records']
        }
    
    def _retrieve_approved_data(self, request_id: str) -> dict:
        """Retrieve approved data"""
        
        # Demo data
        return {
            'account_balance': 'RM 45,678.90',
            'transaction_history': '[Last 12 months data]',
            'retrieved_at': datetime.now().isoformat()
        }
    
    def _get_audit_logs(self, agency_id: str) -> list:
        """Get audit logs"""
        
        # Demo data
        return [
            {
                'timestamp': '2025-12-22T10:30:00Z',
                'action': 'REQUEST_SUBMITTED',
                'request_id': 'REQ-2025-002',
                'officer': session.get('officer_id')
            },
            {
                'timestamp': '2025-12-20T10:00:00Z',
                'action': 'DATA_RETRIEVED',
                'request_id': 'REQ-2025-001',
                'officer': session.get('officer_id')
            }
        ]
    
    def run(self, host='0.0.0.0', port=8001, debug=False):
        """Run the web application"""
        
        print(f"\n{'='*70}")
        print(f"🚀 STARTING GOVERNMENT PORTAL")
        print(f"{'='*70}")
        print(f"   URL: https://{host}:{port}")
        print(f"   mTLS: Required")
        print(f"   Debug: {debug}")
        print(f"\n   Press CTRL+C to stop")
        print(f"{'='*70}\n")
        
        # In production: configure SSL
        self.app.run(host=host, port=port, debug=debug)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    app = GovernmentPortalApp()
    app.run(debug=True)