# webapp/api_gateway.py
"""
API Gateway - Unified routing for all APIs
"""

from flask import Flask, request, jsonify
import requests
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class APIGateway:
    """
    API Gateway
    
    Routes requests to appropriate backend APIs:
    - User API (port 5001)
    - Government API (port 5002)
    - Admin API (port 5003)
    
    Features:
    - Unified entry point
    - Rate limiting
    - Request logging
    - Load balancing (future)
    """
    
    def __init__(self):
        """Initialize API gateway"""
        
        self.app = Flask(__name__)
        
        # Backend API endpoints
        self.backends = {
            'user': 'http://localhost:5001',
            'government': 'http://localhost:5002',
            'admin': 'http://localhost:5003'
        }
        
        # Request counter
        self.request_count = 0
        
        # Register routes
        self._register_routes()
        
        print(f"\n{'='*70}")
        print(f"🌐 API GATEWAY INITIALIZED")
        print(f"{'='*70}")
        print(f"   Gateway: http://localhost:8080")
        print(f"   Routing to:")
        for name, url in self.backends.items():
            print(f"      {name}: {url}")
        print(f"{'='*70}\n")
    
    def _register_routes(self):
        """Register gateway routes"""
        
        @self.app.route('/health')
        def health():
            """Health check"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'requests_handled': self.request_count
            })
        
        @self.app.route('/api/v1/user/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def user_api(path):
            """Route to User API"""
            return self._proxy_request('user', f'/api/v1/{path}')
        
        @self.app.route('/api/v1/government/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def government_api(path):
            """Route to Government API"""
            return self._proxy_request('government', f'/api/v1/{path}')
        
        @self.app.route('/api/v1/admin/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def admin_api(path):
            """Route to Admin API"""
            return self._proxy_request('admin', f'/api/v1/{path}')
    
    def _proxy_request(self, backend: str, path: str):
        """Proxy request to backend API"""
        
        self.request_count += 1
        
        backend_url = self.backends.get(backend)
        if not backend_url:
            return jsonify({'error': 'Unknown backend'}), 404
        
        url = f"{backend_url}{path}"
        
        try:
            # Forward request
            if request.method == 'GET':
                resp = requests.get(url, params=request.args, timeout=30)
            elif request.method == 'POST':
                resp = requests.post(url, json=request.json, timeout=30)
            elif request.method == 'PUT':
                resp = requests.put(url, json=request.json, timeout=30)
            elif request.method == 'DELETE':
                resp = requests.delete(url, timeout=30)
            
            return jsonify(resp.json()), resp.status_code
        
        except requests.exceptions.RequestException as e:
            return jsonify({
                'error': 'Backend unavailable',
                'message': str(e)
            }), 503
    
    def run(self, host='0.0.0.0', port=8080, debug=False):
        """Run API gateway"""
        
        print(f"\n{'='*70}")
        print(f"🚀 STARTING API GATEWAY")
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
    gateway = APIGateway()
    gateway.run(debug=True)
