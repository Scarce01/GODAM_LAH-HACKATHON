# deployment/docker_builder.py
"""
Docker Image Builder
Builds production-ready Docker images for OBSIDIAN components
"""

import os
import subprocess
from typing import List, Dict, Optional
from datetime import datetime


class DockerBuilder:
    """
    Docker Image Builder
    
    Builds containerized images for:
    - API services (User, Government, Admin)
    - Web applications (User Portal, Gov Portal)
    - Blockchain nodes
    - Storage services
    - AI orchestrator
    """
    
    def __init__(self, registry: str = "obsidian.registry.my"):
        """
        Initialize Docker builder
        
        Args:
            registry: Docker registry URL
        """
        
        self.registry = registry
        self.images = []
        
        print(f"\n{'='*70}")
        print(f"🐳 Docker Builder Initialized")
        print(f"{'='*70}")
        print(f"   Registry: {registry}")
        print(f"{'='*70}\n")
    
    def generate_dockerfile_api(self) -> str:
        """
        Generate Dockerfile for API services
        
        Returns:
            Dockerfile content
        """
        
        dockerfile = """
# OBSIDIAN API Service Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libssl-dev \\
    libffi-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY core/ ./core/
COPY storage/ ./storage/
COPY blockchain/ ./blockchain/
COPY api/ ./api/
COPY policy/ ./policy/
COPY ai/ ./ai/

# Create non-root user
RUN useradd -m -u 1000 obsidian && \\
    chown -R obsidian:obsidian /app

USER obsidian

# Expose API ports
EXPOSE 5001 5002 5003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:5001/health')"

# Start API service
CMD ["python", "-m", "api.user_api"]
"""
        return dockerfile
    
    def generate_dockerfile_webapp(self) -> str:
        """
        Generate Dockerfile for web applications
        
        Returns:
            Dockerfile content
        """
        
        dockerfile = """
# OBSIDIAN Web Application Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY webapp/ ./webapp/
COPY templates/ ./templates/
COPY static/ ./static/

# Create non-root user
RUN useradd -m -u 1000 obsidian && \\
    chown -R obsidian:obsidian /app

USER obsidian

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "webapp.user_portal"]
"""
        return dockerfile
    
    def generate_dockerfile_blockchain(self) -> str:
        """
        Generate Dockerfile for blockchain nodes
        
        Returns:
            Dockerfile content
        """
        
        dockerfile = """
# OBSIDIAN Blockchain Node Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install blockchain dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libssl-dev \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy blockchain code
COPY blockchain/ ./blockchain/
COPY core/ ./core/

# Create data directory
RUN mkdir -p /data/blockchain && \\
    useradd -m -u 1000 obsidian && \\
    chown -R obsidian:obsidian /app /data

USER obsidian

# Blockchain ports
EXPOSE 8545 8546 30303

VOLUME ["/data/blockchain"]

CMD ["python", "-m", "blockchain.zetrix_private_node"]
"""
        return dockerfile
    
    def generate_dockerfile_ai(self) -> str:
        """
        Generate Dockerfile for AI orchestrator
        
        Returns:
            Dockerfile content
        """
        
        dockerfile = """
# OBSIDIAN AI Orchestrator Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Ollama
RUN apt-get update && apt-get install -y \\
    curl \\
    gcc \\
    && curl -fsSL https://ollama.com/install.sh | sh \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy AI code
COPY ai/ ./ai/
COPY policy/ ./policy/

# Pull Ollama model
RUN ollama pull llama3.2

RUN useradd -m -u 1000 obsidian && \\
    chown -R obsidian:obsidian /app

USER obsidian

EXPOSE 11434

CMD ["python", "-m", "ai.obsidian_orchestrator"]
"""
        return dockerfile
    
    def generate_docker_compose(self) -> str:
        """
        Generate docker-compose.yml for development
        
        Returns:
            docker-compose.yml content
        """
        
        compose = """
version: '3.8'

services:
  # User API
  user-api:
    build:
      context: .
      dockerfile: deployment/Dockerfile.api
    image: ${REGISTRY}/obsidian-user-api:${VERSION}
    container_name: obsidian-user-api
    ports:
      - "5001:5001"
    volumes:
      - ./data/storage:/data/storage
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    networks:
      - obsidian-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Government API
  government-api:
    build:
      context: .
      dockerfile: deployment/Dockerfile.api
    image: ${REGISTRY}/obsidian-government-api:${VERSION}
    container_name: obsidian-government-api
    ports:
      - "5002:5002"
    volumes:
      - ./certs:/certs:ro
    environment:
      - ENVIRONMENT=production
      - MTLS_ENABLED=true
    networks:
      - obsidian-network
    restart: unless-stopped

  # Admin API
  admin-api:
    build:
      context: .
      dockerfile: deployment/Dockerfile.api
    image: ${REGISTRY}/obsidian-admin-api:${VERSION}
    container_name: obsidian-admin-api
    ports:
      - "127.0.0.1:5003:5003"
    environment:
      - ENVIRONMENT=production
      - ADMIN_ONLY=true
    networks:
      - obsidian-network
    restart: unless-stopped

  # User Portal
  user-portal:
    build:
      context: .
      dockerfile: deployment/Dockerfile.webapp
    image: ${REGISTRY}/obsidian-user-portal:${VERSION}
    container_name: obsidian-user-portal
    ports:
      - "8000:8000"
    networks:
      - obsidian-network
    restart: unless-stopped

  # Blockchain Node 1
  blockchain-node-1:
    build:
      context: .
      dockerfile: deployment/Dockerfile.blockchain
    image: ${REGISTRY}/obsidian-blockchain:${VERSION}
    container_name: obsidian-blockchain-1
    ports:
      - "8545:8545"
    volumes:
      - blockchain-data-1:/data/blockchain
    environment:
      - NODE_ID=1
      - CONSENSUS_MODE=raft
    networks:
      - obsidian-network
    restart: unless-stopped

  # Blockchain Node 2
  blockchain-node-2:
    build:
      context: .
      dockerfile: deployment/Dockerfile.blockchain
    image: ${REGISTRY}/obsidian-blockchain:${VERSION}
    container_name: obsidian-blockchain-2
    ports:
      - "8546:8545"
    volumes:
      - blockchain-data-2:/data/blockchain
    environment:
      - NODE_ID=2
      - CONSENSUS_MODE=raft
    networks:
      - obsidian-network
    restart: unless-stopped

  # AI Orchestrator
  ai-orchestrator:
    build:
      context: .
      dockerfile: deployment/Dockerfile.ai
    image: ${REGISTRY}/obsidian-ai:${VERSION}
    container_name: obsidian-ai
    ports:
      - "11434:11434"
    volumes:
      - ai-models:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    networks:
      - obsidian-network
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: obsidian-postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=obsidian
      - POSTGRES_USER=obsidian
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    networks:
      - obsidian-network
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: obsidian-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - obsidian-network
    restart: unless-stopped

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: obsidian-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./deployment/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - obsidian-network
    restart: unless-stopped

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    container_name: obsidian-grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    networks:
      - obsidian-network
    restart: unless-stopped

networks:
  obsidian-network:
    driver: bridge

volumes:
  blockchain-data-1:
  blockchain-data-2:
  postgres-data:
  redis-data:
  ai-models:
  prometheus-data:
  grafana-data:
"""
        return compose
    
    def build_image(self, component: str, tag: str = "latest") -> bool:
        """
        Build Docker image for component
        
        Args:
            component: Component name (api, webapp, blockchain, ai)
            tag: Image tag
        
        Returns:
            True if build successful
        """
        
        print(f"\n🔨 Building {component} image...")
        
        dockerfile = f"Dockerfile.{component}"
        image_name = f"{self.registry}/obsidian-{component}:{tag}"
        
        # Generate Dockerfile
        if component == "api":
            content = self.generate_dockerfile_api()
        elif component == "webapp":
            content = self.generate_dockerfile_webapp()
        elif component == "blockchain":
            content = self.generate_dockerfile_blockchain()
        elif component == "ai":
            content = self.generate_dockerfile_ai()
        else:
            print(f"❌ Unknown component: {component}")
            return False
        
        # Write Dockerfile
        with open(dockerfile, 'w') as f:
            f.write(content)
        
        # Build image
        cmd = [
            "docker", "build",
            "-t", image_name,
            "-f", dockerfile,
            "."
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Built: {image_name}")
            self.images.append(image_name)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e.stderr}")
            return False
    
    def push_image(self, image_name: str) -> bool:
        """
        Push image to registry
        
        Args:
            image_name: Full image name with tag
        
        Returns:
            True if push successful
        """
        
        print(f"\n📤 Pushing {image_name}...")
        
        cmd = ["docker", "push", image_name]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Pushed: {image_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Push failed: {e}")
            return False
    
    def build_all(self, tag: str = "latest") -> bool:
        """
        Build all OBSIDIAN images
        
        Args:
            tag: Image tag
        
        Returns:
            True if all builds successful
        """
        
        print(f"\n{'='*70}")
        print(f"🚀 BUILDING ALL OBSIDIAN IMAGES")
        print(f"{'='*70}\n")
        
        components = ["api", "webapp", "blockchain", "ai"]
        
        for component in components:
            if not self.build_image(component, tag):
                return False
        
        print(f"\n{'='*70}")
        print(f"✅ ALL IMAGES BUILT SUCCESSFULLY")
        print(f"{'='*70}")
        print(f"   Total images: {len(self.images)}")
        for img in self.images:
            print(f"   - {img}")
        print(f"{'='*70}\n")
        
        return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Docker Builder Testing")
    print("="*70)
    
    builder = DockerBuilder()
    
    # Test 1: Generate Dockerfiles
    print("\n[TEST 1] Generate Dockerfiles")
    
    dockerfiles = {
        "API": builder.generate_dockerfile_api(),
        "WebApp": builder.generate_dockerfile_webapp(),
        "Blockchain": builder.generate_dockerfile_blockchain(),
        "AI": builder.generate_dockerfile_ai()
    }
    
    for name, content in dockerfiles.items():
        if "FROM python" in content:
            print(f"✅ {name} Dockerfile generated")
    
    # Test 2: Generate docker-compose
    print("\n[TEST 2] Generate docker-compose.yml")
    compose = builder.generate_docker_compose()
    if "version:" in compose and "services:" in compose:
        print("✅ docker-compose.yml generated")
        
        # Save to file
        with open("docker-compose.yml", "w") as f:
            f.write(compose)
        print("   Saved to: docker-compose.yml")
    
    print("\n✅ Docker Builder tests complete!")