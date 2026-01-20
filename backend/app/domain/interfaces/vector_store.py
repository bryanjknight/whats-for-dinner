"""Vector store interface (port).

This interface defines the contract for vector similarity search operations.
Any implementation (Milvus, Zilliz Cloud, Pinecone, etc.) must follow this interface.
"""

from abc import ABC, abstractmethod

from ..entities.recipe import Recipe


class IVectorStore(ABC):
    """Abstract interface for vector storage and similarity search."""

    @abstractmethod
    def index_recipe(self, recipe: Recipe, embedding: list[float]) -> None:
        """Index a recipe with its embedding vector.

        Args:
            recipe: Recipe entity to index
            embedding: Vector embedding representation

        Raises:
            VectorStoreError: If indexing operation fails
        """
        pass

    @abstractmethod
    def search_similar(self, query_embedding: list[float], limit: int = 10) -> list[str]:
        """Search for similar recipes by embedding similarity.

        Args:
            query_embedding: Query vector embedding
            limit: Maximum number of results to return

        Returns:
            List of recipe IDs ordered by similarity (most similar first)
        """
        pass

    @abstractmethod
    def delete_recipe(self, recipe_id: str) -> bool:
        """Delete a recipe from the vector store.

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, recipe_id: str) -> bool:
        """Check if a recipe exists in the vector store.

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            True if recipe exists, False otherwise
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all data from the vector store.

        This is typically used for testing or resetting.
        """
        pass
