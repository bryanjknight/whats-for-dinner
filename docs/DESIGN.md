# Meal Planner App — Design Document

## Project Overview

A local-first, AI-powered meal planning application that generates personalized weekly dinner plans with consolidated grocery lists. Designed to run entirely on a MacBook M1 Pro (32GB RAM) with a clear upgrade path to cloud services.

### Goals

1. **Cost minimization**: Run LLM inference and vector search locally; zero ongoing API costs during development
2. **Quality over features**: Prioritize excellent recipe generation and clear instructions over feature breadth
3. **Portfolio-ready**: Clean architecture, documented decisions, deployable demo

### Non-Goals (for MVP)

- Mobile app
- Grocery delivery integration (Instacart, etc.)
- Multi-user/family accounts
- Pantry photo scanning

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│   - User profile setup                                          │
│   - Weekly meal plan view                                       │
│   - Recipe detail view                                          │
│   - Grocery list view                                           │
│   - Feedback/rating UI                                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   /profile  │  │   /plan     │  │  /recipes   │             │
│  │   /feedback │  │   /grocery  │  │  /suggest   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  RAG Pipeline                            │   │
│  │  Query → Embed → Retrieve → Rerank → Context Assembly   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  LLM Service                             │   │
│  │  Recipe Generation │ Adaptation │ Grocery Consolidation │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   SQLite    │      │   Chroma    │      │   Ollama    │
│  (app data) │      │ (vectors)   │      │   (LLM)     │
└─────────────┘      └─────────────┘      └─────────────┘
```

### Technology Stack

| Layer | Local Development | Cloud (AWS Serverless) |
|-------|-------------------|------------------------|
| Frontend | Next.js 14 (App Router) | AWS Amplify Hosting (or S3 + CloudFront) |
| Backend | FastAPI + Uvicorn | API Gateway + Lambda (via Mangum adapter) |
| LLM | Ollama (qwen2.5:14b or llama3.1:8b) | Amazon Bedrock (Claude) or Lambda + Anthropic API |
| Embeddings | nomic-embed-text via Ollama | Amazon Bedrock (Titan Embeddings) or Voyage API |
| Vector Store | Milvus (local via Docker) | Zilliz Cloud (free tier: 2 collections, 500K vectors) |
| Database | SQLite + SQLAlchemy | DynamoDB (on-demand) or Aurora Serverless v2 |
| Auth | None (single user local) | Cognito (optional, for multi-user) |
| Infrastructure | Docker Compose (optional) | Terraform |

**Why this AWS stack:**
- **Lambda + API Gateway**: Pay-per-request, ~$0 at low traffic, scales automatically
- **DynamoDB on-demand**: No minimum cost, pay only for reads/writes
- **Amplify Hosting**: Free tier includes 1000 build minutes/month, 15GB served
- **Bedrock**: Pay-per-token, no provisioned capacity needed
- **Milvus → Zilliz**: Same engine locally and in cloud—no behavioral drift between environments

---

## Data Models

### SQLite Schema

```sql
-- User preferences and restrictions
CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY,
    household_size INTEGER DEFAULT 2,
    dietary_restrictions TEXT,  -- JSON array: ["vegetarian", "gluten-free"]
    disliked_ingredients TEXT,  -- JSON array: ["cilantro", "olives"]
    cuisine_preferences TEXT,   -- JSON array: ["italian", "mexican", "asian"]
    max_prep_time_minutes INTEGER DEFAULT 45,
    skill_level TEXT DEFAULT 'intermediate',  -- beginner, intermediate, advanced
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recipe corpus (source of truth, not LLM-generated)
CREATE TABLE recipe (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    cuisine TEXT,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    total_time_minutes INTEGER GENERATED ALWAYS AS (prep_time_minutes + cook_time_minutes) STORED,
    servings INTEGER,
    difficulty TEXT,  -- easy, medium, hard
    ingredients TEXT NOT NULL,  -- JSON array (see schema below)
    instructions TEXT NOT NULL, -- JSON array of step strings
    tags TEXT,  -- JSON array: ["vegetarian", "one-pot", "meal-prep"]
    source_url TEXT,
    source_name TEXT,
    embedding_id TEXT,  -- reference to Chroma document ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly meal plans
CREATE TABLE meal_plan (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES user_profile(id),
    week_start DATE NOT NULL,
    meals TEXT NOT NULL,  -- JSON: {"monday": recipe_id, "tuesday": recipe_id, ...}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User feedback for learning
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES user_profile(id),
    recipe_id INTEGER REFERENCES recipe(id),
    meal_plan_id INTEGER REFERENCES meal_plan(id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    would_make_again BOOLEAN,
    notes TEXT,
    cooked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated grocery lists
CREATE TABLE grocery_list (
    id INTEGER PRIMARY KEY,
    meal_plan_id INTEGER REFERENCES meal_plan(id),
    items TEXT NOT NULL,  -- JSON array (see schema below)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### JSON Schemas

#### Ingredient Schema
```json
{
  "item": "chicken thighs",
  "quantity": 1.5,
  "unit": "lbs",
  "preparation": "boneless, skinless",
  "category": "protein",
  "optional": false
}
```

#### Grocery Item Schema
```json
{
  "item": "chicken thighs",
  "total_quantity": 3,
  "unit": "lbs",
  "category": "meat",
  "recipes_used_in": ["Chicken Tikka Masala", "Greek Chicken Bowl"],
  "notes": "boneless, skinless"
}
```

#### Meal Plan Schema
```json
{
  "monday": {"recipe_id": 42, "servings_override": null},
  "tuesday": {"recipe_id": 17, "servings_override": 4},
  "wednesday": null,
  "thursday": {"recipe_id": 8, "servings_override": null},
  "friday": {"recipe_id": 23, "servings_override": null},
  "saturday": null,
  "sunday": {"recipe_id": 31, "servings_override": null}
}
```

---

## RAG Pipeline Design

### Recipe Corpus Strategy

**Target size**: 200-300 high-quality recipes to start

**Sources** (prioritized by quality):
1. Serious Eats (well-tested, explains "why")
2. Budget Bytes (practical, cost-conscious)
3. USDA/Extension services (public domain)
4. Manually curated family favorites

**Ingestion process**:
1. Scrape or manually enter recipes into structured JSON
2. Validate against ingredient/instruction schema
3. Generate embedding from combined text (title + description + ingredients + cuisine + tags)
4. Store in SQLite (structured) and Chroma (vector)

### Embedding Strategy

**Model**: `nomic-embed-text` via Ollama (768 dimensions, good quality, runs locally)

**What to embed**: Concatenated string of:
```
{title}

{description}

Cuisine: {cuisine}
Tags: {tags joined by comma}
Main ingredients: {top 5 ingredients by importance}
```

**Why this approach**: 
- Recipes are short enough to embed whole (no chunking needed)
- Metadata in embedding improves semantic search
- Separate structured filtering happens before/after retrieval

### Retrieval Strategy

```python
def retrieve_recipes(
    query: str,
    user_profile: UserProfile,
    n_candidates: int = 20,
    n_final: int = 7
) -> list[Recipe]:
    """
    1. Pre-filter by hard constraints (dietary restrictions, disliked ingredients)
    2. Embed query
    3. Vector search for candidates
    4. Post-filter and rerank by soft preferences (cuisine, time, recent history)
    5. Return top N
    """
```

**Pre-filtering** (in Chroma metadata or SQL):
- Exclude recipes with disliked ingredients
- Exclude recipes violating dietary restrictions
- Filter by max prep time

**Reranking factors**:
- Cuisine preference match (+weight)
- Time since last cooked (-weight if recent)
- User rating history (+weight for highly rated similar recipes)
- Variety score (-weight if same protein as adjacent days)

---

## LLM Integration

### Model Selection

**Primary recommendation**: `qwen2.5:14b` via Ollama
- Excellent instruction following
- Good at structured output
- Runs well on M1 Pro 32GB (needs ~10GB VRAM)

**Fallback**: `llama3.1:8b` if memory constrained

**Cloud upgrade**: Claude 3.5 Sonnet (superior quality, ~$0.003/1K input tokens)

### Prompt Templates

#### Weekly Plan Generation

```
You are a meal planning assistant. Generate a weekly dinner plan based on the user's preferences and the available recipes.

USER PROFILE:
- Household size: {household_size}
- Dietary restrictions: {dietary_restrictions}
- Disliked ingredients: {disliked_ingredients}
- Cuisine preferences: {cuisine_preferences}
- Max prep time: {max_prep_time} minutes
- Skill level: {skill_level}

AVAILABLE RECIPES (retrieved based on preferences):
{retrieved_recipes_json}

RECENT MEALS (to avoid repetition):
{recent_meals_list}

INSTRUCTIONS:
1. Select 5 dinners for the week (Mon, Tue, Thu, Fri, Sun - leaving Wed/Sat flexible)
2. Ensure variety in proteins and cuisines across the week
3. Consider prep time distribution (lighter meals on busy weeknights)
4. Avoid repeating proteins on consecutive days

Respond with valid JSON only:
{
  "monday": {"recipe_id": <id>, "reasoning": "<brief explanation>"},
  "tuesday": {"recipe_id": <id>, "reasoning": "<brief explanation>"},
  ...
}
```

#### Recipe Adaptation

```
You are a helpful cooking assistant. Adapt the following recipe based on the user's needs.

ORIGINAL RECIPE:
{recipe_json}

ADAPTATION REQUEST:
{user_request}

USER CONSTRAINTS:
- Dietary restrictions: {dietary_restrictions}
- Disliked ingredients: {disliked_ingredients}

Provide the adapted recipe in the same JSON format, explaining substitutions in a "adaptation_notes" field.
```

#### Grocery List Consolidation

```
Consolidate the following ingredients from multiple recipes into a single grocery list.

RECIPES AND INGREDIENTS:
{recipes_with_ingredients}

INSTRUCTIONS:
1. Combine quantities of identical ingredients
2. Group by grocery store section (produce, meat, dairy, pantry, frozen)
3. Add notes for items that appear in multiple recipes
4. Round up quantities for practical shopping

Respond with valid JSON:
{
  "produce": [...],
  "meat": [...],
  "dairy": [...],
  "pantry": [...],
  "frozen": [...]
}
```

### Structured Output Handling

Use Pydantic models for validation:

```python
from pydantic import BaseModel

class MealSelection(BaseModel):
    recipe_id: int
    reasoning: str

class WeeklyPlan(BaseModel):
    monday: MealSelection | None
    tuesday: MealSelection | None
    wednesday: MealSelection | None
    thursday: MealSelection | None
    friday: MealSelection | None
    saturday: MealSelection | None
    sunday: MealSelection | None

# Parse LLM output
plan = WeeklyPlan.model_validate_json(llm_response)
```

---

## API Endpoints

### Profile Management

```
POST /api/profile
  Create or update user profile
  Body: UserProfileCreate schema
  Returns: UserProfile

GET /api/profile
  Get current user profile
  Returns: UserProfile
```

### Meal Planning

```
POST /api/plan/generate
  Generate a new weekly meal plan
  Body: { "week_start": "2025-01-20", "preferences_override": {...} }
  Returns: MealPlan with embedded recipe summaries

GET /api/plan/{plan_id}
  Get a specific meal plan
  Returns: MealPlan with full recipe details

PATCH /api/plan/{plan_id}
  Swap a meal in an existing plan
  Body: { "day": "tuesday", "new_recipe_id": 42 }
  Returns: Updated MealPlan

POST /api/plan/{plan_id}/regenerate-day
  Regenerate suggestion for a specific day
  Body: { "day": "tuesday", "reason": "want something faster" }
  Returns: List of 3 alternative recipe suggestions
```

### Recipes

```
GET /api/recipes
  List recipes with filtering
  Query params: cuisine, max_time, tags, search
  Returns: Paginated list of RecipeSummary

GET /api/recipes/{recipe_id}
  Get full recipe details
  Returns: Recipe with ingredients and instructions

POST /api/recipes/suggest
  Get recipe suggestions based on constraints
  Body: { "ingredients_on_hand": [...], "max_time": 30, "cuisine": "italian" }
  Returns: List of matching recipes with relevance scores
```

### Grocery

```
GET /api/plan/{plan_id}/grocery
  Get consolidated grocery list for a meal plan
  Returns: GroceryList grouped by category

PATCH /api/plan/{plan_id}/grocery
  Mark items as owned/purchased
  Body: { "item_ids": [...], "status": "owned" }
  Returns: Updated GroceryList
```

### Feedback

```
POST /api/feedback
  Submit feedback for a cooked meal
  Body: { "recipe_id": 42, "meal_plan_id": 1, "rating": 4, "would_make_again": true, "notes": "..." }
  Returns: Feedback confirmation
```

---

## Frontend Pages

### Page Structure

```
/                       → Dashboard (current week's plan + quick actions)
/onboarding            → First-time user profile setup (multi-step form)
/plan                  → Current week meal plan view
/plan/[weekStart]      → Specific week's plan
/recipe/[id]           → Full recipe detail page
/grocery               → Current grocery list
/history               → Past meal plans and feedback
/settings              → Profile preferences editor
```

### Key UI Components

1. **MealPlanCard**: Shows a single day's meal with recipe thumbnail, title, time, and swap/regenerate buttons

2. **RecipeDetail**: Full recipe view with:
   - Hero image (placeholder for MVP)
   - Ingredient list with checkboxes
   - Step-by-step instructions with timers
   - Scaling controls (adjust servings)
   - "I cooked this" feedback button

3. **GroceryList**: Grouped by store section with:
   - Checkboxes for purchased items
   - Recipe attribution badges
   - "Copy to clipboard" for sharing

4. **PreferenceForm**: Multi-section form for:
   - Dietary restrictions (checkboxes)
   - Disliked ingredients (tag input)
   - Cuisine preferences (ranked drag-drop)
   - Time/skill constraints (sliders)

---

## Project Structure

```
meal-planner/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, CORS, middleware
│   │   ├── config.py            # Settings, environment variables
│   │   ├── database.py          # SQLAlchemy setup, session management
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # UserProfile model
│   │   │   ├── recipe.py        # Recipe model
│   │   │   ├── plan.py          # MealPlan, GroceryList models
│   │   │   └── feedback.py      # Feedback model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # Pydantic schemas for API
│   │   │   ├── recipe.py
│   │   │   ├── plan.py
│   │   │   └── grocery.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── profile.py       # /api/profile routes
│   │   │   ├── recipes.py       # /api/recipes routes
│   │   │   ├── plan.py          # /api/plan routes
│   │   │   └── feedback.py      # /api/feedback routes
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm.py           # Ollama/Bedrock abstraction
│   │   │   ├── embeddings.py    # Embedding generation (Ollama/Bedrock)
│   │   │   ├── vector_store.py  # Chroma/Pinecone abstraction
│   │   │   ├── database.py      # SQLite/DynamoDB abstraction
│   │   │   ├── rag.py           # RAG pipeline orchestration
│   │   │   ├── planner.py       # Meal plan generation logic
│   │   │   └── grocery.py       # Grocery consolidation logic
│   │   └── prompts/
│   │       ├── plan_generation.txt
│   │       ├── recipe_adaptation.txt
│   │       └── grocery_consolidation.txt
│   ├── scripts/
│   │   ├── init_db.py           # Create tables
│   │   ├── seed_recipes.py      # Load initial recipe corpus
│   │   └── test_llm.py          # Verify Ollama connection
│   ├── data/
│   │   └── recipes/             # JSON recipe files for seeding
│   ├── tests/
│   │   └── ...
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx         # Dashboard
│   │   │   ├── onboarding/
│   │   │   ├── plan/
│   │   │   ├── recipe/
│   │   │   ├── grocery/
│   │   │   └── settings/
│   │   ├── components/
│   │   │   ├── MealPlanCard.tsx
│   │   │   ├── RecipeDetail.tsx
│   │   │   ├── GroceryList.tsx
│   │   │   ├── PreferenceForm.tsx
│   │   │   └── ...
│   │   ├── lib/
│   │   │   ├── api.ts           # API client
│   │   │   └── types.ts         # TypeScript types
│   │   └── hooks/
│   │       └── ...
│   ├── package.json
│   └── tsconfig.json
├── infra/
│   ├── main.tf                  # Provider config, backend
│   ├── variables.tf             # Input variables
│   ├── outputs.tf               # Output values
│   ├── lambda.tf                # Lambda function + IAM
│   ├── api_gateway.tf           # API Gateway config
│   ├── dynamodb.tf              # DynamoDB table
│   ├── secrets.tf               # Secrets Manager
│   └── terraform.tfvars.example # Example variables (gitignored actual)
├── docker-compose.yml           # Local containerized setup
├── Makefile                     # Common commands
└── README.md
```

---

## Development Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up project structure (backend + frontend scaffolding)
- [ ] Configure SQLite + SQLAlchemy models
- [ ] Set up Ollama locally with qwen2.5:14b
- [ ] Create basic FastAPI endpoints (health check, profile CRUD)
- [ ] Build user profile onboarding UI

### Phase 2: Recipe Corpus (Week 2)
- [ ] Define recipe JSON schema
- [ ] Write recipe scraping/ingestion scripts
- [ ] Curate initial 50 recipes manually
- [ ] Set up Chroma vector store
- [ ] Implement embedding generation pipeline
- [ ] Build recipe browsing UI

### Phase 3: RAG + Planning (Week 3)
- [ ] Implement RAG retrieval with filtering
- [ ] Build meal plan generation prompts
- [ ] Create plan generation endpoint
- [ ] Build weekly plan UI with swap functionality
- [ ] Add "regenerate day" feature

### Phase 4: Grocery + Feedback (Week 4)
- [ ] Implement grocery consolidation logic
- [ ] Build grocery list UI
- [ ] Add feedback submission flow
- [ ] Integrate feedback into retrieval ranking
- [ ] Polish and bug fixes

### Phase 5: Portfolio Polish (Week 5)
- [ ] Write README with architecture diagrams
- [ ] Add deployment instructions (local + cloud)
- [ ] Create demo video/screenshots
- [ ] Document cost analysis
- [ ] Deploy to free tier hosting

---

## Local Development Setup

### Prerequisites

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull qwen2.5:14b
ollama pull nomic-embed-text

# Verify
ollama list

# Start Milvus (via Docker)
# Option 1: Milvus Lite (embedded, simpler for dev)
pip install pymilvus[lite]

# Option 2: Full Milvus (closer to production)
curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh
bash standalone_embed.sh start
# Milvus will be available at localhost:19530
```

### Docker Compose (Full Local Stack)

```yaml
# docker-compose.yml
version: '3.8'

services:
  milvus:
    image: milvusdb/milvus:v2.4-latest
    container_name: milvus-standalone
    environment:
      ETCD_USE_EMBED: "true"
      ETCD_DATA_DIR: "/var/lib/milvus/etcd"
      COMMON_STORAGETYPE: "local"
    volumes:
      - milvus_data:/var/lib/milvus
    ports:
      - "19530:19530"
      - "9091:9091"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9091/healthz"]
      interval: 30s
      start_period: 90s
      timeout: 20s
      retries: 3

volumes:
  milvus_data:
```

```bash
# Start Milvus
docker-compose up -d milvus

# Verify Milvus is running
curl http://localhost:9091/healthz
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Seed recipes
python scripts/seed_recipes.py

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Available at http://localhost:3000
```

### Environment Variables

```bash
# backend/.env (local development)
ENVIRONMENT=local
DATABASE_URL=sqlite:///./meal_planner.db
MILVUS_HOST=localhost
MILVUS_PORT=19530
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b
OLLAMA_EMBED_MODEL=nomic-embed-text

# For local testing with cloud services
ZILLIZ_ENDPOINT=https://xxx.zillizcloud.com
ZILLIZ_API_KEY=your-zilliz-key
AWS_REGION=us-east-1

# backend/.env.production (or use AWS Secrets Manager)
ENVIRONMENT=production
DYNAMODB_TABLE=MealPlannerTable
ZILLIZ_ENDPOINT={{from-secrets-manager}}
ZILLIZ_API_KEY={{from-secrets-manager}}
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
AWS_REGION=us-east-1

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# frontend/.env.production
NEXT_PUBLIC_API_URL=https://xxxxx.execute-api.us-east-1.amazonaws.com/prod
```

---

## Cloud Deployment (AWS Serverless)

### Architecture Overview

```
                                    ┌─────────────────┐
                                    │   CloudFront    │
                                    │   (CDN + SSL)   │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┴────────────────────────┐
                    │                                                  │
                    ▼                                                  ▼
          ┌─────────────────┐                               ┌─────────────────┐
          │  S3 / Amplify   │                               │   API Gateway   │
          │  (Static Site)  │                               │   (REST API)    │
          └─────────────────┘                               └────────┬────────┘
                                                                     │
                                                                     ▼
                                                            ┌─────────────────┐
                                                            │     Lambda      │
                                                            │   (FastAPI +    │
                                                            │    Mangum)      │
                                                            └────────┬────────┘
                                                                     │
                    ┌────────────────────────┬────────────────────────┼────────────────────────┐
                    │                        │                        │                        │
                    ▼                        ▼                        ▼                        ▼
          ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
          │    DynamoDB     │      │    Pinecone     │      │ Amazon Bedrock  │      │   Cognito       │
          │  (app data)     │      │   (vectors)     │      │   (Claude LLM)  │      │  (auth, opt.)   │
          └─────────────────┘      └─────────────────┘      └─────────────────┘      └─────────────────┘
```

### Lambda Deployment with Mangum

Mangum is an adapter that lets FastAPI run in Lambda unchanged:

```python
# backend/app/main.py
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

# ... all your existing routes ...

# Lambda handler
handler = Mangum(app, lifespan="off")
```

### DynamoDB Table Design

Single-table design for efficient access patterns:

```
Table: MealPlannerTable
Partition Key: PK (String)
Sort Key: SK (String)
GSI1: GSI1PK / GSI1SK (for alternate access patterns)

Entity Types:
┌──────────────────┬─────────────────────────┬─────────────────────────┐
│ Entity           │ PK                      │ SK                      │
├──────────────────┼─────────────────────────┼─────────────────────────┤
│ UserProfile      │ USER#<user_id>          │ PROFILE                 │
│ Recipe           │ RECIPE#<recipe_id>      │ METADATA                │
│ MealPlan         │ USER#<user_id>          │ PLAN#<week_start>       │
│ Feedback         │ USER#<user_id>          │ FEEDBACK#<timestamp>    │
│ GroceryList      │ PLAN#<plan_id>          │ GROCERY                 │
└──────────────────┴─────────────────────────┴─────────────────────────┘

GSI1 (for queries like "get all feedback for a recipe"):
┌──────────────────┬─────────────────────────┬─────────────────────────┐
│ Entity           │ GSI1PK                  │ GSI1SK                  │
├──────────────────┼─────────────────────────┼─────────────────────────┤
│ Feedback         │ RECIPE#<recipe_id>      │ FEEDBACK#<timestamp>    │
│ Recipe           │ CUISINE#<cuisine>       │ RECIPE#<recipe_id>      │
└──────────────────┴─────────────────────────┴─────────────────────────┘
```

### Infrastructure as Code (Terraform)

Project structure for Terraform:
```
infra/
├── main.tf              # Provider config, backend
├── variables.tf         # Input variables
├── outputs.tf           # Output values (API URL, etc.)
├── lambda.tf            # Lambda function + IAM
├── api_gateway.tf       # API Gateway configuration
├── dynamodb.tf          # DynamoDB table
├── secrets.tf           # Secrets Manager
├── s3.tf                # S3 bucket for frontend (optional)
├── cloudfront.tf        # CloudFront distribution (optional)
└── terraform.tfvars     # Variable values (gitignored)
```

```hcl
# infra/main.tf
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Remote state (optional but recommended)
  backend "s3" {
    bucket = "your-terraform-state-bucket"
    key    = "meal-planner/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "meal-planner"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
```

```hcl
# infra/variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "zilliz_endpoint" {
  description = "Zilliz Cloud endpoint URL"
  type        = string
  sensitive   = true
}

variable "zilliz_api_key" {
  description = "Zilliz Cloud API key"
  type        = string
  sensitive   = true
}
```

```hcl
# infra/dynamodb.tf
resource "aws_dynamodb_table" "meal_planner" {
  name         = "MealPlannerTable-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "GSI1PK"
    type = "S"
  }

  attribute {
    name = "GSI1SK"
    type = "S"
  }

  global_secondary_index {
    name            = "GSI1"
    hash_key        = "GSI1PK"
    range_key       = "GSI1SK"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }
}
```

```hcl
# infra/lambda.tf
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../backend"
  output_path = "${path.module}/lambda.zip"
  excludes    = ["__pycache__", "*.pyc", ".env", "venv", ".pytest_cache"]
}

resource "aws_lambda_function" "api" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "meal-planner-api-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "app.main.handler"
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 512
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      ENVIRONMENT      = var.environment
      DYNAMODB_TABLE   = aws_dynamodb_table.meal_planner.name
      ZILLIZ_ENDPOINT  = var.zilliz_endpoint
      BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_policy]
}

resource "aws_iam_role" "lambda_role" {
  name = "meal-planner-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "meal-planner-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.meal_planner.arn,
          "${aws_dynamodb_table.meal_planner.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.zilliz.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
```

```hcl
# infra/api_gateway.tf
resource "aws_apigatewayv2_api" "api" {
  name          = "meal-planner-api-${var.environment}"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = ["*"]  # Restrict in production
    allow_methods = ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 300
  }
}

resource "aws_apigatewayv2_stage" "api" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      path           = "$context.path"
      status         = "$context.status"
      responseLength = "$context.responseLength"
    })
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "api" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/apigateway/meal-planner-${var.environment}"
  retention_in_days = 14
}
```

```hcl
# infra/secrets.tf
resource "aws_secretsmanager_secret" "zilliz" {
  name = "meal-planner/zilliz-${var.environment}"
}

resource "aws_secretsmanager_secret_version" "zilliz" {
  secret_id = aws_secretsmanager_secret.zilliz.id
  secret_string = jsonencode({
    endpoint = var.zilliz_endpoint
    api_key  = var.zilliz_api_key
  })
}
```

```hcl
# infra/outputs.tf
output "api_url" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_api.api.api_endpoint
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.meal_planner.name
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.api.function_name
}
```

### Deployment Commands

```bash
# Initialize Terraform (one-time)
cd infra
terraform init

# Preview changes
terraform plan -var-file="terraform.tfvars"

# Apply changes
terraform apply -var-file="terraform.tfvars"

# Destroy (when needed)
terraform destroy -var-file="terraform.tfvars"
```

### Lambda Packaging Note

For production, you'll need to package dependencies with your Lambda. Options:

1. **Lambda Layer** (recommended):
```bash
# Create layer with dependencies
pip install -r requirements.txt -t python/
zip -r layer.zip python/
aws lambda publish-layer-version --layer-name meal-planner-deps --zip-file fileb://layer.zip
```

2. **Container Image** (for larger dependencies):
```dockerfile
FROM public.ecr.aws/lambda/python:3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["app.main.handler"]
```

Update the Terraform to use `image_uri` instead of `filename` for container approach.

### Frontend Deployment (Amplify)

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize (one-time)
cd frontend
amplify init

# Add hosting
amplify add hosting
# Select: Hosting with Amplify Console
# Select: Continuous deployment (Git-based)

# Deploy
amplify publish
```

Or use S3 + CloudFront manually:
```bash
# Build Next.js as static export
npm run build
# next.config.js must have: output: 'export'

# Sync to S3
aws s3 sync out/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Environment Configuration

```bash
# AWS Secrets Manager (for sensitive values)
aws secretsmanager create-secret \
  --name meal-planner/zilliz \
  --secret-string '{"endpoint":"https://xxx.zillizcloud.com","api_key":"your-zilliz-key"}'

# Lambda environment variables (non-sensitive)
# Set in Terraform variables or via AWS Console

# Frontend environment (.env.production)
NEXT_PUBLIC_API_URL=https://xxxxx.execute-api.us-east-1.amazonaws.com/prod
```

### Cost Estimation (Low Traffic)

| Service | Free Tier | Est. Monthly Cost |
|---------|-----------|-------------------|
| Lambda | 1M requests, 400K GB-seconds | $0 |
| API Gateway | 1M API calls | $0 |
| DynamoDB | 25 GB storage, 25 WCU/RCU | $0 |
| Amplify Hosting | 1000 build min, 15 GB served | $0 |
| Bedrock (Claude) | None | ~$1-5 (usage-based) |
| Zilliz Cloud | 2 collections, 500K vectors | $0 |
| **Total** | | **~$1-5/month** |

At low personal usage (a few meal plans per week), your only real cost is Bedrock inference.

---

## Onion Architecture

The application follows onion (clean) architecture to enforce separation of concerns and make infrastructure swappable. Dependencies point inward—outer layers depend on inner layers, never the reverse.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Infrastructure Layer                              │
│  (FastAPI routes, Milvus/Zilliz, DynamoDB/SQLite, Ollama/Bedrock, AWS)     │
├─────────────────────────────────────────────────────────────────────────────┤
│                            Application Layer                                 │
│  (Use cases: GenerateMealPlan, GetGroceryList, SubmitFeedback)             │
├─────────────────────────────────────────────────────────────────────────────┤
│                            Domain Layer                                      │
│  (Entities: Recipe, MealPlan, UserProfile, GroceryList)                     │
│  (Interfaces: IRecipeRepository, IVectorStore, ILLMService)                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Project Structure (Onion)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app setup, middleware
│   ├── config.py                    # Settings via pydantic-settings
│   │
│   ├── domain/                      # CORE - No external dependencies
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── recipe.py            # Recipe dataclass/model
│   │   │   ├── meal_plan.py         # MealPlan, MealSlot
│   │   │   ├── user_profile.py      # UserProfile, DietaryRestriction
│   │   │   ├── grocery.py           # GroceryList, GroceryItem
│   │   │   └── feedback.py          # Feedback
│   │   ├── interfaces/              # Abstract interfaces (ports)
│   │   │   ├── __init__.py
│   │   │   ├── recipe_repository.py # IRecipeRepository
│   │   │   ├── user_repository.py   # IUserRepository
│   │   │   ├── plan_repository.py   # IMealPlanRepository
│   │   │   ├── vector_store.py      # IVectorStore
│   │   │   ├── llm_service.py       # ILLMService
│   │   │   └── embedding_service.py # IEmbeddingService
│   │   └── exceptions.py            # Domain-specific exceptions
│   │
│   ├── application/                 # USE CASES - Orchestrates domain
│   │   ├── __init__.py
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   ├── generate_meal_plan.py
│   │   │   ├── swap_meal.py
│   │   │   ├── get_grocery_list.py
│   │   │   ├── suggest_recipes.py
│   │   │   ├── submit_feedback.py
│   │   │   └── manage_profile.py
│   │   ├── dto/                     # Data transfer objects
│   │   │   ├── __init__.py
│   │   │   ├── requests.py          # Input DTOs
│   │   │   └── responses.py         # Output DTOs
│   │   └── services/                # Application services
│   │       ├── __init__.py
│   │       ├── rag_service.py       # RAG orchestration
│   │       └── grocery_service.py   # Grocery consolidation logic
│   │
│   └── infrastructure/              # ADAPTERS - External implementations
│       ├── __init__.py
│       ├── api/                     # FastAPI routes (primary adapter)
│       │   ├── __init__.py
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── profile.py
│       │   │   ├── recipes.py
│       │   │   ├── plan.py
│       │   │   └── feedback.py
│       │   ├── dependencies.py      # DI container
│       │   └── middleware.py
│       ├── persistence/             # Database adapters
│       │   ├── __init__.py
│       │   ├── sqlite/
│       │   │   ├── __init__.py
│       │   │   ├── models.py        # SQLAlchemy models
│       │   │   ├── recipe_repository.py
│       │   │   ├── user_repository.py
│       │   │   └── plan_repository.py
│       │   └── dynamodb/
│       │       ├── __init__.py
│       │       ├── recipe_repository.py
│       │       ├── user_repository.py
│       │       └── plan_repository.py
│       ├── vector/                  # Vector store adapters
│       │   ├── __init__.py
│       │   ├── milvus_store.py      # Local Milvus
│       │   └── zilliz_store.py      # Zilliz Cloud (same SDK, different config)
│       ├── llm/                     # LLM adapters
│       │   ├── __init__.py
│       │   ├── ollama_service.py
│       │   └── bedrock_service.py
│       ├── embeddings/              # Embedding adapters
│       │   ├── __init__.py
│       │   ├── ollama_embeddings.py
│       │   └── bedrock_embeddings.py
│       └── prompts/                 # Prompt templates
│           ├── plan_generation.txt
│           ├── recipe_adaptation.txt
│           └── grocery_consolidation.txt
```

### Domain Layer (Core)

The domain layer has zero external dependencies. It defines entities and interfaces only.

```python
# app/domain/entities/recipe.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Ingredient:
    item: str
    quantity: float
    unit: str
    preparation: Optional[str] = None
    category: str = "other"
    optional: bool = False

@dataclass
class Recipe:
    id: str
    title: str
    description: str
    cuisine: str
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    difficulty: str
    ingredients: list[Ingredient]
    instructions: list[str]
    tags: list[str]
    source_url: Optional[str] = None
    
    @property
    def total_time_minutes(self) -> int:
        return self.prep_time_minutes + self.cook_time_minutes
    
    def scale(self, new_servings: int) -> "Recipe":
        """Return a new Recipe scaled to different servings."""
        factor = new_servings / self.servings
        scaled_ingredients = [
            Ingredient(
                item=i.item,
                quantity=round(i.quantity * factor, 2),
                unit=i.unit,
                preparation=i.preparation,
                category=i.category,
                optional=i.optional
            )
            for i in self.ingredients
        ]
        return Recipe(
            id=self.id,
            title=self.title,
            description=self.description,
            cuisine=self.cuisine,
            prep_time_minutes=self.prep_time_minutes,
            cook_time_minutes=self.cook_time_minutes,
            servings=new_servings,
            difficulty=self.difficulty,
            ingredients=scaled_ingredients,
            instructions=self.instructions,
            tags=self.tags,
            source_url=self.source_url
        )
```

```python
# app/domain/interfaces/recipe_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from ..entities.recipe import Recipe

class IRecipeRepository(ABC):
    @abstractmethod
    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        pass
    
    @abstractmethod
    def get_all(self, limit: int = 100, offset: int = 0) -> list[Recipe]:
        pass
    
    @abstractmethod
    def get_by_ids(self, recipe_ids: list[str]) -> list[Recipe]:
        pass
    
    @abstractmethod
    def save(self, recipe: Recipe) -> None:
        pass
    
    @abstractmethod
    def search(
        self,
        cuisine: Optional[str] = None,
        max_time: Optional[int] = None,
        tags: Optional[list[str]] = None,
        exclude_ingredients: Optional[list[str]] = None
    ) -> list[Recipe]:
        pass
```

```python
# app/domain/interfaces/vector_store.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class VectorSearchResult:
    id: str
    score: float
    metadata: dict

class IVectorStore(ABC):
    @abstractmethod
    def upsert(self, id: str, embedding: list[float], metadata: dict) -> None:
        pass
    
    @abstractmethod
    def query(
        self,
        embedding: list[float],
        top_k: int = 10,
        filter_expr: Optional[str] = None
    ) -> list[VectorSearchResult]:
        pass
    
    @abstractmethod
    def delete(self, id: str) -> None:
        pass
```

```python
# app/domain/interfaces/llm_service.py
from abc import ABC, abstractmethod
from typing import Optional

class ILLMService(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        pass
    
    @abstractmethod
    def generate_json(self, prompt: str, system: Optional[str] = None) -> dict:
        """Generate and parse JSON response."""
        pass
```

### Application Layer (Use Cases)

Use cases orchestrate domain logic. They depend only on domain interfaces, not implementations.

```python
# app/application/use_cases/generate_meal_plan.py
from dataclasses import dataclass
from datetime import date
from typing import Optional

from ...domain.entities.meal_plan import MealPlan, MealSlot
from ...domain.entities.user_profile import UserProfile
from ...domain.interfaces.recipe_repository import IRecipeRepository
from ...domain.interfaces.vector_store import IVectorStore
from ...domain.interfaces.llm_service import ILLMService
from ...domain.interfaces.embedding_service import IEmbeddingService
from ...domain.interfaces.plan_repository import IMealPlanRepository
from ..services.rag_service import RAGService

@dataclass
class GenerateMealPlanRequest:
    user_id: str
    week_start: date
    days_to_plan: list[str] = None  # e.g., ["monday", "tuesday", "thursday", "friday", "sunday"]
    
    def __post_init__(self):
        if self.days_to_plan is None:
            self.days_to_plan = ["monday", "tuesday", "thursday", "friday", "sunday"]

@dataclass
class GenerateMealPlanResponse:
    meal_plan: MealPlan
    reasoning: dict[str, str]  # day -> explanation

class GenerateMealPlanUseCase:
    def __init__(
        self,
        recipe_repo: IRecipeRepository,
        plan_repo: IMealPlanRepository,
        vector_store: IVectorStore,
        llm_service: ILLMService,
        embedding_service: IEmbeddingService,
        user_repo: "IUserRepository"
    ):
        self.recipe_repo = recipe_repo
        self.plan_repo = plan_repo
        self.rag_service = RAGService(vector_store, embedding_service, recipe_repo)
        self.llm_service = llm_service
        self.user_repo = user_repo
    
    def execute(self, request: GenerateMealPlanRequest) -> GenerateMealPlanResponse:
        # 1. Get user profile
        profile = self.user_repo.get_by_id(request.user_id)
        if not profile:
            raise ValueError(f"User {request.user_id} not found")
        
        # 2. Get recent meals to avoid repetition
        recent_plans = self.plan_repo.get_recent(request.user_id, weeks=2)
        recent_recipe_ids = self._extract_recent_recipe_ids(recent_plans)
        
        # 3. Use RAG to find candidate recipes
        candidates = self.rag_service.retrieve_candidates(
            profile=profile,
            exclude_ids=recent_recipe_ids,
            n_candidates=20
        )
        
        # 4. Use LLM to select and arrange meals
        prompt = self._build_prompt(profile, candidates, request.days_to_plan)
        response = self.llm_service.generate_json(prompt, system=PLANNER_SYSTEM_PROMPT)
        
        # 5. Build meal plan from LLM response
        meal_plan = self._build_meal_plan(request, response)
        
        # 6. Save and return
        self.plan_repo.save(meal_plan)
        
        return GenerateMealPlanResponse(
            meal_plan=meal_plan,
            reasoning={day: response[day]["reasoning"] for day in request.days_to_plan}
        )
    
    def _extract_recent_recipe_ids(self, plans: list[MealPlan]) -> list[str]:
        ids = []
        for plan in plans:
            for slot in plan.meals.values():
                if slot and slot.recipe_id:
                    ids.append(slot.recipe_id)
        return ids
    
    def _build_prompt(self, profile: UserProfile, candidates: list, days: list[str]) -> str:
        # Build prompt from template + data
        pass
    
    def _build_meal_plan(self, request: GenerateMealPlanRequest, response: dict) -> MealPlan:
        # Convert LLM response to MealPlan entity
        pass

PLANNER_SYSTEM_PROMPT = """You are a meal planning assistant. Select meals that:
1. Respect all dietary restrictions absolutely
2. Vary proteins across the week
3. Balance prep times (lighter meals on busy nights)
4. Match cuisine preferences when possible

Respond with valid JSON only."""
```

### Infrastructure Layer (Adapters)

Adapters implement domain interfaces with specific technologies.

```python
# app/infrastructure/vector/milvus_store.py
from pymilvus import MilvusClient
from typing import Optional

from ...domain.interfaces.vector_store import IVectorStore, VectorSearchResult

class MilvusVectorStore(IVectorStore):
    """Works with both local Milvus and Zilliz Cloud (same SDK)."""
    
    def __init__(
        self,
        uri: str,  # "http://localhost:19530" or "https://xxx.zillizcloud.com"
        token: Optional[str] = None,  # Required for Zilliz
        collection_name: str = "recipes",
        dimension: int = 768
    ):
        self.client = MilvusClient(uri=uri, token=token)
        self.collection_name = collection_name
        self.dimension = dimension
        self._ensure_collection()
    
    def _ensure_collection(self):
        if not self.client.has_collection(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=self.dimension,
                metric_type="COSINE"
            )
    
    def upsert(self, id: str, embedding: list[float], metadata: dict) -> None:
        self.client.upsert(
            collection_name=self.collection_name,
            data=[{"id": id, "vector": embedding, **metadata}]
        )
    
    def query(
        self,
        embedding: list[float],
        top_k: int = 10,
        filter_expr: Optional[str] = None
    ) -> list[VectorSearchResult]:
        results = self.client.search(
            collection_name=self.collection_name,
            data=[embedding],
            limit=top_k,
            filter=filter_expr,
            output_fields=["*"]
        )
        
        return [
            VectorSearchResult(
                id=hit["id"],
                score=hit["distance"],
                metadata={k: v for k, v in hit["entity"].items() if k not in ["id", "vector"]}
            )
            for hit in results[0]
        ]
    
    def delete(self, id: str) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            filter=f'id == "{id}"'
        )
```

```python
# app/infrastructure/llm/ollama_service.py
import requests
import json
from typing import Optional

from ...domain.interfaces.llm_service import ILLMService

class OllamaLLMService(ILLMService):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
    
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "system": system or "",
                "stream": False,
                "options": {"temperature": 0.7}
            }
        )
        response.raise_for_status()
        return response.json()["response"]
    
    def generate_json(self, prompt: str, system: Optional[str] = None) -> dict:
        # Add JSON instruction to prompt
        json_prompt = f"{prompt}\n\nRespond with valid JSON only, no markdown or explanation."
        response_text = self.generate(json_prompt, system)
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        return json.loads(response_text.strip())
```

```python
# app/infrastructure/llm/bedrock_service.py
import boto3
import json
from typing import Optional

from ...domain.interfaces.llm_service import ILLMService

class BedrockLLMService(ILLMService):
    def __init__(self, model_id: str, region: str = "us-east-1"):
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = model_id
    
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system:
            body["system"] = system
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]
    
    def generate_json(self, prompt: str, system: Optional[str] = None) -> dict:
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        response_text = self.generate(json_prompt, system)
        return json.loads(response_text.strip())
```

### Dependency Injection Container

Wire everything together based on environment:

```python
# app/infrastructure/api/dependencies.py
from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from ...config import get_settings, Settings
from ...domain.interfaces.recipe_repository import IRecipeRepository
from ...domain.interfaces.vector_store import IVectorStore
from ...domain.interfaces.llm_service import ILLMService
from ...domain.interfaces.embedding_service import IEmbeddingService

from ..persistence.sqlite.recipe_repository import SQLiteRecipeRepository
from ..persistence.dynamodb.recipe_repository import DynamoDBRecipeRepository
from ..vector.milvus_store import MilvusVectorStore
from ..llm.ollama_service import OllamaLLMService
from ..llm.bedrock_service import BedrockLLMService
from ..embeddings.ollama_embeddings import OllamaEmbeddingService
from ..embeddings.bedrock_embeddings import BedrockEmbeddingService

@lru_cache()
def get_vector_store(settings: Settings = Depends(get_settings)) -> IVectorStore:
    if settings.environment == "production":
        return MilvusVectorStore(
            uri=settings.zilliz_endpoint,
            token=settings.zilliz_api_key,
            collection_name="recipes"
        )
    return MilvusVectorStore(
        uri=f"http://{settings.milvus_host}:{settings.milvus_port}",
        collection_name="recipes"
    )

@lru_cache()
def get_llm_service(settings: Settings = Depends(get_settings)) -> ILLMService:
    if settings.environment == "production":
        return BedrockLLMService(
            model_id=settings.bedrock_model_id,
            region=settings.aws_region
        )
    return OllamaLLMService(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model
    )

@lru_cache()
def get_embedding_service(settings: Settings = Depends(get_settings)) -> IEmbeddingService:
    if settings.environment == "production":
        return BedrockEmbeddingService(region=settings.aws_region)
    return OllamaEmbeddingService(
        base_url=settings.ollama_base_url,
        model=settings.ollama_embed_model
    )

@lru_cache()
def get_recipe_repository(settings: Settings = Depends(get_settings)) -> IRecipeRepository:
    if settings.environment == "production":
        return DynamoDBRecipeRepository(
            table_name=settings.dynamodb_table,
            region=settings.aws_region
        )
    return SQLiteRecipeRepository(db_url=settings.database_url)

# Type aliases for cleaner route signatures
VectorStore = Annotated[IVectorStore, Depends(get_vector_store)]
LLMService = Annotated[ILLMService, Depends(get_llm_service)]
EmbeddingService = Annotated[IEmbeddingService, Depends(get_embedding_service)]
RecipeRepo = Annotated[IRecipeRepository, Depends(get_recipe_repository)]
```

### Route Example

```python
# app/infrastructure/api/routes/plan.py
from fastapi import APIRouter, Depends
from datetime import date

from ....application.use_cases.generate_meal_plan import (
    GenerateMealPlanUseCase,
    GenerateMealPlanRequest,
    GenerateMealPlanResponse
)
from ..dependencies import VectorStore, LLMService, EmbeddingService, RecipeRepo, UserRepo, PlanRepo

router = APIRouter(prefix="/api/plan", tags=["Meal Plans"])

@router.post("/generate", response_model=GenerateMealPlanResponse)
def generate_meal_plan(
    week_start: date,
    user_id: str,  # In production, get from auth token
    vector_store: VectorStore,
    llm_service: LLMService,
    embedding_service: EmbeddingService,
    recipe_repo: RecipeRepo,
    user_repo: UserRepo,
    plan_repo: PlanRepo
):
    use_case = GenerateMealPlanUseCase(
        recipe_repo=recipe_repo,
        plan_repo=plan_repo,
        vector_store=vector_store,
        llm_service=llm_service,
        embedding_service=embedding_service,
        user_repo=user_repo
    )
    
    request = GenerateMealPlanRequest(user_id=user_id, week_start=week_start)
    return use_case.execute(request)
```

---

## Quality Checklist

### Recipe Quality
- [ ] Each recipe tested by at least one person
- [ ] Clear, numbered instructions (not walls of text)
- [ ] Ingredient quantities are precise
- [ ] Prep/cook times are realistic
- [ ] Difficulty ratings are consistent

### LLM Output Quality
- [ ] Plans respect all dietary restrictions 100%
- [ ] Variety across the week (no protein repeats on adjacent days)
- [ ] Time constraints honored
- [ ] Grocery list quantities are correct after consolidation
- [ ] Graceful handling of edge cases (no recipes match)

### Portfolio Quality
- [ ] README explains the "why" not just the "what"
- [ ] Architecture decisions are documented
- [ ] Code is clean and commented where non-obvious
- [ ] Demo works reliably (no broken states)
- [ ] Cost analysis shows real numbers

---

## Open Questions / Future Considerations

1. **Recipe scaling**: How to handle halving/doubling recipes with odd quantities?
2. **Leftover planning**: Can we suggest meals that reuse ingredients from previous days?
3. **Seasonal ingredients**: Should retrieval prefer in-season produce?
4. **Batch cooking**: How to represent "make double, eat twice" scenarios?
5. **Nutritional tracking**: Add calorie/macro info? (scope creep risk)

---

## Appendix: Sample Recipe JSON

```json
{
  "title": "Sheet Pan Chicken Fajitas",
  "description": "Easy weeknight fajitas with minimal cleanup. Chicken and vegetables roast together on one pan.",
  "cuisine": "mexican",
  "prep_time_minutes": 15,
  "cook_time_minutes": 25,
  "servings": 4,
  "difficulty": "easy",
  "ingredients": [
    {"item": "chicken breast", "quantity": 1.5, "unit": "lbs", "preparation": "sliced into strips", "category": "protein"},
    {"item": "bell peppers", "quantity": 3, "unit": "whole", "preparation": "sliced", "category": "produce"},
    {"item": "onion", "quantity": 1, "unit": "large", "preparation": "sliced", "category": "produce"},
    {"item": "olive oil", "quantity": 3, "unit": "tbsp", "category": "pantry"},
    {"item": "chili powder", "quantity": 2, "unit": "tsp", "category": "pantry"},
    {"item": "cumin", "quantity": 1, "unit": "tsp", "category": "pantry"},
    {"item": "garlic powder", "quantity": 1, "unit": "tsp", "category": "pantry"},
    {"item": "salt", "quantity": 1, "unit": "tsp", "category": "pantry"},
    {"item": "flour tortillas", "quantity": 8, "unit": "small", "category": "pantry"}
  ],
  "instructions": [
    "Preheat oven to 400°F (200°C). Line a large sheet pan with parchment paper.",
    "In a large bowl, combine olive oil, chili powder, cumin, garlic powder, and salt.",
    "Add sliced chicken, peppers, and onion to the bowl. Toss until everything is evenly coated.",
    "Spread the mixture in a single layer on the prepared sheet pan. Don't overcrowd.",
    "Roast for 20-25 minutes, stirring halfway through, until chicken is cooked through and vegetables are tender with charred edges.",
    "Warm tortillas in the microwave for 30 seconds wrapped in a damp paper towel.",
    "Serve chicken and vegetables in tortillas with your favorite toppings."
  ],
  "tags": ["quick", "one-pan", "meal-prep-friendly", "gluten-free-adaptable"],
  "source_url": null,
  "source_name": "Original"
}
```