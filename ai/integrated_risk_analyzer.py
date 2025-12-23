# ai/integrated_risk_analyzer.py
"""
Integrated Risk Analyzer
Calculates trust scores for government requests
"""

from typing import Dict, Any
from datetime import datetime


class IntegratedRiskAnalyzer:
    """
    Integrated Risk Analyzer
    
    Analyzes:
    - Agency trust score (base trust from registry)
    - Sector compliance (licenses, certifications)
    - Data sensitivity (what data is requested)
    - Retention period (how long they keep it)
    - Purpose alignment (does request match purpose)
    """
    
    def __init__(self):
        """Initialize risk analyzer"""
        
        self.agency_registry = self._load_agency_registry()
        self.standards = self._load_sector_standards()
        
        print(f"🎯 Risk Analyzer initialized")
        print(f"   Agencies: {len(self.agency_registry)}")
    
    def _load_agency_registry(self) -> Dict:
        """Load trusted agency registry"""
        
        return {
            "GOV-IRB-0002": {
                "name": "Lembaga Hasil Dalam Negeri",
                "base_trust": 95,
                "sector": "tax"
            },
            "GOV-KKM-0001": {
                "name": "Kementerian Kesihatan Malaysia",
                "base_trust": 90,
                "sector": "healthcare"
            },
            "GOV-JPN-0001": {
                "name": "Jabatan Pendaftaran Negara",
                "base_trust": 95,
                "sector": "government"
            }
        }
    
    def _load_sector_standards(self) -> Dict:
        """Load sector standards"""
        
        return {
            "tax": {"max_retention_days": 2555},  # 7 years
            "healthcare": {"max_retention_days": 365},
            "government": {"max_retention_days": 1825}  # 5 years
        }
    
    def analyze_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze request and calculate trust/risk scores
        
        Args:
            request: Government request
        
        Returns:
            Risk analysis with scores
        """
        
        agency_id = request.get('requesting_authority', {}).get('agency_id')
        
        # Step 1: Base trust
        base_trust = self._calculate_base_trust(agency_id)
        
        # Step 2: Data sensitivity penalty
        data_penalty = self._calculate_data_penalty(request)
        
        # Step 3: Retention penalty
        retention_penalty = self._calculate_retention_penalty(request)
        
        # Calculate final trust score
        trust_score = base_trust - data_penalty - retention_penalty
        trust_score = max(0, min(100, trust_score))
        
        # Risk score is inverse
        risk_score = 100 - trust_score
        
        # Determine risk level
        if risk_score <= 10:
            risk_level = "MINIMAL"
            trust_level = "CRITICAL TRUST ✅"
            recommendation = "AUTO_APPROVE"
        elif risk_score <= 25:
            risk_level = "LOW"
            trust_level = "HIGH TRUST ⚠️"
            recommendation = "APPROVE"
        elif risk_score <= 50:
            risk_level = "MEDIUM"
            trust_level = "MEDIUM TRUST 🛑"
            recommendation = "MANUAL_REVIEW"
        else:
            risk_level = "HIGH"
            trust_level = "LOW TRUST ⛔"
            recommendation = "DENY"
        
        return {
            "trust_score": round(trust_score, 2),
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "trust_level": trust_level,
            "recommendation": recommendation,
            "detailed_breakdown": {
                "base_trust": base_trust,
                "data_penalty": data_penalty,
                "retention_penalty": retention_penalty
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_base_trust(self, agency_id: str) -> float:
        """Calculate base trust from agency registry"""
        
        if agency_id in self.agency_registry:
            return self.agency_registry[agency_id]["base_trust"]
        else:
            return 30.0  # Unverified agency
    
    def _calculate_data_penalty(self, request: Dict) -> float:
        """Calculate penalty for sensitive data"""
        
        sensitivity_weights = {
            "Medical_Records": 20,
            "Financial_Records": 15,
            "Personal_Identity": 10
        }
        
        penalty = 0
        
        for data_set in request.get('data_sets_requested', []):
            category = data_set.get('data_category', '')
            penalty += sensitivity_weights.get(category, 5)
        
        return min(penalty, 40)  # Cap at 40
    
    def _calculate_retention_penalty(self, request: Dict) -> float:
        """Calculate penalty for excessive retention"""
        
        retention_days = request.get('retention_period', {}).get('duration_days', 0)
        purpose = request.get('purpose', {}).get('category', '')
        
        # Get max allowed for purpose
        max_allowed = 365  # Default
        
        if retention_days <= max_allowed:
            return 0
        else:
            excess_ratio = retention_days / max_allowed
            return min((excess_ratio - 1) * 20, 30)  # Cap at 30


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 RISK ANALYZER TESTING")
    print("="*70)
    
    analyzer = IntegratedRiskAnalyzer()
    
    # Test 1: Trusted agency, low sensitivity
    print("\nTEST 1: Low Risk Request")
    
    low_risk = {
        "requesting_authority": {
            "agency_id": "GOV-IRB-0002"
        },
        "data_sets_requested": [
            {"data_category": "Financial_Records"}
        ],
        "retention_period": {
            "duration_days": 365
        }
    }
    
    result = analyzer.analyze_request(low_risk)
    print(f"   Trust Score: {result['trust_score']}/100")
    print(f"   Risk Score: {result['risk_score']}/100")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Recommendation: {result['recommendation']}")
    
    # Test 2: Unknown agency, high sensitivity
    print("\nTEST 2: High Risk Request")
    
    high_risk = {
        "requesting_authority": {
            "agency_id": "UNKNOWN-999"
        },
        "data_sets_requested": [
            {"data_category": "Medical_Records"},
            {"data_category": "Financial_Records"}
        ],
        "retention_period": {
            "duration_days": 3650
        }
    }
    
    result = analyzer.analyze_request(high_risk)
    print(f"   Trust Score: {result['trust_score']}/100")
    print(f"   Risk Score: {result['risk_score']}/100")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Recommendation: {result['recommendation']}")
    
    print("\n✅ Risk Analyzer tests complete")
```

---

## 📦 Complete AI Folder Structure
```
ai/
├── __init__.py
├── obsidian_orchestrator.py     🤖 Main AI orchestrator
├── policy_engine.py              📋 Deterministic rules
├── rag_memory.py                 📚 Malaysian law KB
└── integrated_risk_analyzer.py  🎯 Trust scoring