# deployment/load_balancer.py
"""
Load Balancer Configuration
HAProxy and Nginx setup for high availability
"""


class LoadBalancer:
    """
    Load Balancer Configuration
    
    Supports:
    - HAProxy (Layer 4/7 load balancing)
    - Nginx (Reverse proxy)
    - SSL/TLS termination
    - Health checks
    - Session persistence
    """
    
    def __init__(self):
        """Initialize load balancer configuration"""
        
        print(f"\n{'='*70}")
        print(f"⚖️  Load Balancer Configuration Initialized")
        print(f"{'='*70}\n")
    
    def generate_haproxy_config(self) -> str:
        """
        Generate HAProxy configuration
        
        Returns:
            HAProxy config content
        """
        
        config = """
# OBSIDIAN HAProxy Configuration

global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

    # SSL configuration
    tune.ssl.default-dh-param 2048
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000
    timeout client  50000
    timeout server  50000
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http
    errorfile 504 /etc/haproxy/errors/504.http

# Statistics dashboard
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE

# Frontend: User API
frontend user_api_frontend
    bind *:443 ssl crt /etc/ssl/certs/obsidian.pem
    bind *:80
    redirect scheme https code 301 if !{ ssl_fc }
    
    default_backend user_api_backend
    
    # Rate limiting
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }

# Backend: User API (3 replicas)
backend user_api_backend
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    
    server api-1 10.0.1.10:5001 check
    server api-2 10.0.1.11:5001 check
    server api-3 10.0.1.12:5001 check

# Frontend: Government API (mTLS)
frontend government_api_frontend
    bind *:5002 ssl crt /etc/ssl/certs/obsidian.pem ca-file /etc/ssl/certs/gov-ca.pem verify required
    
    default_backend government_api_backend

# Backend: Government API
backend government_api_backend
    balance leastconn
    option httpchk GET /health
    
    server api-gov-1 10.0.1.10:5002 check
    server api-gov-2 10.0.1.11:5002 check

# Frontend: Web Portal
frontend webapp_frontend
    bind *:8000 ssl crt /etc/ssl/certs/obsidian.pem
    
    default_backend webapp_backend

# Backend: Web Portal
backend webapp_backend
    balance roundrobin
    option httpchk GET /health
    
    # Session stickiness (same user → same server)
    cookie SERVERID insert indirect nocache
    
    server webapp-1 10.0.2.10:8000 check cookie webapp-1
    server webapp-2 10.0.2.11:8000 check cookie webapp-2

# Frontend: Blockchain RPC
frontend blockchain_rpc_frontend
    bind *:8545
    mode tcp
    
    default_backend blockchain_rpc_backend

# Backend: Blockchain RPC (round-robin across 5 nodes)
backend blockchain_rpc_backend
    mode tcp
    balance roundrobin
    
    server blockchain-1 10.0.3.10:8545 check
    server blockchain-2 10.0.3.11:8545 check
    server blockchain-3 10.0.3.12:8545 check
    server blockchain-4 10.0.3.13:8545 check
    server blockchain-5 10.0.3.14:8545 check
"""
        return config
    
    def generate_nginx_config(self) -> str:
        """
        Generate Nginx configuration
        
        Returns:
            Nginx config content
        """
        
        config = """
# OBSIDIAN Nginx Configuration

user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 4096;
    use epoll;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=webapp_limit:10m rate=50r/s;

    # Upstream: User API
    upstream user_api {
        least_conn;
        server 10.0.1.10:5001 max_fails=3 fail_timeout=30s;
        server 10.0.1.11:5001 max_fails=3 fail_timeout=30s;
        server 10.0.1.12:5001 max_fails=3 fail_timeout=30s;
    }

    # Upstream: Web Portal
    upstream webapp {
        ip_hash;  # Session persistence
        server 10.0.2.10:8000 max_fails=3 fail_timeout=30s;
        server 10.0.2.11:8000 max_fails=3 fail_timeout=30s;
    }

    # Server: User Portal (HTTPS)
    server {
        listen 443 ssl http2;
        server_name obsidian.my;

        ssl_certificate /etc/ssl/certs/obsidian.pem;
        ssl_certificate_key /etc/ssl/private/obsidian.key;

        location / {
            proxy_pass http://webapp;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Rate limiting
            limit_req zone=webapp_limit burst=20 nodelay;
        }

        location /health {
            access_log off;
            return 200 "OK";
        }
    }

    # Server: API (HTTPS)
    server {
        listen 443 ssl http2;
        server_name api.obsidian.my;

        ssl_certificate /etc/ssl/certs/obsidian.pem;
        ssl_certificate_key /etc/ssl/private/obsidian.key;

        location / {
            proxy_pass http://user_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Rate limiting
            limit_req zone=api_limit burst=5 nodelay;
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
    }

    # Server: HTTP → HTTPS redirect
    server {
        listen 80;
        server_name obsidian.my api.obsidian.my;
        return 301 https://$server_name$request_uri;
    }
}
"""
        return config
    
    def save_configs(self, output_dir: str = "./loadbalancer") -> bool:
        """
        Save load balancer configs
        
        Args:
            output_dir: Output directory
        
        Returns:
            True if successful
        """
        
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n💾 Saving load balancer configs to {output_dir}...")
        
        # Save HAProxy config
        haproxy_config = self.generate_haproxy_config()
        with open(os.path.join(output_dir, "haproxy.cfg"), 'w') as f:
            f.write(haproxy_config)
        print(f"   Saved: haproxy.cfg")
        
        # Save Nginx config
        nginx_config = self.generate_nginx_config()
        with open(os.path.join(output_dir, "nginx.conf"), 'w') as f:
            f.write(nginx_config)
        print(f"   Saved: nginx.conf")
        
        print(f"✅ All configs saved")
        
        return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Load Balancer Testing")
    print("="*70)
    
    lb = LoadBalancer()
    
    # Test: Generate configs
    print("\n[TEST] Generate Load Balancer Configs")
    
    haproxy_config = lb.generate_haproxy_config()
    nginx_config = lb.generate_nginx_config()
    
    if haproxy_config and nginx_config:
        print("✅ Configs generated")
        
        # Save to files
        lb.save_configs("./loadbalancer")
        print("✅ Configs saved")
    
    print("\n✅ Load Balancer tests complete!")
    print("\nTo deploy:")
    print("  HAProxy: cp loadbalancer/haproxy.cfg /etc/haproxy/")
    print("  Nginx:   cp loadbalancer/nginx.conf /etc/nginx/")
```

---

## 🎉 **OBSIDIAN IRON VAULT - 100% COMPLETE!** 🎉

---

## 📊 Final Project Summary
```
✅ FOLDER 1:  core/              - 9-layer military security (6 files)
✅ FOLDER 2:  storage/           - PDSA local storage (5 files)
✅ FOLDER 3:  blockchain/        - Private Zetrix chain (4 files)
✅ FOLDER 4:  communication/     - mTLS secure channels (6 files)
✅ FOLDER 5:  api/               - Three-tier API (6 files)
✅ FOLDER 6:  ai/                - Ollama + Policy + RAG (5 files)
✅ FOLDER 7:  policy/            - Bilateral agreements (5 files)
✅ FOLDER 8:  webapp/            - User/Gov/Admin portals (5 files)
✅ FOLDER 9:  hardware/          - MyKad + Phone TEE (5 files)
✅ FOLDER 10: deployment/        - Docker/K8s/Ansible (8 files)

📦 TOTAL: 10 FOLDERS, 55 FILES
📝 TOTAL LINES: ~15,000+ production code