# api/middleware.py
"""
API Middleware
Authentication, logging, and rate limiting
"""

from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from typing import Dict, Callable
import hashlib


class AuthMiddleware:
    """
    Authentication middleware
    
    Validates:
    - Hardware authentication (IC + Phone)
    - mTLS certificates (Government)
    - Admin 2FA tokens
    """
    
    @staticmethod
    def require_hardware_auth(f: Callable) -> Callable:
        """Require hardware authentication"""
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.json or {}
            
            biometric = data.get('biometric_verified', False)
            card_tap = data.get('card_tapped', False)
            
            if not (biometric and card_tap):
                return jsonify({
                    "status": "error",
                    "message": "Hardware authentication required"
                }), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    @staticmethod
    def require_mtls(f: Callable) -> Callable:
        """Require mTLS certificate"""
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check client certificate
            # In production: verify from request.environ
            
            cert_verified = True  # Placeholder
            
            if not cert_verified:
                return jsonify({
                    "status": "error",
                    "message": "Valid mTLS certificate required"
                }), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    @staticmethod
    def require_2fa(f: Callable) -> Callable:
        """Require 2FA token"""
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('X-2FA-Token')
            
            if not token:
                return jsonify({
                    "status": "error",
                    "message": "2FA token required"
                }), 401
            
            # Verify token
            # In production: verify against TOTP
            
            return f(*args, **kwargs)
        
        return decorated_function


class LoggingMiddleware:
    """
    Logging middleware
    Logs all API requests
    """
    
    def __init__(self):
        self.logs = []
    
    def log_request(self):
        """Log incoming request"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "path": request.path,
            "ip": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'Unknown')
        }
        
        self.logs.append(log_entry)
        
        print(f"📝 {log_entry['method']} {log_entry['path']} from {log_entry['ip']}")
    
    def get_logs(self, limit: int = 100) -> list:
        """Get recent logs"""
        return self.logs[-limit:]


class RateLimitMiddleware:
    """
    Rate limiting middleware
    Prevents API abuse
    """
    
    def __init__(self, max_requests: int = 60, window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Max requests per window
            window: Time window in seconds
        """
        
        self.max_requests = max_requests
        self.window = window
        self.request_counts = {}
    
    def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if request is within rate limit
        
        Args:
            identifier: IP address or user ID
        
        Returns:
            True if allowed
        """
        
        now = datetime.now()
        
        # Clean old entries
        cutoff = now - timedelta(seconds=self.window)
        self.request_counts = {
            k: v for k, v in self.request_counts.items()
            if v['reset_time'] > cutoff
        }
        
        # Check limit
        if identifier not in self.request_counts:
            self.request_counts[identifier] = {
                "count": 1,
                "reset_time": now + timedelta(seconds=self.window)
            }
            return True
        
        entry = self.request_counts[identifier]
        
        if entry['count'] >= self.max_requests:
            print(f"⚠️  Rate limit exceeded for {identifier}")
            return False
        
        entry['count'] += 1
        return True
    
    def rate_limit_decorator(self, f: Callable) -> Callable:
        """Decorator for rate limiting"""
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = request.remote_addr
            
            if not self.check_rate_limit(identifier):
                return jsonify({
                    "status": "error",
                    "message": "Rate limit exceeded"
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 MIDDLEWARE TESTING")
    print("="*70)
    
    # Test rate limiter
    rate_limiter = RateLimitMiddleware(max_requests=5, window=10)
    
    print("\nTesting rate limiter (5 requests/10 seconds):")
    
    for i in range(7):
        allowed = rate_limiter.check_rate_limit("test-ip")
        status = "✅ Allowed" if allowed else "❌ Blocked"
        print(f"  Request {i+1}: {status}")
    
    print("\n✅ Middleware tests complete")