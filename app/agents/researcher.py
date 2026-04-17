"""
researcher.py
─────────────
RESEARCHER AGENT — Insurance Hub Multi-Agent System

Responsibilities:
  1. Query the RAG knowledge base (ChromaDB) for relevant chunks
  2. If RAG context is insufficient, perform live LLM research
  3. Return structured research data packet for handoff to Writer Agent

State it produces (ResearchPacket):
  - query          : original user question
  - policy_type    : detected policy category
  - rag_context    : retrieved knowledge chunks
  - research_notes : LLM-generated supplementary notes
  - sources        : list of knowledge sources used
  - confidence     : how complete the research is (high/medium/low)

Directory: app/agents/researcher.py
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from groq import Groq

# ── Groq client ───────────────────────────────────────────────
_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# ═══════════════════════════════════════════════════════════════
# DATA PACKET — State passed between agents
# ═══════════════════════════════════════════════════════════════
@dataclass
class ResearchPacket:
    """
    State object passed from Researcher Agent → Writer Agent.
    Contains all information Writer needs to produce a final answer.
    """
    query          : str
    policy_type    : str
    rag_context    : str                    = ""
    research_notes : str                    = ""
    sources        : list                   = field(default_factory=list)
    confidence     : str                    = "low"    # high / medium / low
    error          : Optional[str]          = None

    def is_sufficient(self) -> bool:
        """Check if research is sufficient for Writer Agent."""
        return bool(self.rag_context or self.research_notes)

    def combined_context(self) -> str:
        """Merge RAG + research notes for Writer Agent."""
        parts = []
        if self.rag_context:
            parts.append(f"[RAG Knowledge Base]\n{self.rag_context}")
        if self.research_notes:
            parts.append(f"[Researcher Supplementary Notes]\n{self.research_notes}")
        return "\n\n".join(parts)


# ═══════════════════════════════════════════════════════════════
# RESEARCHER AGENT
# ═══════════════════════════════════════════════════════════════
class ResearcherAgent:
    """
    Researcher Agent — sourcing and gathering insurance information.

    Pipeline:
    1. Detect policy type from query
    2. Query RAG (ChromaDB) for relevant chunks
    3. If RAG insufficient → LLM research fallback
    4. Assess confidence level
    5. Return ResearchPacket for handoff

    Specialization: India-specific insurance market research
    """

    SYSTEM_PROMPT = """You are a specialized Insurance Research Agent with deep expertise 
in the Indian insurance market (IRDAI regulated). Your role is to:

1. Research insurance policy details, coverage, premiums, regulations
2. Focus specifically on Indian insurance products, providers, and regulations  
3. Provide factual, structured research notes
4. Cite specific Indian insurers, premium ranges in INR, IRDAI regulations
5. Always mention IRDAI compliance, Section 80C/80D tax benefits where relevant
6. Analyze bima sugam for more accurate, India-specific information.
7. Take consumer protection and claim settlement ratios into account when mentioning insurers.

Format your research as structured bullet points with clear sections.
Do NOT write a final answer — only provide raw research notes for synthesis by another agent.
Be thorough but factual. If uncertain, state confidence level."""

    def __init__(self):
        self.name = "ResearcherAgent"

    def _detect_policy_type(self, query: str) -> str:
        """Detect policy type from user query."""
        query_lower = query.lower()
        if any(w in query_lower for w in [
            "health", "medical", "hospital", "cashless", "family floater",
            "critical illness", "mediclaim", "ped"
        ]):
            return "Health Insurance"
        elif any(w in query_lower for w in [
            "term", "life", "death", "nominee", "sum assured",
            "claim settlement", "mortality"
        ]):
            return "Term Insurance"
        elif any(w in query_lower for w in [
            "vehicle", "car", "bike", "motor", "ncb", "idv",
            "zero dep", "third party", "own damage", "accident"
        ]):
            return "Vehicle Insurance"
        else:
            return "General Insurance"

    def _query_rag(self, query: str, policy_type: str) -> str:
        """Query RAG knowledge base for relevant context."""
        try:
            from .knowledge_base import retrieve_context
            context = retrieve_context(query, policy_type, n_results=4)
            return context
        except Exception as e:
            print(f"[ResearcherAgent] RAG query failed: {e}")
            return ""

    def _llm_research(self, query: str, policy_type: str, rag_context: str) -> str:
        """
        LLM-based research fallback / supplementation.
        Always runs to add depth beyond what RAG provides.
        """
        rag_info = f"\n\nKnowledge base context available:\n{rag_context}" if rag_context else ""

        prompt = f"""Research task: "{query}"
Policy category: {policy_type}
Indian market focus: Yes
{rag_info}

Provide detailed research notes covering:
1. Direct answer to the query with specifics
2. Relevant Indian regulations (IRDAI rules if applicable)
3. Actual premium ranges in INR from top Indian insurers
4. Key terms and conditions specific to Indian policies
5. Tax implications (80C, 80D, 10D) if relevant
6. Common pitfalls Indian customers should avoid
7. Top 3-5 Indian insurers relevant to this query
8. Consumer guidelines and protection info specific to India.

Format as structured bullet points under clear headings."""

        try:
            response = _groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3   # Low temperature for factual research
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[ResearcherAgent] LLM research failed: {e}")
            return ""

    def _assess_confidence(self, rag_context: str, research_notes: str) -> str:
        """Assess confidence level of research output."""
        rag_words      = len(rag_context.split())      if rag_context      else 0
        research_words = len(research_notes.split())   if research_notes   else 0
        total_words    = rag_words + research_words

        if total_words > 400:
            return "high"
        elif total_words > 150:
            return "medium"
        else:
            return "low"

    def research(self, query: str, policy_type: str = None) -> ResearchPacket:
        """
        Main research method — entry point for Orchestrator.

        Args:
            query:       User's question
            policy_type: Optional override; auto-detected if not provided

        Returns:
            ResearchPacket ready for Writer Agent handoff
        """
        print(f"[ResearcherAgent] Starting research: '{query[:60]}...'")

        # Step 1: Detect policy type
        detected_type = policy_type or self._detect_policy_type(query)
        print(f"[ResearcherAgent] Policy type detected: {detected_type}")

        # Step 2: Query RAG knowledge base
        print(f"[ResearcherAgent] Querying RAG knowledge base...")
        rag_context = self._query_rag(query, detected_type)
        rag_chunks  = len([c for c in rag_context.split("---") if c.strip()]) if rag_context else 0
        print(f"[ResearcherAgent] RAG retrieved {rag_chunks} relevant chunks.")

        # Step 3: LLM supplementary research
        print(f"[ResearcherAgent] Running LLM supplementary research...")
        research_notes = self._llm_research(query, detected_type, rag_context)

        # Step 4: Assess confidence
        confidence = self._assess_confidence(rag_context, research_notes)
        print(f"[ResearcherAgent] Research confidence: {confidence}")

        # Step 5: Build sources list
        sources = []
        if rag_context:
            sources.append("ChromaDB RAG — India Insurance Knowledge Base")
        if research_notes:
            sources.append("Groq Llama 3.3 70B — Supplementary Research")

        # Step 6: Return research packet for Writer Agent
        packet = ResearchPacket(
            query          = query,
            policy_type    = detected_type,
            rag_context    = rag_context,
            research_notes = research_notes,
            sources        = sources,
            confidence     = confidence
        )

        print(f"[ResearcherAgent] Research complete. Handing off to Writer Agent.")
        return packet