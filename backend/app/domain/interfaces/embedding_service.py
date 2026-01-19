"""Embedding service interface (port).

This interface defines the contract for text embedding operations.
Any implementation (Ollama, Bedrock, OpenAI, etc.) must follow this interface.
"""

from abc import ABC, abstractmethod

from ..exceptions import EmbeddingError


class IEmbeddingService(ABC):
    """Abstract interface for text embedding generation."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text.

        Args:
            text: Text to embed

        Returns:
            Vector embedding as a list of floats

        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of vector embeddings

        Raises:
            EmbeddingError: If batch embedding fails
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the dimensionality of the embedding vectors.

        Returns:
            Dimension of embedding vectors (e.g., 384, 768, 1536)
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the embedding service is available and healthy.

        Returns:
            True if service is available, False otherwise
        """
        pass
