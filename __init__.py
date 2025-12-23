# ai/__init__.py
"""
OBSIDIAN AI Module
Three-layer AI architecture: Ollama + Policy Engine + RAG Memory

Components:
- obsidian_main: Main AI orchestrator
- policy_engine: Deterministic rule evaluation
- rag_memory: Malaysian law knowledge base
- risk_analyzer: Integrated risk scoring

Author: OBSIDIAN Team
Version: 2.0 (Iron Vault - Enhanced AI)
"""

__version__ = "2.0.0"
__author__ = "OBSIDIAN Team"

from .obsidian_orchestrator import OBSIDIANOrchestrator
from .policy_engine import PolicyEngine
from .rag_memory import RAGMemory, build_rag_context
from .integrated_risk_analyzer import IntegratedRiskAnalyzer

__all__ = [
    'OBSIDIANOrchestrator',
    'PolicyEngine',
    'RAGMemory',
    'build_rag_context',
    'IntegratedRiskAnalyzer'
]

# AI configuration
AI_CONFIG = {
    "ollama": {
        "model": "obsidian-ai",
        "base_model": "llama3.2",
        "temperature": 0.7,
        "max_tokens": 1000,
        "timeout": 30
    },
    "policy_engine": {
        "mode": "deterministic",
        "default_action": "deny",
        "require_explicit_consent": True
    },
    "rag_memory": {
        "knowledge_base": "malaysian_laws",
        "embedding_model": "sentence-transformers",
        "chunk_size": 512
    },
    "risk_analyzer": {
        "enabled": True,
        "min_trust_score": 50,
        "sector_weights": {
            "financial": 0.35,
            "healthcare": 0.25,
            "government": 0.40
        }
    }
}

print(f"🤖 OBSIDIAN AI Module v{__version__} loaded")
print(f"   Layer 1: Ollama ({AI_CONFIG['ollama']['model']})")
print(f"   Layer 2: Policy Engine (Deterministic)")
print(f"   Layer 3: RAG Memory (Malaysian Laws)")
print(f"   Risk Analyzer: Enabled")