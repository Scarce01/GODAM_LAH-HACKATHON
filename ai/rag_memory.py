# ai/rag_memory.py
"""
RAG Memory (Layer 3)
Retrieval-Augmented Generation with Malaysian law knowledge
"""

from typing import Dict, List, Optional


class RAGMemory:
    """
    RAG Memory System
    
    Stores:
    - Malaysian laws (PDPA, Medical Practice Act, etc.)
    - Government agency registry
    - User consent preferences
    - Past approval history
    """
    
    def __init__(self):
        """Initialize RAG memory with Malaysian knowledge base"""
        
        self.laws = self._load_malaysian_laws()
        self.authorities = self._load_authority_registry()
        self.user_policies = {}
        self.past_approvals = {}
        
        print(f"📚 RAG Memory initialized")
        print(f"   Laws loaded: {len(self.laws)}")
        print(f"   Authorities: {len(self.authorities)}")
    
    def _load_malaysian_laws(self) -> Dict:
        """Load Malaysian law database"""
        
        return {
            "pdpa_2010": {
                "title": "Personal Data Protection Act 2010",
                "jurisdiction": "Malaysia",
                "relevant_sections": {
                    "section_6": "Processing of personal data",
                    "section_40": "Consent requirements for sensitive data"
                },
                "url": "https://www.pdp.gov.my"
            },
            "medical_practice_act_1971": {
                "title": "Medical Practice Act 1971",
                "jurisdiction": "Malaysia",
                "relevant_sections": {
                    "section_19": "Medical records access and confidentiality",
                    "section_27": "Penalties for unauthorized disclosure"
                }
            },
            "income_tax_act_1967": {
                "title": "Income Tax Act 1967",
                "jurisdiction": "Malaysia",
                "relevant_sections": {
                    "section_138": "Secrecy provisions",
                    "section_139": "Permitted disclosures"
                }
            }
        }
    
    def _load_authority_registry(self) -> Dict:
        """Load government authority registry"""
        
        return {
            "medical": [
                {
                    "name": "Hospital Kuala Lumpur",
                    "short_name": "Hospital_KL",
                    "trust_level": "HIGH",
                    "verification": "PKI Certificate"
                },
                {
                    "name": "Kementerian Kesihatan Malaysia",
                    "short_name": "KKM",
                    "trust_level": "HIGHEST",
                    "verification": "Government PKI"
                }
            ],
            "financial": [
                {
                    "name": "Lembaga Hasil Dalam Negeri",
                    "short_name": "LHDN",
                    "trust_level": "HIGHEST",
                    "verification": "Government PKI"
                },
                {
                    "name": "Bank Negara Malaysia",
                    "short_name": "Bank_Negara",
                    "trust_level": "HIGHEST",
                    "verification": "Government PKI"
                }
            ],
            "government": [
                {
                    "name": "Jabatan Pendaftaran Negara",
                    "short_name": "JPN",
                    "trust_level": "HIGHEST",
                    "verification": "Master Registry"
                }
            ]
        }
    
    def query_law(self, law_id: str) -> Optional[Dict]:
        """Query law database"""
        return self.laws.get(law_id)
    
    def query_authority(self, authority_name: str) -> Optional[Dict]:
        """Query authority registry"""
        
        for category, authorities in self.authorities.items():
            for auth in authorities:
                if (auth.get('name') == authority_name or 
                    auth.get('short_name') == authority_name):
                    return auth
        
        return None
    
    def add_user_policy(self, user_id: str, policy: Dict):
        """Store user policy preferences"""
        self.user_policies[user_id] = policy
    
    def add_approval_record(self, user_id: str, record: Dict):
        """Store approval history"""
        
        if user_id not in self.past_approvals:
            self.past_approvals[user_id] = []
        
        self.past_approvals[user_id].append(record)


def build_rag_context(user_id: str, authority_name: str) -> str:
    """
    Build RAG context for AI prompt injection
    
    Args:
        user_id: User identifier
        authority_name: Requesting authority
    
    Returns:
        Formatted context string
    """
    
    memory = RAGMemory()
    
    # Get authority info
    authority_info = memory.query_authority(authority_name)
    
    # Build context
    context = f"""
RETRIEVED CONTEXT (RAG Layer 3):

AUTHORITY INFORMATION:
- Name: {authority_info['name'] if authority_info else 'Unknown'}
- Trust Level: {authority_info['trust_level'] if authority_info else 'UNVERIFIED'}
- Verification: {authority_info['verification'] if authority_info else 'None'}

APPLICABLE LAWS:
- Personal Data Protection Act 2010 (Section 40: Consent for sensitive data)
- Medical Practice Act 1971 (Section 19: Medical records access)
- Income Tax Act 1967 (Section 138-139: Tax data secrecy)

USER PREFERENCES:
- Auto-approve trusted hospitals: Yes
- Max auto-risk threshold: 20/100
- Geographic restriction: Malaysia only
"""
    
    return context


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 RAG MEMORY TESTING")
    print("="*70)
    
    memory = RAGMemory()
    
    # Test 1: Query law
    print("\nTEST 1: Query Malaysian Law")
    pdpa = memory.query_law("pdpa_2010")
    if pdpa:
        print(f"   ✅ Law: {pdpa['title']}")
        print(f"   Sections: {len(pdpa['relevant_sections'])}")
    
    # Test 2: Query authority
    print("\nTEST 2: Query Government Authority")
    lhdn = memory.query_authority("LHDN")
    if lhdn:
        print(f"   ✅ Authority: {lhdn['name']}")
        print(f"   Trust Level: {lhdn['trust_level']}")
    
    # Test 3: Build context
    print("\nTEST 3: Build RAG Context")
    context = build_rag_context("user-123", "LHDN")
    print(f"   ✅ Context built ({len(context)} chars)")
    print(f"\n{context}")
    
    print("\n✅ RAG Memory tests complete")