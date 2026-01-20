"""LLM service interface (port).

This interface defines the contract for large language model operations.
Any implementation (Ollama, Bedrock, OpenAI, etc.) must follow this interface.
"""

from abc import ABC, abstractmethod


class ILLMService(ABC):
    """Abstract interface for large language model interactions."""

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate text using the LLM.

        Args:
            prompt: The prompt to send to the LLM
            temperature: Sampling temperature (0.0-1.0, higher = more creative)
            max_tokens: Maximum tokens in response

        Returns:
            Generated text response

        Raises:
            LLMError: If generation fails
        """
        pass

    @abstractmethod
    def generate_with_system_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate text using both system and user prompts.

        Args:
            system_prompt: System message that sets context and behavior
            user_prompt: User query or instruction
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Generated text response

        Raises:
            LLMError: If generation fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM service is available and healthy.

        Returns:
            True if service is available, False otherwise
        """
        pass
