# What's for Dinner - Implementation Plan

This document outlines the implementation plan broken down into Linear-compatible tasks. Each phase builds on the previous one, ensuring we always have working, testable code.

## Phase 1: Foundation (Week 1)

### Epic: Project Setup & Infrastructure
**Goal**: Establish project structure with clean architecture

#### Backend Setup
- [ ] **WFD-1**: Initialize backend project structure
  - Create `backend/app/domain`, `application`, `infrastructure` directories
  - Set up `pyproject.toml` with dependencies (FastAPI, SQLAlchemy, Pydantic, pytest)
  - Configure `ruff` for linting and formatting
  - Add `.gitignore` for Python
  - **Tests**: Directory structure exists, imports work

- [ ] **WFD-2**: Create domain entities
  - Implement `Recipe` entity with `Ingredient` dataclass
  - Implement `UserProfile` entity with dietary preferences
  - Implement `MealPlan` entity with `MealSlot`
  - Implement `GroceryList` and `GroceryItem` entities
  - Implement `Feedback` entity
  - **Tests**: Unit tests for entity methods (e.g., `Recipe.scale()`)

- [ ] **WFD-3**: Define domain interfaces (ports)
  - Create `IRecipeRepository` interface
  - Create `IUserRepository` interface
  - Create `IMealPlanRepository` interface
  - Create `IVectorStore` interface
  - Create `ILLMService` interface
  - Create `IEmbeddingService` interface
  - **Tests**: Interfaces are abstract and importable

- [ ] **WFD-4**: Set up configuration management
  - Create `app/config.py` with pydantic-settings
  - Define settings for local (SQLite, Milvus, Ollama)
  - Define settings for production (DynamoDB, Zilliz, Bedrock)
  - Add environment variable loading
  - **Tests**: Settings load correctly from env vars

#### Database Layer
- [ ] **WFD-5**: Implement SQLite persistence layer
  - Create SQLAlchemy models for Recipe, UserProfile, MealPlan, Feedback, GroceryList
  - Implement `SQLiteRecipeRepository`
  - Implement `SQLiteUserRepository`
  - Implement `SQLiteMealPlanRepository`
  - Create database session management
  - **Tests**: Integration tests for each repository (CRUD operations)

- [ ] **WFD-6**: Create database initialization scripts
  - Write `scripts/init_db.py` to create all tables
  - Add sample data script for testing
  - Create migration strategy notes
  - **Tests**: Script creates valid schema, sample data loads

#### API Layer
- [ ] **WFD-7**: Set up FastAPI application
  - Create `app/main.py` with FastAPI app
  - Add CORS middleware
  - Add error handling middleware
  - Add health check endpoint
  - Configure Mangum handler for Lambda compatibility
  - **Tests**: Health check returns 200

- [ ] **WFD-8**: Implement dependency injection container
  - Create `infrastructure/api/dependencies.py`
  - Add factory functions for repositories (SQLite vs DynamoDB)
  - Add factory functions for services (Ollama vs Bedrock)
  - Environment-based switching logic
  - **Tests**: DI returns correct implementations based on env

- [ ] **WFD-9**: Implement user profile endpoints
  - Create `ManageProfileUseCase` (create, get, update)
  - Create profile DTOs (request/response)
  - Implement `POST /api/profile` endpoint
  - Implement `GET /api/profile` endpoint
  - Implement `PATCH /api/profile` endpoint
  - **Tests**: API tests for profile CRUD

#### Frontend Setup
- [ ] **WFD-10**: Initialize Next.js frontend
  - Create Next.js 14 app with App Router
  - Set up TypeScript configuration
  - Add Tailwind CSS
  - Create basic layout with navigation
  - **Tests**: Dev server runs, pages render

- [ ] **WFD-11**: Create API client library
  - Create `lib/api.ts` with fetch wrapper
  - Add TypeScript types matching backend DTOs
  - Implement profile API methods
  - Add error handling
  - **Tests**: API client methods type-check

- [ ] **WFD-12**: Build user profile/onboarding UI
  - Create `PreferenceForm` component
  - Build multi-step onboarding flow
  - Add form validation
  - Connect to profile API
  - **Tests**: E2E test for profile creation

---

## Phase 2: Recipe Corpus & Vector Search (Week 2)

### Epic: Recipe Management & Semantic Search

#### Recipe Data Pipeline
- [ ] **WFD-13**: Define recipe JSON schema
  - Document ingredient schema
  - Document recipe schema
  - Create JSON schema validator
  - Add example recipes
  - **Tests**: Schema validation catches errors

- [ ] **WFD-14**: Build recipe ingestion tooling
  - Create `scripts/validate_recipe.py`
  - Create `scripts/import_recipes.py`
  - Add recipe scraping helpers (optional)
  - Create recipe template
  - **Tests**: Script validates and imports sample recipes

- [ ] **WFD-15**: Curate initial recipe corpus
  - Research and collect 50+ recipes
  - Convert to standard JSON format
  - Validate all recipes
  - Organize by cuisine and difficulty
  - Store in `backend/data/recipes/`
  - **Tests**: All recipes pass validation

#### Vector Store Setup
- [ ] **WFD-16**: Set up Milvus locally
  - Create `docker-compose.yml` with Milvus
  - Document Milvus startup process
  - Create Milvus connection test script
  - **Tests**: Milvus accepts connections

- [ ] **WFD-17**: Implement Ollama embedding service
  - Create `OllamaEmbeddingService` implementing `IEmbeddingService`
  - Add connection to Ollama API
  - Implement `nomic-embed-text` embedding generation
  - Add batch embedding support
  - **Tests**: Unit tests with mocked Ollama, integration test with real Ollama

- [ ] **WFD-18**: Implement Milvus vector store adapter
  - Create `MilvusVectorStore` implementing `IVectorStore`
  - Implement collection creation (768 dimensions, COSINE)
  - Implement upsert, query, delete methods
  - Add metadata filtering support
  - **Tests**: Integration tests for vector CRUD operations

- [ ] **WFD-19**: Create recipe embedding pipeline
  - Create `scripts/embed_recipes.py`
  - Generate embeddings for all recipes
  - Store in Milvus with metadata
  - Link recipe IDs between SQLite and Milvus
  - **Tests**: All recipes have embeddings, search returns results

#### Recipe API & UI
- [ ] **WFD-20**: Implement recipe search use cases
  - Create `SearchRecipesUseCase`
  - Add filtering by cuisine, time, tags
  - Add semantic search via vector store
  - Combine filters with vector search
  - **Tests**: Unit tests for search logic

- [ ] **WFD-21**: Build recipe API endpoints
  - Implement `GET /api/recipes` (list with filters)
  - Implement `GET /api/recipes/{id}` (detail)
  - Implement `POST /api/recipes/suggest` (semantic search)
  - Add pagination
  - **Tests**: API integration tests

- [ ] **WFD-22**: Create recipe browsing UI
  - Build `RecipeCard` component
  - Build `RecipeList` component with filters
  - Build `RecipeDetail` page
  - Add search interface
  - **Tests**: UI renders recipes, filters work

---

## Phase 3: RAG Pipeline & Meal Planning (Week 3)

### Epic: AI-Powered Meal Plan Generation

#### LLM Integration
- [ ] **WFD-23**: Set up Ollama locally
  - Pull `qwen2.5:14b` model
  - Test Ollama API connection
  - Document model selection rationale
  - **Tests**: Ollama generates responses

- [ ] **WFD-24**: Implement Ollama LLM service
  - Create `OllamaLLMService` implementing `ILLMService`
  - Implement `generate()` method
  - Implement `generate_json()` with parsing
  - Handle markdown code block wrapping
  - Add retry logic for failed requests
  - **Tests**: Unit tests with mocked API, integration test with real Ollama

- [ ] **WFD-25**: Create prompt templates
  - Write `plan_generation.txt` prompt template
  - Write `recipe_adaptation.txt` prompt template
  - Write `grocery_consolidation.txt` prompt template
  - Add prompt formatting utilities
  - **Tests**: Prompts render correctly with sample data

#### RAG Pipeline
- [ ] **WFD-26**: Implement RAG service
  - Create `RAGService` in application layer
  - Implement pre-filtering (dietary restrictions, max time)
  - Implement vector search for candidates
  - Implement post-filtering and reranking
  - Add variety scoring (protein diversity)
  - **Tests**: RAG returns diverse, valid candidates

- [ ] **WFD-27**: Build reranking logic
  - Implement cuisine preference scoring
  - Implement recency penalty (avoid recent meals)
  - Implement user rating boost
  - Implement variety score (protein diversity)
  - Combine scores with weights
  - **Tests**: Reranking produces expected order

#### Meal Planning Use Cases
- [ ] **WFD-28**: Implement GenerateMealPlanUseCase
  - Create use case with request/response DTOs
  - Integrate RAG service for candidate retrieval
  - Build prompt with user profile + candidates
  - Call LLM to select and arrange meals
  - Validate LLM output with Pydantic
  - Save meal plan to repository
  - **Tests**: Unit tests with mocked dependencies, integration test

- [ ] **WFD-29**: Implement SwapMealUseCase
  - Create use case for swapping single day
  - Retrieve alternatives from RAG
  - Update meal plan in repository
  - **Tests**: Swap preserves other days, respects constraints

- [ ] **WFD-30**: Implement RegenerateDayUseCase
  - Create use case for regenerating suggestions
  - Return 3 alternatives with reasoning
  - Do not auto-save (user chooses)
  - **Tests**: Returns valid alternatives

#### Meal Planning API
- [ ] **WFD-31**: Build meal planning endpoints
  - Implement `POST /api/plan/generate`
  - Implement `GET /api/plan/{id}`
  - Implement `PATCH /api/plan/{id}` (swap meal)
  - Implement `POST /api/plan/{plan_id}/regenerate-day`
  - Add proper error handling
  - **Tests**: API integration tests for all endpoints

#### Meal Planning UI
- [ ] **WFD-32**: Create meal plan components
  - Build `MealPlanCard` component
  - Build `WeeklyPlanView` component
  - Add swap functionality UI
  - Add regenerate alternatives modal
  - **Tests**: Components render, interactions work

- [ ] **WFD-33**: Build meal plan pages
  - Create `/plan` page (current week)
  - Create `/plan/[weekStart]` page (specific week)
  - Add "Generate New Plan" button
  - Connect to meal plan API
  - **Tests**: E2E test for plan generation flow

---

## Phase 4: Grocery Lists & Feedback (Week 4)

### Epic: Grocery Consolidation & Learning

#### Grocery List Logic
- [ ] **WFD-34**: Implement grocery consolidation service
  - Create `GroceryService` in application layer
  - Implement ingredient quantity consolidation
  - Group by grocery store section
  - Add recipe attribution to items
  - Round up quantities for practical shopping
  - **Tests**: Unit tests for consolidation accuracy

- [ ] **WFD-35**: Implement GetGroceryListUseCase
  - Create use case with request/response DTOs
  - Retrieve meal plan recipes
  - Scale recipes to servings
  - Consolidate with GroceryService
  - Save grocery list to repository
  - **Tests**: Generated list matches expected output

- [ ] **WFD-36**: Build grocery list endpoints
  - Implement `GET /api/plan/{id}/grocery`
  - Implement `PATCH /api/plan/{id}/grocery` (mark purchased)
  - Add export formats (JSON, plain text)
  - **Tests**: API integration tests

#### Grocery List UI
- [ ] **WFD-37**: Create grocery list components
  - Build `GroceryList` component
  - Group items by store section
  - Add checkboxes for purchased items
  - Show recipe attribution badges
  - Add "Copy to clipboard" functionality
  - **Tests**: Component renders grouped items

- [ ] **WFD-38**: Build grocery list page
  - Create `/grocery` page
  - Connect to grocery API
  - Add print stylesheet
  - **Tests**: Page renders, interactions work

#### Feedback System
- [ ] **WFD-39**: Implement SubmitFeedbackUseCase
  - Create use case with request/response DTOs
  - Validate rating (1-5)
  - Save feedback to repository
  - Link to recipe and meal plan
  - **Tests**: Feedback saves correctly

- [ ] **WFD-40**: Build feedback endpoints
  - Implement `POST /api/feedback`
  - Implement `GET /api/feedback/recent` (for history)
  - **Tests**: API integration tests

- [ ] **WFD-41**: Integrate feedback into RAG ranking
  - Update reranking logic to use feedback
  - Boost highly rated recipes
  - Penalize low-rated recipes
  - Consider "would_make_again" flag
  - **Tests**: RAG prefers highly rated recipes

- [ ] **WFD-42**: Create feedback UI
  - Build "I cooked this" button on recipe detail
  - Create feedback modal (rating, notes)
  - Add to recipe detail page
  - **Tests**: Feedback submission works

- [ ] **WFD-43**: Build history page
  - Create `/history` page
  - Show past meal plans
  - Show feedback submitted
  - Allow viewing past plans
  - **Tests**: History displays correctly

---

## Phase 5: Cloud Migration & Polish (Week 5)

### Epic: Production Readiness

#### Cloud Infrastructure Adapters
- [ ] **WFD-44**: Implement DynamoDB repositories
  - Create `DynamoDBRecipeRepository`
  - Create `DynamoDBUserRepository`
  - Create `DynamoDBMealPlanRepository`
  - Implement single-table design
  - **Tests**: Integration tests with local DynamoDB

- [ ] **WFD-45**: Implement Zilliz Cloud adapter
  - Update `MilvusVectorStore` to support Zilliz
  - Add token authentication
  - Test with Zilliz free tier
  - **Tests**: Same tests pass with Zilliz

- [ ] **WFD-46**: Implement Bedrock LLM service
  - Create `BedrockLLMService` implementing `ILLMService`
  - Add Claude 3.5 Sonnet support
  - Handle Bedrock API format
  - **Tests**: Unit tests with mocked boto3

- [ ] **WFD-47**: Implement Bedrock embedding service
  - Create `BedrockEmbeddingService`
  - Add Titan Embeddings support
  - **Tests**: Unit tests with mocked boto3

#### Infrastructure as Code
- [ ] **WFD-48**: Create Terraform configuration
  - Set up `infra/` directory structure
  - Create `main.tf` with provider config
  - Create `variables.tf` and `outputs.tf`
  - Add `terraform.tfvars.example`
  - **Tests**: `terraform validate` passes

- [ ] **WFD-49**: Define Lambda infrastructure
  - Create `lambda.tf` with function definition
  - Configure IAM role and policies
  - Add environment variables
  - Set up Lambda layer for dependencies
  - **Tests**: Terraform plan succeeds

- [ ] **WFD-50**: Define API Gateway infrastructure
  - Create `api_gateway.tf`
  - Configure HTTP API with Lambda integration
  - Add CORS configuration
  - Set up CloudWatch logs
  - **Tests**: Terraform plan succeeds

- [ ] **WFD-51**: Define DynamoDB infrastructure
  - Create `dynamodb.tf`
  - Configure single table with GSI
  - Set up on-demand billing
  - Enable point-in-time recovery
  - **Tests**: Terraform plan succeeds

- [ ] **WFD-52**: Define secrets management
  - Create `secrets.tf`
  - Add Secrets Manager for Zilliz credentials
  - Configure Lambda access to secrets
  - **Tests**: Terraform plan succeeds

#### Deployment & Documentation
- [ ] **WFD-53**: Create deployment scripts
  - Write backend deployment script
  - Write frontend build script
  - Add environment variable management
  - Document deployment process
  - **Tests**: Scripts run without errors

- [ ] **WFD-54**: Deploy to AWS
  - Run Terraform apply
  - Deploy Lambda function
  - Configure API Gateway
  - Seed DynamoDB with recipes
  - Populate Zilliz with embeddings
  - **Tests**: Health check returns 200 from API Gateway

- [ ] **WFD-55**: Deploy frontend
  - Set up Amplify Hosting or S3 + CloudFront
  - Configure environment variables
  - Deploy static build
  - Test production frontend
  - **Tests**: Frontend loads and connects to API

- [ ] **WFD-56**: Write comprehensive README
  - Add project overview
  - Add architecture diagrams
  - Document technology choices
  - Add local setup instructions
  - Add cloud deployment guide
  - **Tests**: New developer can follow README

- [ ] **WFD-57**: Create cost analysis document
  - Calculate local development costs ($0)
  - Calculate AWS free tier usage
  - Estimate monthly costs at scale
  - Document cost optimization strategies
  - **Tests**: Document is accurate and complete

- [ ] **WFD-58**: Polish and bug fixes
  - Fix any remaining bugs
  - Improve error messages
  - Add loading states
  - Improve UI/UX
  - **Tests**: All tests pass, no console errors

- [ ] **WFD-59**: Create demo materials
  - Record demo video (3-5 minutes)
  - Take screenshots for README
  - Write deployment case study
  - **Tests**: Demo materials are presentable

---

## Success Criteria

### MVP Complete Checklist
- [ ] User can create profile with dietary restrictions
- [ ] User can generate 5-day meal plan
- [ ] Meal plans respect all dietary restrictions (100% accuracy)
- [ ] User can swap individual meals with alternatives
- [ ] Consolidated grocery list generates with correct quantities
- [ ] Grocery list groups items by store section
- [ ] User can submit feedback with ratings
- [ ] Feedback influences future meal plan suggestions
- [ ] All unit tests pass (>80% coverage)
- [ ] All integration tests pass
- [ ] Application runs locally without errors
- [ ] Application deploys to AWS successfully
- [ ] Documentation is complete and accurate

### Portfolio Quality Checklist
- [ ] Code follows clean architecture principles
- [ ] Domain layer has zero infrastructure dependencies
- [ ] All public APIs have docstrings
- [ ] Type hints on all function signatures
- [ ] README explains architecture decisions
- [ ] Tests demonstrate TDD approach
- [ ] Demo video showcases key features
- [ ] Cost analysis shows real AWS costs
- [ ] Code is deployment-ready

---

## Notes

### Dependency Chain
- **WFD-1 through WFD-3** must complete before any other work
- **WFD-5** depends on **WFD-2** (entities must exist)
- **WFD-9** depends on **WFD-8** (DI needed for endpoints)
- **WFD-13** through **WFD-15** should be done in parallel (can work independently)
- **WFD-26** depends on **WFD-17** and **WFD-18** (embedding + vector store)
- **WFD-28** depends on **WFD-24** and **WFD-26** (LLM + RAG)
- **Phase 5** depends on **Phase 4** being complete

### Parallel Work Opportunities
- Frontend tasks (**WFD-10** through **WFD-12**) can be done alongside backend infrastructure
- Recipe curation (**WFD-15**) can happen while building other features
- Cloud adapters (**WFD-44** through **WFD-47**) can be built anytime after interfaces are defined
- Documentation can be written incrementally throughout

### Risk Mitigation
- **LLM output quality**: Build validation early, have fallback prompts
- **Vector search accuracy**: Test with known recipe pairs, tune similarity thresholds
- **Cost overruns**: Monitor AWS usage, set billing alarms
- **Data quality**: Validate recipes thoroughly before embedding
