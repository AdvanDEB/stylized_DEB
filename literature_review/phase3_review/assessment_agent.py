"""Assessment agent for evaluating stylized facts against literature."""

import logging
from typing import Dict, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from literature_review.config import config
from literature_review.phase3_review.rag_retriever import RAGRetriever
from literature_review.phase3_review.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a scientific literature reviewer assessing evidence for Dynamic Energy Budget (DEB) theory statements.

TASK: Assess the literature support for the given stylized fact based ONLY on the provided scientific literature excerpts.

CRITICAL RULES:
1. Base your assessment ONLY on the provided literature - do NOT use your prior knowledge
2. If literature doesn't address the fact, score appropriately low
3. Look for: direct support, indirect support, contradictions, empirical evidence, theoretical backing

SCORING SCALE (1-100):
- 1-20: No evidence or contradictory evidence found
- 21-40: Weak/indirect support, tangential mentions
- 41-60: Moderate support, some direct evidence
- 61-80: Strong support, multiple sources with good evidence
- 81-100: Very strong support, extensive evidence across multiple sources

OUTPUT FORMAT (JSON):
{
  "score": <integer 1-100>,
  "confidence": <"low"|"medium"|"high">,
  "num_supporting_sources": <integer>,
  "num_contradicting_sources": <integer>,
  "key_evidence": "<brief summary, max 200 words>",
  "supporting_papers": ["<filename1>", "<filename2>", ...],
  "contradicting_papers": ["<filename1>", ...] (if any)
}"""

class AssessmentAgent:
    """Agent for assessing stylized facts using RAG + LLM."""
    
    def __init__(self):
        self.retriever = RAGRetriever()
        self.llm = OllamaClient()
    
    def assess_fact(self, fact: Dict) -> Dict:
        """
        Assess a single stylized fact.
        
        Args:
            fact: Dictionary containing fact information
            
        Returns:
            Assessment result dictionary
        """
        fact_number = fact["fact_number"]
        fact_text = fact["fact_text"]
        
        logger.info(f"Assessing fact #{fact_number}: {fact_text[:100]}...")
        
        # Step 1: Retrieve relevant chunks
        relevant_chunks = self.retriever.retrieve(fact_text)
        
        if not relevant_chunks:
            logger.warning(f"No relevant chunks found for fact #{fact_number}")
            return self._default_assessment("No relevant literature found")
        
        # Step 2: Build context from chunks
        context = self._build_context(relevant_chunks)
        
        # Step 3: Create prompt
        prompt = self._create_prompt(fact_number, fact_text, context)
        
        # Step 4: Get LLM assessment
        try:
            assessment = self.llm.generate_json(prompt, SYSTEM_PROMPT)
            
            # Add metadata
            assessment["fact_number"] = fact_number
            assessment["retrieved_chunks_count"] = len(relevant_chunks)
            assessment["top_similarity_score"] = relevant_chunks[0]["similarity_score"] if relevant_chunks else 0
            
            logger.info(f"  Score: {assessment.get('score', 'N/A')}, "
                       f"Confidence: {assessment.get('confidence', 'N/A')}")
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing fact #{fact_number}: {e}")
            return self._default_assessment(f"Error: {str(e)}")
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks."""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            filename = chunk["metadata"].get("filename", "Unknown")
            text = chunk["text"]
            similarity = chunk["similarity_score"]
            
            context_parts.append(
                f"[Document {i}: {filename} (similarity: {similarity:.3f})]\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, fact_number: int, fact_text: str, context: str) -> str:
        """Create prompt for LLM."""
        return f"""STYLIZED FACT #{fact_number}:
"{fact_text}"

RELEVANT LITERATURE EXCERPTS:

{context}

Please assess the literature support for this fact and provide your analysis in JSON format."""
    
    def _default_assessment(self, reason: str) -> Dict:
        """Return default assessment when something goes wrong."""
        return {
            "score": 0,
            "confidence": "low",
            "num_supporting_sources": 0,
            "num_contradicting_sources": 0,
            "key_evidence": reason,
            "supporting_papers": [],
            "contradicting_papers": []
        }
