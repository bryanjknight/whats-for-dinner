# Meal Planner Application - Development Guide

## Project Overview

A local-first, AI-powered meal planning application that generates personalized weekly dinner plans with consolidated grocery lists. Built with clean architecture principles for easy cloud migration.

**Key Goals**:
- Cost minimization: Local-first with clear cloud upgrade path
- Quality over features: Excellent recipe generation and RAG implementation
- Portfolio-ready: Clean architecture, documented decisions

## Architecture Philosophy

### Onion Architecture

This project strictly follows onion architecture:

```
Domain (Core) → Application (Use Cases) → Infrastructure (Adapters)
```

**Critical Rules**:
- Domain layer has ZERO external dependencies (no SQLAlchemy, no FastAPI, no Ollama)
- Application layer depends only on domain interfaces
- Infrastructure layer implements domain interfaces with specific technologies
- Dependencies point INWARD only

### Technology Swappability

Every external dependency must be swappable:
- SQLite ↔ DynamoDB (via IRepository)
- Milvus ↔ Zilliz Cloud (via IVectorStore)
- Ollama ↔ Bedrock (via ILLMService)
- Local ↔ Cloud with zero domain/application changes

## Project Structure

```
backend/
├── app/
│   ├── domain/              # CORE - No external dependencies
│   │   ├── entities/        # Recipe, MealPlan, UserProfile
│   │   ├── interfaces/      # Abstract ports (IRecipeRepository, IVectorStore, etc.)
│   │   └── exceptions.py
│   │
│   ├── application/         # USE CASES - Business logic
│   │   ├── use_cases/       # GenerateMealPlan, SwapMeal, GetGroceryList
│   │   ├── dto/             # Request/Response objects
│   │   └── services/        # RAGService, GroceryService
│   │
│   └── infrastructure/      # ADAPTERS - External implementations
│       ├── api/             # FastAPI routes
│       ├── persistence/     # SQLite + DynamoDB repositories
│       ├── vector/          # Milvus/Zilliz implementations
│       ├── llm/             # Ollama/Bedrock implementations
│       └── embeddings/      # Embedding services
```

## Development Phases

### Phase 1: Foundation (Week 1)
**Goal**: Working backend with user profile management

**Deliverables**:
- [ ] Project structure (domain/application/infrastructure)
- [ ] Domain entities (Recipe, UserProfile, MealPlan)
- [ ] Domain interfaces (all repositories and services)
- [ ] SQLite repositories implementation
- [ ] Basic FastAPI endpoints (health, profile CRUD)
- [ ] Dependency injection container
- [ ] Frontend scaffolding with Next.js 14

**Tests**:
- Unit tests for domain entities
- Integration tests for SQLite repositories
- API endpoint tests

### Phase 2: Recipe Corpus & Vector Search (Week 2)
**Goal**: Recipe storage with semantic search capability

**Deliverables**:
- [ ] Recipe JSON schema and validation
- [ ] Recipe ingestion scripts
- [ ] 50+ curated recipes
- [ ] Milvus vector store implementation
- [ ] Ollama embedding service
- [ ] Recipe search API endpoints
- [ ] Recipe browsing UI

**Tests**:
- Recipe validation tests
- Vector search accuracy tests
- Embedding generation tests

### Phase 3: RAG Pipeline & Meal Planning (Week 3)
**Goal**: AI-powered meal plan generation

**Deliverables**:
- [ ] RAG service (retrieve, filter, rerank)
- [ ] Ollama LLM service implementation
- [ ] GenerateMealPlanUseCase
- [ ] SwapMealUseCase
- [ ] Prompt templates (plan generation, adaptation)
- [ ] Meal plan API endpoints
- [ ] Weekly plan UI with swap functionality

**Tests**:
- RAG retrieval quality tests
- Meal plan variety tests
- Dietary restriction validation tests

### Phase 4: Grocery & Feedback (Week 4)
**Goal**: Complete user workflow with learning

**Deliverables**:
- [ ] Grocery consolidation logic
- [ ] GetGroceryListUseCase
- [ ] SubmitFeedbackUseCase
- [ ] Feedback integration into RAG ranking
- [ ] Grocery list API endpoints
- [ ] Grocery list UI (grouped, checkboxes)
- [ ] Feedback submission UI

**Tests**:
- Grocery consolidation accuracy tests
- Feedback ranking integration tests

### Phase 5: Cloud Migration Path (Week 5)
**Goal**: AWS deployment ready with documentation

**Deliverables**:
- [ ] DynamoDB repository implementation
- [ ] Zilliz Cloud vector store adapter
- [ ] Bedrock LLM service
- [ ] Terraform infrastructure
- [ ] Environment-based DI switching
- [ ] Deployment documentation
- [ ] Cost analysis
- [ ] README with architecture diagrams

## Implementation Guidelines

### Domain Layer Rules

**NEVER import these in domain layer**:
- `fastapi`, `sqlalchemy`, `pymilvus`, `requests`, `boto3`
- Any infrastructure library

**Only use**:
- Python standard library
- `dataclasses`, `typing`, `abc`
- Your own domain code

**Example - GOOD**:
```python
# app/domain/entities/recipe.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Recipe:
    id: str
    title: str
    ingredients: list['Ingredient']

    def scale(self, new_servings: int) -> 'Recipe':
        # Pure domain logic
        pass
```

**Example - BAD**:
```python
# WRONG - Domain should not know about SQLAlchemy
from sqlalchemy import Column, String

class Recipe(Base):  # BAD - infrastructure leak
    __tablename__ = "recipes"
```

### Import Paths

**Always use absolute imports from the app root, never relative imports**:

```python
# ✓ GOOD - Absolute imports
from app.domain.entities.recipe import Recipe
from app.domain.interfaces.recipe_repository import IRecipeRepository
from app.application.use_cases.generate_meal_plan import GenerateMealPlanUseCase

# ✗ BAD - Relative imports
from ...domain.entities.recipe import Recipe
from ..interfaces.recipe_repository import IRecipeRepository
```

Benefits:
- Clearer code intent
- Easier IDE navigation and refactoring
- Works consistently across different execution contexts
- No confusion about relative path depth

### Configuration Management

Application configuration is centralized in `app/config.py` using `pydantic-settings` for environment-based management.

**Configuration File Location**: `app/config.py`

**Environment Variables File**: `.env` (local development, not committed to git)

**Example File**: `.env.example` (committed, shows all available options)

**Settings Features**:
- Loads from `.env` file in backend root directory
- Supports local, development, and production environments
- Type-safe configuration with validation
- Optional fields for production-only settings (Bedrock, Zilliz)
- Boolean and integer parsing from environment variables

**Usage in Application**:
```python
# In FastAPI routes or services
from app.config import Settings, get_settings

# As FastAPI dependency
from fastapi import Depends

def some_route(settings: Settings = Depends(get_settings)) -> dict:
    if settings.is_production:
        # Use production implementations
        pass
    else:
        # Use local implementations
        pass
```

**Environment Configuration for Local Development**:
```bash
ENVIRONMENT=local
DEBUG=true
DATABASE_URL=sqlite:///./meal_planner.db
VECTOR_STORE_TYPE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_PROVIDER=ollama
```

**Environment Configuration for Production**:
```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=dynamodb://meal_planner
VECTOR_STORE_TYPE=zilliz
ZILLIZ_API_KEY=your-api-key
ZILLIZ_URI=https://your-cluster.zilliz.com
LLM_PROVIDER=bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_REGION=us-east-1
EMBEDDING_PROVIDER=bedrock
BEDROCK_EMBED_MODEL_ID=amazon.titan-embed-text-v2:0
```

**Supported Providers**:
- **Database**: SQLite (local) → DynamoDB (production)
- **Vector Store**: Milvus (local) → Zilliz Cloud (production)
- **LLM**: Ollama (local) → Bedrock (production)
- **Embeddings**: Ollama (local) → Bedrock (production)

**Configuration Properties**:
- `settings.is_local` - Check if running in local environment
- `settings.is_production` - Check if running in production environment
- Use these for conditional logic and DI decisions

### Use Case Pattern

Every use case follows this structure:

```python
# app/application/use_cases/generate_meal_plan.py
from dataclasses import dataclass

from app.domain.entities.meal_plan import MealPlan
from app.domain.interfaces.llm_service import ILLMService
from app.domain.interfaces.recipe_repository import IRecipeRepository

@dataclass
class GenerateMealPlanRequest:
    user_id: str
    week_start: date

@dataclass
class GenerateMealPlanResponse:
    meal_plan: MealPlan
    reasoning: dict[str, str]

class GenerateMealPlanUseCase:
    def __init__(
        self,
        recipe_repo: IRecipeRepository,
        llm_service: ILLMService,
        # ... other interfaces
    ):
        self.recipe_repo = recipe_repo
        self.llm_service = llm_service

    def execute(self, request: GenerateMealPlanRequest) -> GenerateMealPlanResponse:
        # Business logic using interfaces only
        pass
```

### Testing Strategy

**Domain Tests** (Fast, no dependencies):
```python
def test_recipe_scaling():
    recipe = Recipe(id="1", servings=4, ingredients=[...])
    scaled = recipe.scale(8)
    assert scaled.servings == 8
    assert scaled.ingredients[0].quantity == 2.0
```

**Application Tests** (Use mocks):
```python
def test_generate_meal_plan_respects_dietary_restrictions():
    mock_repo = Mock(IRecipeRepository)
    mock_llm = Mock(ILLMService)
    use_case = GenerateMealPlanUseCase(mock_repo, mock_llm, ...)

    # Test business logic
```

**Infrastructure Tests** (Integration):
```python
def test_sqlite_recipe_repository_save_and_retrieve():
    repo = SQLiteRecipeRepository(":memory:")
    recipe = Recipe(...)
    repo.save(recipe)
    retrieved = repo.get_by_id(recipe.id)
    assert retrieved == recipe
```

### Dependency Injection

Use FastAPI's dependency injection for wiring:

```python
# app/infrastructure/api/dependencies.py
@lru_cache()
def get_llm_service(settings: Settings = Depends(get_settings)) -> ILLMService:
    if settings.is_production:
        return BedrockLLMService(...)
    return OllamaLLMService(...)

# In routes
@router.post("/plan/generate")
def generate_plan(
    request: GenerateMealPlanDTO,
    llm: ILLMService = Depends(get_llm_service),
    recipe_repo: IRecipeRepository = Depends(get_recipe_repository),
):
    use_case = GenerateMealPlanUseCase(llm, recipe_repo, ...)
    return use_case.execute(request)
```

## RAG Pipeline Specifics

### Retrieval Strategy

1. **Pre-filtering** (Hard constraints):
   - Dietary restrictions
   - Disliked ingredients
   - Max prep time

2. **Vector Search** (Semantic):
   - Query: User preferences + recent meal context
   - Return 20 candidates

3. **Post-filtering & Reranking** (Soft preferences):
   - Cuisine preference match
   - Time since last cooked
   - Variety score (protein diversity)
   - User rating history

### Prompt Engineering

**Critical Requirements**:
- All prompts must request JSON-only output
- Include schema examples in prompt
- Add system prompt for role/constraints
- Handle markdown code block wrapping in response parsing

**Template Location**: `app/infrastructure/prompts/`

### LLM Output Validation

Always validate LLM JSON with Pydantic:

```python
from pydantic import BaseModel

class MealSelection(BaseModel):
    recipe_id: int
    reasoning: str

# Parse and validate
response_text = llm_service.generate(prompt)
selection = MealSelection.model_validate_json(response_text)
```

## Local Development Setup

### Prerequisites Checklist

```bash
# Ollama
ollama pull qwen2.5:14b
ollama pull nomic-embed-text
ollama list  # Verify

# Milvus (via Docker)
docker-compose up -d milvus
curl http://localhost:9091/healthz  # Verify

# Python environment
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database
python scripts/init_db.py
python scripts/seed_recipes.py

# Run
uvicorn app.main:app --reload --port 8000
```

### Environment Variables

```bash
# backend/.env
ENVIRONMENT=local
DATABASE_URL=sqlite:///./meal_planner.db
MILVUS_HOST=localhost
MILVUS_PORT=19530
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

## Quality Standards

### Build & Validation

Use the Makefile in the `backend/` directory for all build and validation tasks:

```bash
# Navigate to backend directory
cd backend

# Full CI pipeline (clean, install, validate, test)
make all

# Common development workflow
make build validate test

# Check before commit (format, lint, type-check, test)
make format lint type-check test

# Quick validation without testing
make validate

# Run tests with coverage report
make test-cov

# Show tool versions and paths
make info
```

**Available make targets:**
- `make help` - Show all available commands
- `make install` - Install production dependencies
- `make install-dev` - Install development dependencies
- `make build` - Build and prepare project
- `make validate` - Run linting + type checking
- `make lint` - Check code style with ruff
- `make format` - Auto-format code
- `make type-check` - Run MyPy type checking
- `make test` - Run all tests
- `make test-cov` - Run tests with coverage report
- `make clean` - Clean build artifacts
- `make ci` - CI pipeline (for CI systems)

### Code Review Checklist

Before committing:
- [ ] Absolute imports only (no relative imports like `..domain`)
- [ ] Domain layer has no infrastructure imports
- [ ] All public methods have docstrings
- [ ] Type hints on all function signatures
- [ ] `make validate` passes (linting + type-checking)
- [ ] `make test` passes (all tests)
- [ ] `make format` has been run (code is formatted)

### Recipe Quality Standards

Each recipe must have:
- [ ] Tested by at least one person
- [ ] Precise ingredient quantities
- [ ] Realistic prep/cook times
- [ ] Clear, numbered instructions
- [ ] Appropriate tags (dietary, speed, difficulty)

### LLM Output Quality

Meal plans must:
- [ ] Respect 100% of dietary restrictions
- [ ] Vary proteins (no adjacent repeats)
- [ ] Honor time constraints
- [ ] Provide reasoning for selections

## Common Pitfalls to Avoid

1. **Leaking infrastructure into domain**
   - Bad: Domain entity inherits from SQLAlchemy Base
   - Good: Separate domain entity + ORM model + mapper

2. **Hardcoding environment logic**
   - Bad: `if ollama_url else bedrock`
   - Good: DI container selects implementation

3. **Testing implementation details**
   - Bad: Mock internal private methods
   - Good: Test public interface behavior

4. **Over-abstracting too early**
   - Bad: Abstract factory factory pattern
   - Good: Simple interface + 2 implementations

5. **Skipping vector search validation**
   - Bad: Assume Milvus works
   - Good: Write tests with known embeddings

## Decision Log

### Why Milvus over Pinecone/Chroma for local?

- Same SDK works for local Milvus and Zilliz Cloud
- No behavioral drift between environments
- Better performance for 200-300 recipes

### Why qwen2.5:14b over llama3.1:8b?

- Better instruction following for structured output
- Better at JSON formatting
- Worth the memory trade-off on M1 Pro 32GB

### Why single-table design for DynamoDB?

- Fewer cross-table queries (user + plans + recipes)
- More cost-efficient (less RCU/WCU)
- Standard pattern for serverless apps

### Why not Chroma?

- Initially considered Chroma for simplicity
- Milvus offers better migration path (Zilliz is hosted Milvus)
- Minimal added complexity with Docker Compose

## Debugging Checklist

### LLM not generating valid JSON?

1. Check prompt includes "Respond with valid JSON only"
2. Add schema example to prompt
3. Verify response parsing handles markdown code blocks
4. Test with simpler prompt first

### Vector search returning poor results?

1. Verify embeddings are actually generated
2. Check metadata filtering is applied correctly
3. Test with known similar recipes
4. Inspect similarity scores (should be > 0.5 for good matches)

### Dietary restrictions not respected?

1. Check pre-filtering in RAG pipeline
2. Verify LLM system prompt includes restrictions
3. Add validation after LLM response
4. Log rejected recipes for debugging

## Success Metrics

### MVP Complete When:

- [ ] User can create profile with restrictions
- [ ] User can generate 5-day meal plan
- [ ] Plans respect all dietary restrictions
- [ ] User can swap individual meals
- [ ] Consolidated grocery list generates correctly
- [ ] User can submit feedback
- [ ] Feedback influences future plans
- [ ] All tests pass
- [ ] Documentation is complete

### Portfolio Quality:

- [ ] README explains architecture decisions
- [ ] Code demonstrates clean architecture
- [ ] Tests show TDD approach
- [ ] Deployment guide for local + cloud
- [ ] Cost analysis with real numbers
- [ ] Demo video or live deployment

---

**Remember**: This is a portfolio piece. Prioritize:
1. **Code quality** over feature breadth
2. **Architecture** over quick hacks
3. **Documentation** over clever code
4. **Testability** over convenience

Build something you're proud to explain in interviews.
