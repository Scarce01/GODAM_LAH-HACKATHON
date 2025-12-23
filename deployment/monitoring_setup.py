# deployment/monitoring_setup.py
"""
Monitoring Setup
Prometheus + Grafana configuration
"""


class MonitoringSetup:
    """
    Monitoring Setup
    
    Configures:
    - Prometheus metrics collection
    - Grafana dashboards
    - Alert rules
    - Log aggregation
    """
    
    def __init__(self):
        """Initialize monitoring setup"""
        
        print(f"\n{'='*70}")
        print(f"📊 Monitoring Setup Initialized")
        print(f"{'='*70}\n")
    
    def generate_prometheus_config(self) -> str:
        """Generate Prometheus configuration"""
        
        config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/rules/*.yml'

scrape_configs:
  - job_name: 'obsidian-api'
    static_configs:
      - targets:
          - 'api-1:5001'
          - 'api-2:5001'
          - 'api-3:5001'

  - job_name: 'obsidian-blockchain'
    static_configs:
      - targets:
          - 'blockchain-1:8545'
          - 'blockchain-2:8545'
          - 'blockchain-3:8545'
          - 'blockchain-4:8545'
          - 'blockchain-5:8545'

  - job_name: 'obsidian-webapp'
    static_configs:
      - targets:
          - 'webapp-1:8000'
          - 'webapp-2:8000'

  - job_name: 'node-exporter'
    static_configs:
      - targets:
          - 'node-exporter:9100'
"""
        return config
    
    def generate_grafana_dashboard(self) -> dict:
        """Generate Grafana dashboard JSON"""
        
        dashboard = {
            "dashboard": {
                "title": "OBSIDIAN System Dashboard",
                "panels": [
                    {
                        "title": "API Request Rate",
                        "targets": [{
                            "expr": "rate(http_requests_total[5m])"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "title": "Blockchain Block Height",
                        "targets": [{
                            "expr": "blockchain_block_height"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "title": "Storage Usage",
                        "targets": [{
                            "expr": "storage_used_bytes / storage_total_bytes * 100"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "title": "Authentication Success Rate",
                        "targets": [{
                            "expr": "rate(auth_success_total[5m]) / rate(auth_attempts_total[5m]) * 100"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
        
        return dashboard
    
    def generate_alert_rules(self) -> str:
        """Generate Prometheus alert rules"""
        
        rules = """
groups:
  - name: obsidian_alerts
    rules:
      - alert: HighAPILatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency detected"
          description: "95th percentile API latency is above 1 second"

      - alert: BlockchainNodeDown
        expr: up{job="obsidian-blockchain"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Blockchain node is down"
          description: "Node {{ $labels.instance }} is unreachable"

      - alert: StorageAlmostFull
        expr: storage_used_bytes / storage_total_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Storage is almost full"
          description: "Storage usage is above 90%"

      - alert: HighAuthenticationFailureRate
        expr: rate(auth_failure_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High authentication failure rate"
          description: "More than 10 auth failures per second"
"""
        return rules


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Monitoring Setup Testing")
    print("="*70)
    
    monitoring = MonitoringSetup()
    
    # Test: Generate configs
    print("\n[TEST] Generate Monitoring Configs")
    
    prometheus_config = monitoring.generate_prometheus_config()
    grafana_dashboard = monitoring.generate_grafana_dashboard()
    alert_rules = monitoring.generate_alert_rules()
    
    if prometheus_config and grafana_dashboard and alert_rules:
        print("✅ Test passed - All configs generated")
    
    print("\n✅ Monitoring Setup tests complete!")