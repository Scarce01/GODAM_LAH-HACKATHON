# communication/mtls_server.py
"""
mTLS Server
Server-side mutual TLS handler
"""

import ssl
import socket
import threading
import json
from typing import Callable, Dict, Any


class MTLSServer:
    """
    Mutual TLS Server
    
    Features:
    - Requires client certificates
    - Verifies client identity
    - Handles encrypted connections
    """
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8443,
        cert_path: str = None,
        key_path: str = None,
        ca_path: str = None
    ):
        """
        Initialize mTLS server
        
        Args:
            host: Server host
            port: Server port
            cert_path: Server certificate
            key_path: Server private key
            ca_path: CA certificate for client verification
        """
        
        self.host = host
        self.port = port
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path
        
        self.is_running = False
        self.handlers = {}
        
        # Create SSL context
        self.ssl_context = self._create_server_context()
        
        print(f"\n{'='*70}")
        print(f"🖥️  mTLS SERVER INITIALIZED")
        print(f"{'='*70}")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Certificate: {cert_path or 'Not configured'}")
        print(f"{'='*70}\n")
    
    def _create_server_context(self) -> ssl.SSLContext:
        """Create server SSL context"""
        
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # Set minimum TLS version
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        
        # Load server certificate and key
        if self.cert_path and self.key_path:
            context.load_cert_chain(self.cert_path, self.key_path)
        
        # Load CA for client verification
        if self.ca_path:
            context.load_verify_locations(self.ca_path)
        
        # Require client certificates
        context.verify_mode = ssl.CERT_REQUIRED
        
        return context
    
    def register_handler(
        self,
        message_type: str,
        handler: Callable[[Dict], Dict]
    ):
        """
        Register message handler
        
        Args:
            message_type: Type of message to handle
            handler: Function that processes the message
        """
        
        self.handlers[message_type] = handler
        print(f"📝 Registered handler for: {message_type}")
    
    def start(self):
        """Start the mTLS server"""
        
        print(f"\n🚀 STARTING mTLS SERVER")
        print(f"   Listening on {self.host}:{self.port}")
        
        self.is_running = True
        
        # Create server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"   ✅ Server is running")
        
        while self.is_running:
            try:
                # Accept connection
                client_socket, address = server_socket.accept()
                
                # Handle in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
            
            except Exception as e:
                if self.is_running:
                    print(f"   ⚠️  Error accepting connection: {e}")
    
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle client connection"""
        
        print(f"\n📞 NEW CONNECTION from {address[0]}:{address[1]}")
        
        try:
            # Wrap socket with SSL
            secure_socket = self.ssl_context.wrap_socket(
                client_socket,
                server_side=True
            )
            
            print(f"   ✅ mTLS handshake complete")
            print(f"   TLS Version: {secure_socket.version()}")
            
            # Get client certificate
            client_cert = secure_socket.getpeercert()
            if client_cert:
                print(f"   ✅ Client certificate verified")
            
            # Receive message length
            message_length_bytes = secure_socket.recv(4)
            if not message_length_bytes:
                return
            
            message_length = int.from_bytes(message_length_bytes, 'big')
            
            # Receive message
            message_bytes = b""
            while len(message_bytes) < message_length:
                chunk = secure_socket.recv(min(8192, message_length - len(message_bytes)))
                if not chunk:
                    break
                message_bytes += chunk
            
            print(f"   📥 Received {len(message_bytes)} bytes")
            
            # Decode message
            message = json.loads(message_bytes.decode('utf-8'))
            message_type = message.get('type', 'unknown')
            
            print(f"   📨 Message Type: {message_type}")
            
            # Process message
            response = self._process_message(message)
            
            # Send response
            response_json = json.dumps(response)
            response_bytes = response_json.encode('utf-8')
            
            secure_socket.sendall(len(response_bytes).to_bytes(4, 'big'))
            secure_socket.sendall(response_bytes)
            
            print(f"   📤 Sent {len(response_bytes)} bytes")
            print(f"   ✅ Connection handled successfully")
            
            # Close connection
            secure_socket.close()
        
        except Exception as e:
            print(f"   ❌ Error handling client: {e}")
    
    def _process_message(self, message: Dict) -> Dict:
        """Process incoming message"""
        
        message_type = message.get('type', 'unknown')
        
        # Find handler
        handler = self.handlers.get(message_type)
        
        if handler:
            try:
                return handler(message)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Handler error: {str(e)}"
                }
        else:
            return {
                "status": "error",
                "message": f"No handler for message type: {message_type}"
            }
    
    def stop(self):
        """Stop the server"""
        
        print(f"\n🛑 STOPPING mTLS SERVER")
        self.is_running = False
        print(f"   ✅ Server stopped")


if __name__ == "__main__":
    # Example handler
    def handle_test_message(message: Dict) -> Dict:
        return {
            "status": "success",
            "echo": message.get('data', '')
        }
    
    # Create server
    server = MTLSServer(port=8443)
    server.register_handler("test", handle_test_message)
    
    print("✅ mTLS Server ready")
    print("⚠️  Note: Requires actual certificates for production use")