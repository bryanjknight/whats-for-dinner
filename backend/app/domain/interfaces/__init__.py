"""Domain layer interfaces (ports).

These interfaces define contracts for external dependencies.
Implementations in the infrastructure layer must follow these contracts.
"""

from app.domain.interfaces.embedding_service import IEmbeddingService
from app.domain.interfaces.llm_service import ILLMService
from app.domain.interfaces.meal_plan_repository import IMealPlanRepository
from app.domain.interfaces.recipe_repository import IRecipeRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.domain.interfaces.vector_store import IVectorStore

__all__ = [
    "IRecipeRepository",
    "IUserRepository",
    "IMealPlanRepository",
    "IVectorStore",
    "ILLMService",
    "IEmbeddingService",
]
