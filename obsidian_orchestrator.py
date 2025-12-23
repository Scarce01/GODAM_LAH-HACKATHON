# ai/obsidian_orchestrator.py
"""
OBSIDIAN AI Orchestrator
Integrates Ollama + Policy Engine + RAG Memory
"""

import subprocess
import json
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from policy_engine import PolicyEngine
from rag_memory import RAGMemory, build_rag_context
from integrated_risk_analyzer import IntegratedRiskAnalyzer


class OBSIDIANOrchestrator:
    """
    Main AI Orchestrator
    
    Three-layer processing:
    1. Layer 1 (Ollama AI): Natural language explanation
    2. Layer 2 (Policy Engine): Deterministic rules
    3. Layer 3 (RAG Memory): Knowledge retrieval
    
    Plus: Integrated Risk Analyzer
    """
    
    def __init__(
        self,
        model_name: str = "obsidian-ai",
        user_policies: Dict = None
    ):
        """
        Initialize orchestrator
        
        Args:
            model_name: Ollama model name
            user_policies: User's policy configuration
        """
        
        self.model_name = model_name
        
        # Initialize components
        self.policy_engine = PolicyEngine(user_policies or {})
        self.rag_memory = RAGMemory()
        self.risk_analyzer = IntegratedRiskAnalyzer()
        
        print(f"\n{'='*70}")
        print(f"🤖 OBSIDIAN AI ORCHESTRATOR INITIALIZED")
        print(f"{'='*70}")
        print(f"   Model: {model_name}")
        print(f"   Policy Engine: Ready")
        print(f"   RAG Memory: Loaded")
        print(f"   Risk Analyzer: Active")
        print(f"{'='*70}\n")
    
    def process_government_request(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process government data access request
        
        Flow:
        1. Risk Analyzer: Calculate trust score
        2. Policy Engine: Evaluate rules
        3. RAG Memory: Build context
        4. Ollama AI: Generate explanation
        
        Args:
            request: Government request dictionary
        
        Returns:
            Complete analysis with AI explanation
        """
        
        print(f"\n{'='*70}")
        print(f"🔍 PROCESSING GOVERNMENT REQUEST")
        print(f"{'='*70}")
        
        request_id = request.get('request_id', 'UNKNOWN')
        agency = request.get('requesting_authority', {}).get('agency_name', 'Unknown')
        
        print(f"   Request ID: {request_id}")
        print(f"   Agency: {agency}")
        
        # STEP 1: Risk Analysis
        print(f"\n[STEP 1] Risk Analyzer...")
        risk_result = self.risk_analyzer.analyze_request(request)
        
        trust_score = risk_result['trust_score']
        risk_level = risk_result['risk_level']
        
        print(f"   Trust Score: {trust_score}/100")
        print(f"   Risk Level: {risk_level}")
        
        # STEP 2: Policy Evaluation
        print(f"\n[STEP 2] Policy Engine...")
        policy_result = self.policy_engine.evaluate_request(request)
        
        print(f"   Decision: {policy_result['decision']}")
        print(f"   Reason: {policy_result['reason']}")
        
        # STEP 3: RAG Context Building
        print(f"\n[STEP 3] RAG Memory...")
        user_id = request.get('target_user_id', '')
        rag_context = build_rag_context(user_id, agency)
        
        print(f"   Context retrieved")
        
        # STEP 4: AI Explanation Generation
        print(f"\n[STEP 4] Ollama AI...")
        ai_explanation = self._generate_ai_explanation(
            request,
            policy_result,
            risk_result,
            rag_context
        )
        
        print(f"   Explanation generated")
        
        # Combine results
        final_response = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "risk_analysis": risk_result,
            "policy_decision": policy_result,
            "ai_explanation": ai_explanation,
            "final_recommendation": self._get_final_recommendation(
                policy_result,
                risk_result
            )
        }
        
        print(f"\n{'='*70}")
        print(f"✅ REQUEST PROCESSING COMPLETE")
        print(f"{'='*70}\n")
        
        return final_response
    
    def _generate_ai_explanation(
        self,
        request: Dict,
        policy_result: Dict,
        risk_result: Dict,
        rag_context: str
    ) -> str:
        """
        Generate AI explanation using Ollama
        
        Args:
            request: Original request
            policy_result: Policy engine result
            risk_result: Risk analyzer result
            rag_context: RAG memory context
        
        Returns:
            AI-generated explanation
        """
        
        # Build comprehensive prompt
        prompt = f"""
You are OBSIDIAN, a Malaysian identity guardian AI helping citizens understand government data requests.

INCOMING REQUEST:
- Request ID: {request.get('request_id')}
- Agency: {request.get('requesting_authority', {}).get('agency_name')}
- Purpose: {request.get('purpose', {}).get('category')}
- Data Requested: {', '.join([ds.get('data_category', '') for ds in request.get('data_sets_requested', [])])}

RISK ANALYSIS:
- Trust Score: {risk_result['trust_score']}/100
- Risk Score: {risk_result['risk_score']}/100
- Risk Level: {risk_result['risk_level']}
- Trust Level: {risk_result['trust_level']}

POLICY DECISION:
- Decision: {policy_result['decision']}
- Reason: {policy_result['reason']}
- Violations: {', '.join(policy_result['violations']) if policy_result['violations'] else 'None'}

{rag_context}

YOUR TASK:
Explain this request to the user in clear, simple language (mix of Bahasa Malaysia and English).

Cover:
1. Who is requesting and why
2. What data they want
3. Trust score and what it means
4. Policy decision and reasoning
5. Your recommendation (APPROVE/DENY/REVIEW)

Use a calm, protective tone. Help the user make an informed decision.

Keep it concise (max 200 words). Start with clear recommendation.
"""
        
        # Call Ollama
        try:
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"[AI explanation unavailable: {result.stderr}]"
        
        except FileNotFoundError:
            return "[AI explanation unavailable: Ollama not installed]"
        except subprocess.TimeoutExpired:
            return "[AI explanation unavailable: Request timed out]"
        except Exception as e:
            return f"[AI explanation unavailable: {str(e)}]"
    
    def _get_final_recommendation(
        self,
        policy_result: Dict,
        risk_result: Dict
    ) -> str:
        """
        Get final recommendation based on all factors
        
        Args:
            policy_result: Policy decision
            risk_result: Risk analysis
        
        Returns:
            Final recommendation
        """
        
        trust_score = risk_result['trust_score']
        risk_score = risk_result['risk_score']
        policy_decision = policy_result['decision']
        
        # If policy denies, always deny
        if policy_decision == "DENY":
            return "DENY"
        
        # If high risk, deny
        if risk_score > 50:
            return "DENY"
        
        # If policy approves and trust high, approve
        if policy_decision == "AUTO_APPROVE" and trust_score >= 75:
            return "AUTO_APPROVE"
        
        # If policy approves but medium trust, manual review
        if policy_decision == "AUTO_APPROVE" and trust_score >= 50:
            return "MANUAL_REVIEW"
        
        # Default: manual review
        return "MANUAL_REVIEW"
    
    def chat(
        self,
        user_question: str,
        context: Dict = None
    ) -> str:
        """
        Interactive chat with AI
        
        Args:
            user_question: User's question
            context: Optional context
        
        Returns:
            AI response
        """
        
        prompt = user_question
        
        if context:
            prompt = f"""
CONTEXT:
{json.dumps(context, indent=2)}

USER QUESTION:
{user_question}

Answer the user's question based on the context provided.
"""
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Chat error: {result.stderr}"
        
        except Exception as e:
            return f"Chat error: {str(e)}"


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 OBSIDIAN AI ORCHESTRATOR TESTING")
    print("="*70)
    
    # Initialize orchestrator
    orchestrator = OBSIDIANOrchestrator()
    
    # Test request 1: Legitimate tax request
    print("\n" + "="*70)
    print("TEST 1: LEGITIMATE TAX REQUEST")
    print("="*70)
    
    tax_request = {
        "request_id": "REQ-2025-TAX001",
        "target_user_id": "900101-01-1234",
        "requesting_authority": {
            "agency_id": "GOV-IRB-0002",
            "agency_name": "Lembaga Hasil Dalam Negeri",
            "officer_id": "IRB-2025-001234"
        },
        "purpose": {
            "category": "Tax_Audit"
        },
        "data_sets_requested": [
            {
                "data_category": "Financial_Records",
                "fields": ["account_balance", "transaction_history_12months"]
            }
        ],
        "retention_period": {
            "duration_days": 2555
        }
    }
    
    result1 = orchestrator.process_government_request(tax_request)
    
    print(f"\n📊 RESULT:")
    print(f"   Trust Score: {result1['risk_analysis']['trust_score']}/100")
    print(f"   Policy Decision: {result1['policy_decision']['decision']}")
    print(f"   Final Recommendation: {result1['final_recommendation']}")
    
    print(f"\n💬 AI EXPLANATION:")
    print(f"   {result1['ai_explanation']}")
    
    # Test request 2: Suspicious request
    print("\n\n" + "="*70)
    print("TEST 2: SUSPICIOUS REQUEST (Unknown Agency)")
    print("="*70)
    
    suspicious_request = {
        "request_id": "REQ-2025-UNK001",
        "target_user_id": "900101-01-1234",
        "requesting_authority": {
            "agency_id": "UNKNOWN-999",
            "agency_name": "Unknown Agency",
            "officer_id": "UNK-001"
        },
        "purpose": {
            "category": "Tax_Audit"
        },
        "data_sets_requested": [
            {
                "data_category": "Financial_Records",
                "fields": ["account_balance"]
            }
        ],
        "retention_period": {
            "duration_days": 365
        }
    }
    
    result2 = orchestrator.process_government_request(suspicious_request)
    
    print(f"\n📊 RESULT:")
    print(f"   Trust Score: {result2['risk_analysis']['trust_score']}/100")
    print(f"   Policy Decision: {result2['policy_decision']['decision']}")
    print(f"   Final Recommendation: {result2['final_recommendation']}")
    
    print(f"\n💬 AI EXPLANATION:")
    print(f"   {result2['ai_explanation']}")
    
    # Test interactive chat
    print("\n\n" + "="*70)
    print("TEST 3: INTERACTIVE CHAT")
    print("="*70)
    
    response = orchestrator.chat(
        "Why was the first request approved?",
        context=result1
    )
    
    print(f"\n💬 AI RESPONSE:")
    print(f"   {response}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE")
    print("="*70)
    print("\n⚠️  Note: AI explanations require Ollama installation")
    print("   Run: ./setup_obsidian.sh to install Ollama + model")
    print("="*70 + "\n")