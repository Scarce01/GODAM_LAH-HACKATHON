# webapp/admin_dashboard.py
"""
Admin Dashboard - System administration interface
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
import sys
import os
from datetime import datetime, timedelta
import secrets
import pyotp

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from storage.pdsa_local_storage import PDSALocalStorage
from blockchain.zetrix_private_node import ZetrixPrivateNode


class AdminDashboardApp:
    """
    Admin Dashboard Application
    
    Features:
    - System monitoring
    - User management
    - Blockchain statistics
    - Storage statistics
    - Security audit logs
    - System backup/restore
    """
    
    def __init__(self, config: dict = None):
        """Initialize admin dashboard"""
        
        self.app = Flask(__name__, template_folder='templates')
        self.app.secret_key = secrets.token_hex(32)
        
        # Session configuration
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SESSION_PERMANENT'] = False
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
        Session(self.app)
        
        # Initialize subsystems
        self.storage = PDSALocalStorage()
        self.blockchain = ZetrixPrivateNode()
        
        # 2FA secret (in production: store securely per admin)
        self.totp_secret = pyotp.random_base32()
        
        # Register routes
        self._register_routes()
        
        print(f"\n{'='*70}")
        print(f"🔧 ADMIN DASHBOARD INITIALIZED")
        print(f"{'='*70}")
        print(f"   Access: https://127.0.0.1:8002 (localhost only)")
        print(f"   2FA: Required")
        print(f"   Session Timeout: 15 minutes")
        print(f"   2FA Secret: {self.totp_secret}")
        print(f"{'='*70}\n")
    
    def _register_routes(self):
        """Register all web routes"""
        
        # ==================== AUTHENTICATION ====================
        
        @self.app.route('/')
        def index():
            """Admin login page"""
            return render_template('admin_login.html')
        
        @self.app.route('/login', methods=['POST'])
        def login():
            """Admin login with 2FA"""
            
            username = request.form.get('username')
            password = request.form.get('password')
            totp_code = request.form.get('totp_code')
            
            # Verify credentials (in production: check database)
            if username != 'admin' or password != 'demo_password':
                return render_template('admin_login.html', error="Invalid credentials")
            
            # Verify 2FA
            totp = pyotp.TOTP(self.totp_secret)
            if not totp.verify(totp_code):
                return render_template('admin_login.html', error="Invalid 2FA code")
            
            session['admin'] = True
            session['username'] = username
            session['login_time'] = datetime.now().isoformat()
            
            return redirect(url_for('dashboard'))
        
        @self.app.route('/logout')
        def logout():
            """Logout"""
            session.clear()
            return redirect(url_for('index'))
        
        # ==================== DASHBOARD ====================
        
        @self.app.route('/dashboard')
        def dashboard():
            """Main admin dashboard"""
            
            if not session.get('admin'):
                return redirect(url_for('index'))
            
            # Get system statistics
            stats = {
                'total_users': self._get_total_users(),
                'blockchain_blocks': self._get_blockchain_blocks(),
                'storage_used_gb': self._get_storage_used(),
                'requests_today': self._get_requests_today(),
                'system_uptime': self._get_system_uptime(),
                'active_sessions': self._get_active_sessions()
            }
            
            return render_template('admin_dashboard.html', stats=stats)
        
        # ==================== USER MANAGEMENT ====================
        
        @self.app.route('/users')
        def users():
            """User management"""
            
            if not session.get('admin'):
                return redirect(url_for('index'))
            
            user_list = self._get_all_users()
            
            return render_template('admin_users.html', users=user_list)
        
        @self.app.route('/users/<user_id>')
        def user_details(user_id):
            """View user details"""
            
            if not session.get('admin'):
                return redirect(url_for('index'))
            
            user_info = self._get_user_info(user_id)
            
            return render_template('user_details.html', user=user_info)
        
        # ==================== BLOCKCHAIN ====================
        
        @self.app.route('/blockchain')
        def blockchain():
            """Blockchain statistics"""
            
            if not session.get('admin'):
                return redirect(url_for('index'))
            
            stats = self.blockchain.get_network_status()
            
            return render_template('admin_blockchain.html', stats=stats)
        
        @self.app.route('/blockchain/blocks')
        def blockchain_blocks():
            """View blockchain blocks"""
            
            if not session.get('admin'):
                return redirect(url_for('index'))
            
            blocks = self._get_recent_blocks(limit=50)
            
            return render_template('blockchain_blocks.html', blocks=blocks)
        
        # ==================== STORAGE ====================
        
        @self.app.route('/storage')
        def storage():
            """Storage statistics"""
            
            if not session.get('admin'):
                return redirect(url_for('index'))
            
            stats = self.storage.get_storage_stats()
            
            return render_template('admin_storage.html', stats=stats)
        
        # ==================== AUDIT LOGS ====================
        
        @self.app.route('/audit-logs')
        def audit_logs():
            """System audit logs"""
            
            if not session.get('admin'):
                return redirect(url_for('index'))
            
            logs = self._get_system_logs(limit=100)
            
            return render_template('audit_logs_admin.html', logs=logs)
        
        # ==================== SYSTEM BACKUP ====================
        
        @self.app.route('/backup', methods=['GET', 'POST'])
        def backup():
            """System backup"""
            
            if not session.get('admin'):
                return redirect(url_for('index'))
            
            if request.method == 'GET':
                backup_history = self._get_backup_history()
                return render_template('backup.html', history=backup_history)
            
            # POST: Trigger backup
            backup_result = self._trigger_backup()
            
            return jsonify(backup_result)
        
        # ==================== SYSTEM SETTINGS ====================
        
        @self.app.route('/settings')
        def settings():
            """System settings"""
            
            if not session.get('admin'):
                return redirect(url_for('index'))
            
            current_settings = self._get_system_settings()
            
            return render_template('settings.html', settings=current_settings)
    
    # ==================== HELPER METHODS ====================
    
    def _get_total_users(self) -> int:
        """Get total registered users"""
        # In production: query database
        return 1247
    
    def _get_blockchain_blocks(self) -> int:
        """Get blockchain block count"""
        return len(self.blockchain.chain)
    
    def _get_storage_used(self) -> float:
        """Get storage used in GB"""
        stats = self.storage.get_storage_stats()
        return stats['total_size_mb'] / 1024
    
    def _get_requests_today(self) -> int:
        """Get requests processed today"""
        # In production: query logs
        return 342
    
    def _get_system_uptime(self) -> str:
        """Get system uptime"""
        # In production: check actual uptime
        return "15 days, 7 hours"
    
    def _get_active_sessions(self) -> int:
        """Get active user sessions"""
        # In production: check session store
        return 28
    
    def _get_all_users(self) -> list:
        """Get all users"""
        # Demo data
        return [
            {
                'user_id': '900101-01-****',
                'name': 'Ahmad Bin Ali',
                'registered': '2024-06-15',
                'last_login': '2025-12-22',
                'status': 'Active'
            }
        ]
    
    def _get_user_info(self, user_id: str) -> dict:
        """Get user information"""
        # Demo data
        return {
            'user_id': user_id,
            'name': 'Ahmad Bin Ali',
            'registered': '2024-06-15',
            'total_consents': 15,
            'active_policies': 3,
            'last_login': '2025-12-22'
        }
    
    def _get_recent_blocks(self, limit: int = 50) -> list:
        """Get recent blockchain blocks"""
        blocks = self.blockchain.chain[-limit:]
        return [
            {
                'index': b.index,
                'hash': b.hash[:16] + '...',
                'transactions': len(b.transactions),
                'timestamp': b.timestamp
            }
            for b in blocks
        ]
    
    def _get_system_logs(self, limit: int = 100) -> list:
        """Get system audit logs"""
        # Demo data
        return [
            {
                'timestamp': '2025-12-22T14:30:00Z',
                'level': 'INFO',
                'event': 'USER_LOGIN',
                'user_id': '900101-01-****'
            }
        ]
    
    def _get_backup_history(self) -> list:
        """Get backup history"""
        # Demo data
        return [
            {
                'backup_id': 'BACKUP-20251220',
                'timestamp': '2025-12-20T02:00:00Z',
                'size_gb': 45.2,
                'status': 'Success'
            }
        ]
    
    def _trigger_backup(self) -> dict:
        """Trigger system backup"""
        # In production: actual backup
        return {
            'success': True,
            'backup_id': f"BACKUP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'started_at': datetime.now().isoformat()
        }
    
    def _get_system_settings(self) -> dict:
        """Get system settings"""
        return {
            'session_timeout': 1800,
            'max_file_size_mb': 10,
            'backup_schedule': 'Daily at 02:00',
            'log_retention_days': 90
        }
    
    def run(self, host='127.0.0.1', port=8002, debug=False):
        """Run the web application"""
        
        print(f"\n{'='*70}")
        print(f"🚀 STARTING ADMIN DASHBOARD")
        print(f"{'='*70}")
        print(f"   URL: https://{host}:{port}")
        print(f"   Localhost Only: Yes")
        print(f"   2FA Required: Yes")
        print(f"   Debug: {debug}")
        print(f"\n   2FA Setup:")
        print(f"   Secret: {self.totp_secret}")
        print(f"   Use Google Authenticator or similar app")
        print(f"\n   Press CTRL+C to stop")
        print(f"{'='*70}\n")
        
        # Bind to localhost only for security
        self.app.run(host=host, port=port, debug=debug)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    app = AdminDashboardApp()
    app.run(debug=True)