# communication/mtls_client.py
"""
mTLS Client
Client-side mutual TLS handler
"""

import ssl
import socket
import json
from typing import Dict, Any, Optional


class MTLSClient:
    """
    Mutual TLS Client
    
    Features:
    - Presents client certificate
    - Verifies server identity
    - Secure communication
    """
    
    def __init__(
        self,
        cert_path: str = None,
        key_path: str = None,
        ca_path: str = None
    ):
        """
        Initialize mTLS client
        
        Args:
            cert_path: Client certificate
            key_path: Client private key
            ca_path: CA certificate
        """
        
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path
        
        # Create SSL context
        self.ssl_context = self._create_client_context()
        
        print(f"📱 mTLS Client initialized")
    
    def _create_client_context(self) -> ssl.SSLContext:
        """Create client SSL context"""
        
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        
        # Set minimum TLS version
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        
        # Load client certificate
        if self.cert_path and self.key_path:
            context.load_cert_chain(self.cert_path, self.key_path)
        
        # Load CA
        if self.ca_path:
            context.load_verify_locations(self.ca_path)
        
        # Verify server certificate
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        return context
    
    def send_request(
        self,
        host: str,
        port: int,
        message: Dict[str, Any],
        timeout: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Send request to mTLS server
        
        Args:
            host: Server host
            port: Server port
            message: Request message
            timeout: Connection timeout
        
        Returns:
            Response dictionary
        """
        
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Wrap with SSL
            secure_sock = self.ssl_context.wrap_socket(
                sock,
                server_hostname=host
            )
            
            # Connect
            secure_sock.connect((host, port))
            
            # Send message
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
            
            secure_sock.sendall(len(message_bytes).to_bytes(4, 'big'))
            secure_sock.sendall(message_bytes)
            
            # Receive response
            response_length = int.from_bytes(secure_sock.recv(4), 'big')
            response_bytes = secure_sock.recv(response_length)
            
            response = json.loads(response_bytes.decode('utf-8'))
            
            # Close
            secure_sock.close()
            
            return response
        
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None


if __name__ == "__main__":
    client = MTLSClient()
    print("✅ mTLS Client ready")