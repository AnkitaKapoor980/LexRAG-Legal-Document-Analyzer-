"""
Q&A Agent - Answers legal questions using RAG.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional

from ..llm_client import get_llm_client
from ..retriever import get_retriever
from ..prompts.templates import QA_PROMPT

logger = logging.getLogger(__name__)


class QAAgent:
    """Answers legal questions using RAG retrieval."""

    def __init__(self, top_k: int = 5):
        """
        Initialize Q&A Agent.

        Args:
            top_k: Number of context chunks to retrieve
        """
        self.llm = get_llm_client(purpose="qa")
        self.retriever = get_retriever(top_k=top_k)
        self.conversation_history: List[Dict[str, str]] = []

    def answer(
        self,
        question: str,
        use_history: bool = True,
        clear_history: bool = False,
    ) -> Dict[str, Any]:
        """
        Answer a legal question using LLM.

        Args:
            question: The question to answer
            use_history: Whether to use conversation history
            clear_history: Whether to clear conversation history first

        Returns:
            Answer with sources and confidence
        """
        if clear_history:
            self.conversation_history = []

        if not question or not question.strip():
            return {
                "answer": "Please provide a valid question.",
                "sources": [],
                "confidence": "low",
                "notes": "Empty question provided",
            }

        # Build context with history if enabled
        context = ""
        if use_history and self.conversation_history:
            history_text = "\n".join([
                f"Q: {h['question']}\nA: {h['answer']}"
                for h in self.conversation_history[-3:]  # Last 3 exchanges
            ])
            context = f"Previous conversation:\n{history_text}\n\n"

        # Use LLM to generate answer (without RAG retrieval)
        try:
            result = self._answer_with_llm_simple(question, context)

            # Update conversation history
            if use_history:
                self.conversation_history.append({
                    "question": question,
                    "answer": result["answer"],
                })

            return result
        except Exception as e:
            logger.error(f"LLM Q&A failed: {e}")
            return {
                "answer": "I encountered an error processing your question. Please try again.",
                "sources": [],
                "confidence": "low",
                "notes": f"Error: {str(e)}",
            }

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def _answer_with_llm(self, question: str, legal_context: str) -> Dict[str, Any]:
        """Generate answer using LLM with RAG context."""
        prompt = QA_PROMPT.format(
            question=question,
            legal_context=legal_context or "No relevant legal context found.",
        )

        response = self.llm.invoke(prompt)

        # Parse JSON response
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                result = json.loads(response)

            # Validate confidence
            confidence = result.get("confidence", "medium").lower()
            if confidence not in ["high", "medium", "low"]:
                confidence = "medium"

            return {
                "answer": result.get("answer", "Unable to generate answer."),
                "sources": result.get("sources", []),
                "confidence": confidence,
                "notes": result.get("notes", ""),
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}\nResponse: {response[:200]}")
            return {
                "answer": "I encountered an error processing your question. Please try rephrasing it.",
                "sources": [],
                "confidence": "low",
                "notes": "Error in response parsing",
            }

    def _answer_with_llm_simple(self, question: str, conversation_context: str = "") -> Dict[str, Any]:
        """Generate answer using LLM without RAG (simple chatbot mode)."""
        
        # Simple prompt for general legal questions
        prompt = f"""You are a helpful legal assistant specializing in Indian law. Answer the user's question clearly and concisely.

{conversation_context}Current question: {question}

Provide a helpful answer about Indian law, legal concepts, or general legal advice. If the question is about signing a contract or making legal decisions, advise consulting with a qualified lawyer.

Answer the question directly and conversationally. Be helpful and informative."""

        response = self.llm.invoke(prompt)
        
        # Return simple response (no JSON parsing needed)
        return {
            "answer": response.strip(),
            "sources": [],
            "confidence": "medium",
            "notes": "General legal information - consult a lawyer for specific advice",
        }

    def _answer_with_heuristic(
        self, question: str, legal_context_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback heuristic answer."""
        citations = self.retriever.get_citations(legal_context_results)
        return {
            "answer": f"I found {len(legal_context_results)} relevant legal documents, but detailed analysis is unavailable. "
                     f"Please review the retrieved sources manually.",
            "sources": citations,
            "confidence": "low",
            "notes": "Heuristic-based answer (detailed analysis unavailable)",
        }

