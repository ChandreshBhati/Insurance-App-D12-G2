"""
orchestrator.py
───────────────
ORCHESTRATOR — Insurance Hub Multi-Agent System

Manages the complete agent workflow:
  1. Receives user query
  2. Invokes Researcher Agent
  3. Validates research output (handoff gate)
  4. Invokes Writer Agent with ResearchPacket
  5. Returns final AgentResponse

Handoff Protocol:
  ResearcherAgent ──(ResearchPacket)──► WriterAgent ──(AgentResponse)──► User

State Management:
  - AgentState tracks progress through the pipeline
  - Each stage logs its status for transparency
  - Failed stages fall back gracefully

Directory: app/agents/orchestrator.py
"""

import time
from dataclasses import dataclass, field
from typing import Optional
from .researcher import ResearcherAgent, ResearchPacket
from .writer     import WriterAgent, AgentResponse


# ═══════════════════════════════════════════════════════════════
# AGENT STATE — tracks pipeline execution
# ═══════════════════════════════════════════════════════════════
@dataclass
class AgentState:
    """
    Tracks state throughout the multi-agent pipeline.
    Provides transparency on what each agent did.
    """
    query           : str
    policy_type     : str                = ""
    stage           : str                = "init"
    start_time      : float              = field(default_factory=time.time)
    researcher_done : bool               = False
    writer_done     : bool               = False
    research_packet : Optional[ResearchPacket] = None
    final_response  : Optional[AgentResponse]  = None
    error           : Optional[str]            = None
    logs            : list               = field(default_factory=list)

    def log(self, message: str):
        """Add timestamped log entry."""
        elapsed = round(time.time() - self.start_time, 2)
        self.logs.append(f"[{elapsed}s] {message}")
        print(f"[Orchestrator] {message}")

    def elapsed(self) -> float:
        return round(time.time() - self.start_time, 2)


# ═══════════════════════════════════════════════════════════════
# ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════
class InsuranceOrchestrator:
    """
    Orchestrates the Researcher → Writer agent pipeline.

    Design:
    - Sequential pipeline (Researcher then Writer)
    - Handoff gate validates research before Writer receives it
    - Full state tracking for transparency
    - Graceful degradation if any agent fails

    Usage:
        orchestrator = InsuranceOrchestrator()
        result = orchestrator.run("What is cashless hospitalization?", "Health Insurance")
    """

    def __init__(self):
        self.researcher = ResearcherAgent()
        self.writer     = WriterAgent()

    def _validate_handoff(self, state: AgentState) -> bool:
        """
        Handoff Gate — validates research before passing to Writer.
        Returns True if research is sufficient for Writer to proceed.
        """
        packet = state.research_packet

        if packet is None:
            state.log("HANDOFF GATE: FAILED — No research packet produced.")
            return False

        if packet.error:
            state.log(f"HANDOFF GATE: WARNING — Research has error: {packet.error}")
            # Still proceed — Writer can work with partial data

        if not packet.is_sufficient():
            state.log("HANDOFF GATE: WARNING — Research insufficient; Writer will use base knowledge.")
            # Still proceed with empty context

        state.log(
            f"HANDOFF GATE: PASSED — "
            f"RAG chunks: {'yes' if packet.rag_context else 'no'}, "
            f"Research notes: {'yes' if packet.research_notes else 'no'}, "
            f"Confidence: {packet.confidence}"
        )
        return True

    def run(self, query: str, policy_type: str = None) -> dict:
        """
        Execute the full agent pipeline.

        Args:
            query:       User's insurance question
            policy_type: Optional policy type hint

        Returns:
            dict with content, metadata, pipeline info
        """
        # ── Initialize state ──────────────────────────────────
        state = AgentState(query=query, policy_type=policy_type or "")
        state.log(f"Pipeline started for query: '{query[:80]}'")

        # ── Stage 1: Researcher Agent ─────────────────────────
        state.stage = "researching"
        state.log("Stage 1: Invoking ResearcherAgent...")

        try:
            research_packet        = self.researcher.research(query, policy_type)
            state.research_packet  = research_packet
            state.policy_type      = research_packet.policy_type
            state.researcher_done  = True
            state.log(
                f"ResearcherAgent complete. "
                f"Policy type: {research_packet.policy_type}. "
                f"Confidence: {research_packet.confidence}."
            )
        except Exception as e:
            state.error = str(e)
            state.log(f"ResearcherAgent FAILED: {e}")
            # Create minimal packet so Writer can still attempt
            from .researcher import ResearchPacket
            state.research_packet = ResearchPacket(
                query       = query,
                policy_type = policy_type or "General Insurance",
                error       = str(e)
            )

        # ── Handoff Gate ──────────────────────────────────────
        state.stage = "handoff"
        handoff_ok  = self._validate_handoff(state)

        # ── Stage 2: Writer Agent ─────────────────────────────
        state.stage = "writing"
        state.log("Stage 2: Invoking WriterAgent (handoff received)...")

        try:
            final_response     = self.writer.write(state.research_packet)
            state.final_response = final_response
            state.writer_done  = True
            state.log(
                f"WriterAgent complete. "
                f"Response length: {len(final_response.content)} chars."
            )
        except Exception as e:
            state.error = str(e)
            state.log(f"WriterAgent FAILED: {e}")
            from .writer import AgentResponse
            state.final_response = AgentResponse(
                content         = f"I encountered an error generating your response: {str(e)}",
                policy_type     = state.policy_type or "General Insurance",
                confidence      = "low",
                sources_used    = [],
                agents_involved = ["ResearcherAgent", "WriterAgent"],
                query           = query,
                error           = str(e)
            )

        # ── Finalize ──────────────────────────────────────────
        state.stage = "complete"
        total_time  = state.elapsed()
        state.log(f"Pipeline complete in {total_time}s.")

        response = state.final_response

        return {
            "content"         : response.content,
            "policy_type"     : response.policy_type,
            "confidence"      : response.confidence,
            "sources_used"    : response.sources_used,
            "agents_involved" : response.agents_involved,
            "pipeline_logs"   : state.logs,
            "total_time_s"    : total_time,
            "researcher_done" : state.researcher_done,
            "writer_done"     : state.writer_done,
            "query"           : query,
            "error"           : response.error
        }


# ── Singleton instance ────────────────────────────────────────
_orchestrator = None

def get_orchestrator() -> InsuranceOrchestrator:
    """Return singleton orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = InsuranceOrchestrator()
    return _orchestrator