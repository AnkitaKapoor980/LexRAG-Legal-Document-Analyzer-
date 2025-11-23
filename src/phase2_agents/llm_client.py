"""
LLM Client abstraction for Groq/HuggingFace APIs.
"""

import os
import time
import logging
from typing import Optional
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Rate limiting configuration
# Groq free tier: ~30 requests per minute
# Add delays to prevent hitting rate limits
REQUEST_DELAY = 2.5  # 2.5 second delay between requests (30 req/min = 2 sec/req, adding buffer)
_last_request_time = 0


class LLMClient:
    """Unified LLM client supporting Groq and HuggingFace."""

    def __init__(
        self,
        provider: str = "groq",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.1,
    ):
        """
        Initialize LLM client.

        Args:
            provider: "groq" or "huggingface"
            model_name: Model name (defaults from env/config)
            api_key: API key (defaults to env var)
            temperature: LLM temperature (lower = more deterministic)
        """
        self.provider = provider.lower()
        self.temperature = temperature

        # Get API key
        if api_key:
            self.api_key = api_key
        elif self.provider == "groq":
            self.api_key = os.getenv("GROQ_API_KEY")
            if not self.api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
        else:
            self.api_key = os.getenv("HUGGINGFACE_API_KEY")
            if not self.api_key:
                raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")

        # Get model name
        if model_name:
            self.model_name = model_name
        elif self.provider == "groq":
            self.model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        else:
            self.model_name = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-3.1-8B-Instruct")

        # Initialize LLM
        self.llm = self._create_llm()

        logger.info(f"Initialized {self.provider} LLM: {self.model_name}")

    def _create_llm(self) -> BaseChatModel:
        """Create LLM instance based on provider."""
        if self.provider == "groq":
            return ChatGroq(
                model=self.model_name,
                api_key=self.api_key,
                temperature=self.temperature,
            )
        else:
            # HuggingFace support (can be added later)
            raise NotImplementedError("HuggingFace support coming soon. Use Groq for now.")

    def invoke(self, prompt: str, **kwargs) -> str:
        """
        Invoke LLM with a prompt.
        Includes rate limiting to prevent 429 errors.

        Args:
            prompt: Input prompt
            **kwargs: Additional arguments for LLM

        Returns:
            LLM response as string
        """
        global _last_request_time
        
        # Rate limiting: Wait if needed to avoid hitting rate limits
        current_time = time.time()
        time_since_last_request = current_time - _last_request_time
        if time_since_last_request < REQUEST_DELAY:
            sleep_time = REQUEST_DELAY - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        try:
            response = self.llm.invoke(prompt, **kwargs)
            _last_request_time = time.time()
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "rate limit" in error_msg:
                # Rate limit hit - wait longer and retry once
                logger.warning("Rate limit hit, waiting 5 seconds before retry...")
                time.sleep(5)
                try:
                    response = self.llm.invoke(prompt, **kwargs)
                    _last_request_time = time.time()
                    return response.content if hasattr(response, "content") else str(response)
                except Exception as retry_error:
                    logger.error(f"LLM invocation failed after retry: {retry_error}")
                    raise
            else:
                logger.error(f"LLM invocation failed: {e}")
                raise

    def get_llm(self) -> BaseChatModel:
        """Get the underlying LangChain LLM object."""
        return self.llm


# Global instance (lazy initialization)
_global_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create global LLM client instance."""
    global _global_llm_client
    if _global_llm_client is None:
        _global_llm_client = LLMClient()
    return _global_llm_client

