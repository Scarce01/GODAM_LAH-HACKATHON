# deployment/ansible_playbook.py
"""
Ansible Playbook Generator
Automated server provisioning and configuration
"""

import yaml
from typing import Dict, List


class AnsiblePlaybook:
    """
    Ansible Playbook Generator
    
    Automates:
    - Server provisioning
    - Dependency installation
    - Security hardening
    - Service configuration
    - Monitoring setup
    """
    
    def __init__(self):
        """Initialize Ansible playbook generator"""
        
        print(f"\n{'='*70}")
        print(f"📜 Ansible Playbook Generator Initialized")
        print(f"{'='*70}\n")
    
    def generate_inventory(self) -> str:
        """Generate Ansible inventory"""
        
        inventory = """
[api_servers]
api-1 ansible_host=10.0.1.10
api-2 ansible_host=10.0.1.11
api-3 ansible_host=10.0.1.12

[webapp_servers]
webapp-1 ansible_host=10.0.2.10
webapp-2 ansible_host=10.0.2.11

[blockchain_nodes]
blockchain-1 ansible_host=10.0.3.10
blockchain-2 ansible_host=10.0.3.11
blockchain-3 ansible_host=10.0.3.12
blockchain-4 ansible_host=10.0.3.13
blockchain-5 ansible_host=10.0.3.14

[storage_servers]
storage-1 ansible_host=10.0.4.10
storage-2 ansible_host=10.0.4.11
storage-3 ansible_host=10.0.4.12

[all:vars]
ansible_user=obsidian
ansible_ssh_private_key_file=~/.ssh/obsidian.pem
ansible_python_interpreter=/usr/bin/python3
"""
        return inventory
    
    def generate_main_playbook(self) -> Dict:
        """Generate main playbook"""
        
        playbook = [{
            "name": "OBSIDIAN Infrastructure Setup",
            "hosts": "all",
            "become": True,
            "vars": {
                "obsidian_version": "2.0.0",
                "python_version": "3.11",
                "docker_version": "24.0"
            },
            "tasks": [
                {
                    "name": "Update apt cache",
                    "apt": {
                        "update_cache": True,
                        "cache_valid_time": 3600
                    }
                },
                {
                    "name": "Install system dependencies",
                    "apt": {
                        "name": [
                            "python3",
                            "python3-pip",
                            "docker.io",
                            "nginx",
                            "postgresql-client",
                            "redis-tools",
                            "ufw"
                        ],
                        "state": "present"
                    }
                },
                {
                    "name": "Configure firewall",
                    "ufw": {
                        "rule": "allow",
                        "port": "{{ item }}",
                        "proto": "tcp"
                    },
                    "loop": ["22", "80", "443", "5001", "5002", "8000"]
                },
                {
                    "name": "Enable firewall",
                    "ufw": {
                        "state": "enabled"
                    }
                },
                {
                    "name": "Create obsidian user",
                    "user": {
                        "name": "obsidian",
                        "shell": "/bin/bash",
                        "groups": ["docker"],
                        "append": True
                    }
                },
                {
                    "name": "Create application directories",
                    "file": {
                        "path": "{{ item }}",
                        "state": "directory",
                        "owner": "obsidian",
                        "group": "obsidian",
                        "mode": "0755"
                    },
                    "loop": [
                        "/opt/obsidian",
                        "/data/storage",
                        "/data/blockchain",
                        "/var/log/obsidian"
                    ]
                },
                {
                    "name": "Deploy application code",
                    "copy": {
                        "src": "../",
                        "dest": "/opt/obsidian/",
                        "owner": "obsidian",
                        "group": "obsidian"
                    }
                },
                {
                    "name": "Install Python dependencies",
                    "pip": {
                        "requirements": "/opt/obsidian/requirements.txt",
                        "executable": "pip3"
                    }
                },
                {
                    "name": "Start OBSIDIAN services",
                    "systemd": {
                        "name": "obsidian-{{ item }}",
                        "state": "started",
                        "enabled": True
                    },
                    "loop": ["api", "webapp", "blockchain"]
                }
            ]
        }]
        
        return playbook
    
    def generate_security_playbook(self) -> Dict:
        """Generate security hardening playbook"""
        
        playbook = [{
            "name": "OBSIDIAN Security Hardening",
            "hosts": "all",
            "become": True,
            "tasks": [
                {
                    "name": "Disable root login",
                    "lineinfile": {
                        "path": "/etc/ssh/sshd_config",
                        "regexp": "^PermitRootLogin",
                        "line": "PermitRootLogin no"
                    }
                },
                {
                    "name": "Disable password authentication",
                    "lineinfile": {
                        "path": "/etc/ssh/sshd_config",
                        "regexp": "^PasswordAuthentication",
                        "line": "PasswordAuthentication no"
                    }
                },
                {
                    "name": "Configure fail2ban",
                    "apt": {
                        "name": "fail2ban",
                        "state": "present"
                    }
                },
                {
                    "name": "Enable automatic security updates",
                    "apt": {
                        "name": "unattended-upgrades",
                        "state": "present"
                    }
                },
                {
                    "name": "Set secure file permissions",
                    "file": {
                        "path": "{{ item }}",
                        "mode": "0600"
                    },
                    "loop": [
                        "/opt/obsidian/config/secrets.yml",
                        "/opt/obsidian/certs/private.key"
                    ]
                }
            ]
        }]
        
        return playbook
    
    def save_playbooks(self, output_dir: str = "./ansible") -> bool:
        """Save playbooks to files"""
        
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n💾 Saving Ansible playbooks to {output_dir}...")
        
        # Save inventory
        with open(os.path.join(output_dir, "inventory.ini"), 'w') as f:
            f.write(self.generate_inventory())
        print(f"   Saved: inventory.ini")
        
        # Save main playbook
        with open(os.path.join(output_dir, "main.yml"), 'w') as f:
            yaml.dump(self.generate_main_playbook(), f, default_flow_style=False)
        print(f"   Saved: main.yml")
        
        # Save security playbook
        with open(os.path.join(output_dir, "security.yml"), 'w') as f:
            yaml.dump(self.generate_security_playbook(), f, default_flow_style=False)
        print(f"   Saved: security.yml")
        
        print(f"✅ All playbooks saved")
        
        return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Ansible Playbook Testing")
    print("="*70)
    
    ansible = AnsiblePlaybook()
    
    # Test: Generate and save playbooks
    print("\n[TEST] Generate and Save Playbooks")
    if ansible.save_playbooks("./ansible"):
        print("✅ Test passed")
    
    print("\n✅ Ansible Playbook tests complete!")
    print("\nTo run playbooks:")
    print("  ansible-playbook -i ansible/inventory.ini ansible/main.yml")