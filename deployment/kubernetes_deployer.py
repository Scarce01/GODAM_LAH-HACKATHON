# deployment/kubernetes_deployer.py
"""
Kubernetes Deployment Manager
Deploys OBSIDIAN to Kubernetes cluster
"""

import yaml
from typing import Dict, List
from datetime import datetime


class KubernetesDeployer:
    """
    Kubernetes Deployment Manager
    
    Deploys OBSIDIAN with:
    - High availability (3+ replicas)
    - Auto-scaling
    - Load balancing
    - Rolling updates
    - Health checks
    - Resource limits
    """
    
    def __init__(self, namespace: str = "obsidian"):
        """
        Initialize Kubernetes deployer
        
        Args:
            namespace: Kubernetes namespace
        """
        
        self.namespace = namespace
        self.manifests = []
        
        print(f"\n{'='*70}")
        print(f"☸️  Kubernetes Deployer Initialized")
        print(f"{'='*70}")
        print(f"   Namespace: {namespace}")
        print(f"{'='*70}\n")
    
    def generate_namespace(self) -> Dict:
        """Generate namespace manifest"""
        
        return {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.namespace,
                "labels": {
                    "name": self.namespace,
                    "app": "obsidian"
                }
            }
        }
    
    def generate_deployment_api(self) -> Dict:
        """Generate deployment manifest for API"""
        
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "obsidian-user-api",
                "namespace": self.namespace,
                "labels": {
                    "app": "obsidian",
                    "component": "user-api"
                }
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "obsidian",
                        "component": "user-api"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "obsidian",
                            "component": "user-api"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "user-api",
                            "image": "obsidian.registry.my/obsidian-user-api:latest",
                            "ports": [{
                                "containerPort": 5001,
                                "name": "http"
                            }],
                            "env": [
                                {"name": "ENVIRONMENT", "value": "production"},
                                {"name": "LOG_LEVEL", "value": "INFO"}
                            ],
                            "resources": {
                                "requests": {
                                    "memory": "512Mi",
                                    "cpu": "500m"
                                },
                                "limits": {
                                    "memory": "1Gi",
                                    "cpu": "1000m"
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": 5001
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": 5001
                                },
                                "initialDelaySeconds": 10,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
    
    def generate_service_api(self) -> Dict:
        """Generate service manifest for API"""
        
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "obsidian-user-api",
                "namespace": self.namespace,
                "labels": {
                    "app": "obsidian",
                    "component": "user-api"
                }
            },
            "spec": {
                "type": "LoadBalancer",
                "selector": {
                    "app": "obsidian",
                    "component": "user-api"
                },
                "ports": [{
                    "protocol": "TCP",
                    "port": 5001,
                    "targetPort": 5001,
                    "name": "http"
                }]
            }
        }
    
    def generate_statefulset_blockchain(self) -> Dict:
        """Generate StatefulSet for blockchain nodes"""
        
        return {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "obsidian-blockchain",
                "namespace": self.namespace
            },
            "spec": {
                "serviceName": "obsidian-blockchain",
                "replicas": 5,
                "selector": {
                    "matchLabels": {
                        "app": "obsidian",
                        "component": "blockchain"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "obsidian",
                            "component": "blockchain"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "blockchain",
                            "image": "obsidian.registry.my/obsidian-blockchain:latest",
                            "ports": [
                                {"containerPort": 8545, "name": "rpc"},
                                {"containerPort": 30303, "name": "p2p"}
                            ],
                            "volumeMounts": [{
                                "name": "blockchain-data",
                                "mountPath": "/data/blockchain"
                            }],
                            "resources": {
                                "requests": {
                                    "memory": "2Gi",
                                    "cpu": "1000m"
                                },
                                "limits": {
                                    "memory": "4Gi",
                                    "cpu": "2000m"
                                }
                            }
                        }]
                    }
                },
                "volumeClaimTemplates": [{
                    "metadata": {
                        "name": "blockchain-data"
                    },
                    "spec": {
                        "accessModes": ["ReadWriteOnce"],
                        "resources": {
                            "requests": {
                                "storage": "100Gi"
                            }
                        }
                    }
                }]
            }
        }
    
    def generate_hpa(self) -> Dict:
        """Generate HorizontalPodAutoscaler for API"""
        
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": "obsidian-user-api-hpa",
                "namespace": self.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "obsidian-user-api"
                },
                "minReplicas": 3,
                "maxReplicas": 10,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 70
                            }
                        }
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 80
                            }
                        }
                    }
                ]
            }
        }
    
    def generate_ingress(self) -> Dict:
        """Generate Ingress for external access"""
        
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "obsidian-ingress",
                "namespace": self.namespace,
                "annotations": {
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true"
                }
            },
            "spec": {
                "tls": [{
                    "hosts": ["obsidian.my", "api.obsidian.my"],
                    "secretName": "obsidian-tls"
                }],
                "rules": [
                    {
                        "host": "obsidian.my",
                        "http": {
                            "paths": [{
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": "obsidian-user-portal",
                                        "port": {"number": 8000}
                                    }
                                }
                            }]
                        }
                    },
                    {
                        "host": "api.obsidian.my",
                        "http": {
                            "paths": [{
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": "obsidian-user-api",
                                        "port": {"number": 5001}
                                    }
                                }
                            }]
                        }
                    }
                ]
            }
        }
    
    def generate_all_manifests(self) -> List[Dict]:
        """Generate all Kubernetes manifests"""
        
        print(f"\n📝 Generating Kubernetes manifests...")
        
        manifests = [
            self.generate_namespace(),
            self.generate_deployment_api(),
            self.generate_service_api(),
            self.generate_statefulset_blockchain(),
            self.generate_hpa(),
            self.generate_ingress()
        ]
        
        self.manifests = manifests
        
        print(f"✅ Generated {len(manifests)} manifests")
        
        return manifests
    
    def save_manifests(self, output_dir: str = "./k8s") -> bool:
        """
        Save manifests to YAML files
        
        Args:
            output_dir: Output directory
        
        Returns:
            True if successful
        """
        
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n💾 Saving manifests to {output_dir}...")
        
        manifest_names = [
            "namespace.yaml",
            "deployment-api.yaml",
            "service-api.yaml",
            "statefulset-blockchain.yaml",
            "hpa.yaml",
            "ingress.yaml"
        ]
        
        for manifest, name in zip(self.manifests, manifest_names):
            filepath = os.path.join(output_dir, name)
            
            with open(filepath, 'w') as f:
                yaml.dump(manifest, f, default_flow_style=False)
            
            print(f"   Saved: {filepath}")
        
        print(f"✅ All manifests saved")
        
        return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Kubernetes Deployer Testing")
    print("="*70)
    
    deployer = KubernetesDeployer()
    
    # Test 1: Generate manifests
    print("\n[TEST 1] Generate Kubernetes Manifests")
    manifests = deployer.generate_all_manifests()
    if len(manifests) > 0:
        print(f"✅ Test 1 passed - Generated {len(manifests)} manifests")
    
    # Test 2: Save manifests
    print("\n[TEST 2] Save Manifests to Files")
    if deployer.save_manifests("./k8s"):
        print("✅ Test 2 passed")
    
    print("\n✅ Kubernetes Deployer tests complete!")
    print("\nTo deploy to Kubernetes:")
    print("  kubectl apply -f k8s/")