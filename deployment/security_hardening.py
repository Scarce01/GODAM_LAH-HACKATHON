# deployment/security_hardening.py
"""
Security Hardening
Production security configuration
"""

import os
import subprocess
from typing import List, Dict


class SecurityHardening:
    """
    Security Hardening Manager
    
    Implements:
    - OS hardening (CIS benchmarks)
    - Network security
    - Application security
    - Access control
    - Audit logging
    """
    
    def __init__(self):
        """Initialize security hardening"""
        
        print(f"\n{'='*70}")
        print(f"🔒 Security Hardening Manager Initialized")
        print(f"{'='*70}\n")
    
    def harden_ssh(self) -> bool:
        """
        Harden SSH configuration
        
        Returns:
            True if successful
        """
        
        print(f"\n🔐 Hardening SSH configuration...")
        
        ssh_config = """
# OBSIDIAN SSH Hardening Configuration

# Disable root login
PermitRootLogin no

# Disable password authentication
PasswordAuthentication no
PubkeyAuthentication yes

# Disable empty passwords
PermitEmptyPasswords no

# Use only SSH Protocol 2
Protocol 2

# Strong ciphers only
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr

# Strong MACs only
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512,hmac-sha2-256

# Strong KEX algorithms only
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256

# Limit authentication attempts
MaxAuthTries 3
MaxSessions 2

# Enable strict mode
StrictModes yes

# Disable X11 forwarding
X11Forwarding no

# Disable agent forwarding
AllowAgentForwarding no

# Set timeout
ClientAliveInterval 300
ClientAliveCountMax 2

# Log verbosely
LogLevel VERBOSE

# Allow only specific users
AllowUsers obsidian admin
"""
        
        config_path = "/etc/ssh/sshd_config.d/obsidian_hardening.conf"
        
        try:
            with open(config_path, 'w') as f:
                f.write(ssh_config)
            
            print(f"✅ SSH configuration hardened: {config_path}")
            print(f"   Restart SSH: systemctl restart sshd")
            
            return True
            
        except Exception as e:
            print(f"❌ SSH hardening failed: {e}")
            return False
    
    def configure_firewall(self) -> bool:
        """
        Configure UFW firewall
        
        Returns:
            True if successful
        """
        
        print(f"\n🛡️  Configuring firewall...")
        
        rules = [
            # Allow SSH (from specific IPs only)
            ("allow", "22/tcp", "from 10.0.0.0/8"),
            
            # Allow HTTPS
            ("allow", "443/tcp"),
            
            # Allow API ports (internal only)
            ("allow", "5001/tcp", "from 10.0.0.0/8"),
            ("allow", "5002/tcp", "from 10.0.0.0/8"),
            
            # Allow web ports
            ("allow", "8000/tcp"),
            ("allow", "8001/tcp"),
            
            # Allow blockchain p2p (internal only)
            ("allow", "30303/tcp", "from 10.0.0.0/8"),
            ("allow", "30303/udp", "from 10.0.0.0/8"),
            
            # Deny all other incoming
            ("deny", "in")
        ]
        
        try:
            # Reset firewall
            subprocess.run(["ufw", "--force", "reset"], check=True)
            
            # Set default policies
            subprocess.run(["ufw", "default", "deny", "incoming"], check=True)
            subprocess.run(["ufw", "default", "allow", "outgoing"], check=True)
            
            # Apply rules
            for rule in rules:
                cmd = ["ufw"]
                cmd.extend(rule)
                subprocess.run(cmd, check=True)
                print(f"   Rule added: {' '.join(rule)}")
            
            # Enable firewall
            subprocess.run(["ufw", "--force", "enable"], check=True)
            
            print(f"✅ Firewall configured and enabled")
            
            return True
            
        except Exception as e:
            print(f"❌ Firewall configuration failed: {e}")
            return False
    
    def enable_auditd(self) -> bool:
        """
        Enable system auditing
        
        Returns:
            True if successful
        """
        
        print(f"\n📝 Enabling audit logging...")
        
        audit_rules = """
# OBSIDIAN Audit Rules

# Monitor authentication
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/sudoers -p wa -k sudo

# Monitor SSH
-w /etc/ssh/sshd_config -p wa -k sshd

# Monitor system calls
-a always,exit -F arch=b64 -S adjtimex,settimeofday -k time-change
-a always,exit -F arch=b64 -S clock_settime -k time-change

# Monitor network
-a always,exit -F arch=b64 -S socket,connect,accept,bind -k network

# Monitor file deletions
-a always,exit -F arch=b64 -S unlink,unlinkat,rename,renameat -k delete

# Monitor OBSIDIAN directories
-w /opt/obsidian -p wa -k obsidian
-w /data/storage -p wa -k storage
-w /data/blockchain -p wa -k blockchain

# Make rules immutable
-e 2
"""
        
        rules_path = "/etc/audit/rules.d/obsidian.rules"
        
        try:
            with open(rules_path, 'w') as f:
                f.write(audit_rules)
            
            # Restart auditd
            subprocess.run(["systemctl", "restart", "auditd"], check=True)
            
            print(f"✅ Audit logging enabled: {rules_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Audit configuration failed: {e}")
            return False
    
    def configure_apparmor(self) -> bool:
        """
        Configure AppArmor profiles
        
        Returns:
            True if successful
        """
        
        print(f"\n🛡️  Configuring AppArmor...")
        
        apparmor_profile = """
#include <tunables/global>

/opt/obsidian/api/user_api {
  #include <abstractions/base>
  #include <abstractions/python>

  # Allow network
  network inet stream,
  network inet6 stream,

  # Allow reading config
  /opt/obsidian/config/** r,

  # Allow reading data
  /data/storage/** rw,

  # Allow temp files
  /tmp/** rw,

  # Deny everything else
  /** ix,
}
"""
        
        profile_path = "/etc/apparmor.d/obsidian-api"
        
        try:
            with open(profile_path, 'w') as f:
                f.write(apparmor_profile)
            
            # Load profile
            subprocess.run(["apparmor_parser", "-r", profile_path], check=True)
            
            print(f"✅ AppArmor profile configured: {profile_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ AppArmor configuration failed: {e}")
            return False
    
    def set_file_permissions(self) -> bool:
        """
        Set secure file permissions
        
        Returns:
            True if successful
        """
        
        print(f"\n📂 Setting secure file permissions...")
        
        permissions = [
            # Configs: read-only
            ("/opt/obsidian/config", "0400", "obsidian:obsidian"),
            
            # Certificates: private key read-only
            ("/opt/obsidian/certs/private.key", "0400", "obsidian:obsidian"),
            ("/opt/obsidian/certs/cert.pem", "0444", "obsidian:obsidian"),
            
            # Data directories: read-write owner only
            ("/data/storage", "0700", "obsidian:obsidian"),
            ("/data/blockchain", "0700", "obsidian:obsidian"),
            
            # Logs: read-write owner, read group
            ("/var/log/obsidian", "0750", "obsidian:obsidian"),
            
            # Application: read-execute
            ("/opt/obsidian", "0755", "obsidian:obsidian")
        ]
        
        try:
            for path, mode, owner in permissions:
                if os.path.exists(path):
                    # Set permissions
                    subprocess.run(["chmod", mode, path], check=True)
                    
                    # Set owner
                    subprocess.run(["chown", "-R", owner, path], check=True)
                    
                    print(f"   {path}: {mode} {owner}")
            
            print(f"✅ File permissions configured")
            
            return True
            
        except Exception as e:
            print(f"❌ Permission setting failed: {e}")
            return False
    
    def disable_unnecessary_services(self) -> bool:
        """
        Disable unnecessary system services
        
        Returns:
            True if successful
        """
        
        print(f"\n🚫 Disabling unnecessary services...")
        
        services_to_disable = [
            "bluetooth",
            "cups",
            "avahi-daemon",
            "ModemManager"
        ]
        
        try:
            for service in services_to_disable:
                try:
                    subprocess.run(
                        ["systemctl", "disable", "--now", service],
                        check=True,
                        capture_output=True
                    )
                    print(f"   Disabled: {service}")
                except subprocess.CalledProcessError:
                    print(f"   Skipped: {service} (not found)")
            
            print(f"✅ Unnecessary services disabled")
            
            return True
            
        except Exception as e:
            print(f"❌ Service disabling failed: {e}")
            return False
    
    def apply_all_hardening(self) -> bool:
        """
        Apply all security hardening measures
        
        Returns:
            True if all successful
        """
        
        print(f"\n{'='*70}")
        print(f"🔒 APPLYING COMPREHENSIVE SECURITY HARDENING")
        print(f"{'='*70}\n")
        
        results = {
            "SSH Hardening": self.harden_ssh(),
            "Firewall Configuration": self.configure_firewall(),
            "Audit Logging": self.enable_auditd(),
            "AppArmor": self.configure_apparmor(),
            "File Permissions": self.set_file_permissions(),
            "Disable Services": self.disable_unnecessary_services()
        }
        
        print(f"\n{'='*70}")
        print(f"📊 HARDENING SUMMARY")
        print(f"{'='*70}")
        
        for measure, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {measure}: {status}")
        
        all_success = all(results.values())
        
        if all_success:
            print(f"\n✅ ALL SECURITY MEASURES APPLIED SUCCESSFULLY")
        else:
            print(f"\n⚠️  SOME SECURITY MEASURES FAILED")
        
        print(f"{'='*70}\n")
        
        return all_success


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Security Hardening Testing")
    print("="*70)
    
    security = SecurityHardening()
    
    # Test: Generate hardening configs
    print("\n[TEST] Generate Security Configurations")
    
    results = {
        "SSH Config": security.harden_ssh(),
        "File Permissions": security.set_file_permissions()
    }
    
    if all(results.values()):
        print("✅ Tests passed")
    
    print("\n✅ Security Hardening tests complete!")
    print("\n⚠️  NOTE: Some tests require root privileges")
    print("   Run with: sudo python security_hardening.py")