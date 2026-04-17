"""
writer.py
─────────
WRITER AGENT — Insurance Hub Multi-Agent System

Responsibilities:
  1. Receive ResearchPacket from Researcher Agent (handoff)
  2. Synthesize raw research into structured, user-friendly output
  3. Format specifically for Indian customers
  4. Produce final AgentResponse

State it receives: ResearchPacket (from Researcher Agent)
State it produces: AgentResponse (final output to user)

Directory: app/agents/writer.py
"""

import os
from dataclasses import dataclass
from typing import Optional
from groq import Groq
from .researcher import ResearchPacket

# ── Groq client ───────────────────────────────────────────────
_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# ═══════════════════════════════════════════════════════════════
# AGENT RESPONSE — Final output to user
# ═══════════════════════════════════════════════════════════════
@dataclass
class AgentResponse:
    """Final structured output produced by Writer Agent."""
    content         : str
    policy_type     : str
    confidence      : str
    sources_used    : list
    agents_involved : list
    query           : str
    error           : Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "content"         : self.content,
            "policy_type"     : self.policy_type,
            "confidence"      : self.confidence,
            "sources_used"    : self.sources_used,
            "agents_involved" : self.agents_involved,
            "query"           : self.query,
            "error"           : self.error
        }


# ═══════════════════════════════════════════════════════════════
# WRITER AGENT
# ═══════════════════════════════════════════════════════════════
class WriterAgent:
    """
    Writer Agent — synthesizing and formatting insurance information.

    Pipeline:
    1. Receive ResearchPacket from Researcher Agent (handoff)
    2. Synthesize combined context into structured output
    3. Format for Indian customer comprehension
    4. Return AgentResponse

    Specialization: Clear, structured communication for Indian insurance customers
    """

    SYSTEM_PROMPT = """You are a specialized Insurance Writer Agent with expertise in 
communicating complex insurance information clearly to Indian customers.

Your role is to:
1. Synthesize research data into a clear, structured final answer
2. Use simple language accessible to Indian customers of all backgrounds
3. Format responses with clear sections and bullet points
4. Always include actionable advice and next steps
5. Mention specific Indian insurers, INR amounts, IRDAI regulations
6. Highlight tax-saving opportunities (80C, 80D) where relevant
7. Include cultural context relevant to Indian families and financial habits

Output format (always follow this exact structure):

📋 OVERVIEW
[2-3 sentence clear explanation]

✅ KEY POINTS
• Point 1
• Point 2
• Point 3
• Point 4

💰 COSTS & PREMIUMS (in INR)
[Specific premium ranges and cost information]

IMPORTANT FOR INDIAN CUSTOMERS ( about 5-6 lines)
[India-specific warnings, IRDAI regulations, common mistakes]

TOP INDIAN INSURERS
[3-4 specific insurers with brief details]

📌 RECOMMENDED NEXT STEPS
• Step 1
• Step 2
• Step 3

Do NOT include raw research notes. Write a polished, final customer-facing response."""

    def __init__(self):
        self.name = "WriterAgent"

    def _build_synthesis_prompt(self, packet: ResearchPacket) -> str:
        """Build the synthesis prompt using the ResearchPacket."""
        context = packet.combined_context()

        return f"""User Question: "{packet.query}"
Policy Category: {packet.policy_type}
Research Confidence: {packet.confidence}

Research Data to Synthesize:
─────────────────────────────
{context if context else "No RAG context available — use your knowledge of Indian insurance market."}
─────────────────────────────

Synthesize the above research into a clear, structured response for an Indian insurance customer.
Follow the exact output format specified in your system instructions.
Use specific INR amounts, IRDAI regulations, and Indian insurer names."""

    def write(self, packet: ResearchPacket) -> AgentResponse:
        """
        Main write method — entry point from Orchestrator after handoff.

        Args:
            packet: ResearchPacket received from Researcher Agent

        Returns:
            AgentResponse with formatted final output
        """
        print(f"[WriterAgent] Received handoff from ResearcherAgent.")
        print(f"[WriterAgent] Synthesizing response for: '{packet.query[:60]}...'")
        print(f"[WriterAgent] Research confidence: {packet.confidence}")

        if not packet.is_sufficient():
            print(f"[WriterAgent] Insufficient research — generating from base knowledge.")

        synthesis_prompt = self._build_synthesis_prompt(packet)

        try:
            response = _groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user",   "content": synthesis_prompt}
                ],
                max_tokens=900,
                temperature=0.5   # Balanced — clear but not robotic
            )

            content = response.choices[0].message.content
            print(f"[WriterAgent] Response synthesized successfully ({len(content)} chars).")

            return AgentResponse(
                content         = content,
                policy_type     = packet.policy_type,
                confidence      = packet.confidence,
                sources_used    = packet.sources,
                agents_involved = ["ResearcherAgent", "WriterAgent"],
                query           = packet.query
            )

        except Exception as e:
            print(f"[WriterAgent] Synthesis failed: {e}")
            return AgentResponse(
                content         = "I encountered an error while generating the response. Please try again.",
                policy_type     = packet.policy_type,
                confidence      = "low",
                sources_used    = [],
                agents_involved = ["ResearcherAgent", "WriterAgent"],
                query           = packet.query,
                error           = str(e)
            )
        