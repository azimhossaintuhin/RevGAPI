# RevGAPI

**RevGAPI** is a SaaS review analysis API. Integrate it into your application, send customer reviews or feedback, and receive structured AI-powered insights — sentiment, summaries, pros/cons, action items, and more.

Built with FastAPI, PostgreSQL, and Google Gemini (via LangChain).

---

## What It Does

RevGAPI helps businesses understand customer reviews at scale. Your app sends a review text; RevGAPI returns a rich analysis object you can display in dashboards, trigger workflows from, or store for reporting.

**Typical use cases:**

- E-commerce product review widgets
- App store / Play Store feedback pipelines
- Support ticket sentiment routing
- Customer success dashboards
- Multi-language review ingestion (auto-detect + translate)

---

## How It Works (SaaS Flow)

```
1. Sign up          →  Create an account via the API
2. Get API key      →  Each user receives a unique API key
3. Send a review    →  POST review text from your application
4. Receive analysis →  Structured JSON with sentiment & insights
```

Your customers never touch the AI layer — they use **your product**, which calls RevGAPI behind the scenes using their API key.

---

## Analysis Output

Every analyzed review returns an `AgentOutput` object with:

| Field | Type | Description |
|-------|------|-------------|
| `feedback_language` | `string` | Detected language of the review |
| `translation` | `string \| null` | English translation (if not already English) |
| `sentiment` | `"positive" \| "negative" \| "neutral"` | Overall sentiment |
| `summary` | `string` | Short summary of the review |
| `pros` | `list[string]` | Positive points mentioned |
| `cons` | `list[string]` | Negative points mentioned |
| `action_items` | `list[string]` | Recommended actions for your team |
| `suggestions` | `list[string]` | Suggestions to improve the experience |
| `customer_repeats` | `boolean` | Likelihood the customer will return |
| `confidence_score` | `float` | Model confidence in the sentiment (0–1) |

**Example response shape:**

```json
{
  "feedback_language": "English",
  "translation": null,
  "sentiment": "positive",
  "summary": "Customer loves the product quality and pricing.",
  "pros": ["High quality", "Reasonable price"],
  "cons": [],
  "action_items": ["Maintain quality standards"],
  "suggestions": ["Invite customer to leave a public review"],
  "customer_repeats": true,
  "confidence_score": 0.98
}
```

---

## API Overview

### Account & Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/users/create` | — | Register a new account |
| `POST` | `/users/login` | — | Login (OAuth2: username = email) |
| `GET` | `/users/profile` | Bearer JWT | View account profile |
| `PUT` | `/users/profile` | Bearer JWT | Update profile / avatar |

### Review Analysis (Core Product)

Send review text from your application; RevGAPI returns structured `AgentOutput` JSON.

The analysis engine lives in `src/config/agents.py` (LangChain + Gemini). SaaS customers authenticate with their **API key** (`X-API-Key` header).

**Intended integration:**

```http
POST /analyze
X-API-Key: ari-api-<your-key>
Content-Type: application/json

{
  "review": "The product is great! I love the quality and the price is reasonable."
}
```

**Test the analysis engine locally:**

```bash
uv run python -m src.config.agents
```

---

## API Key & Usage Limits

Each registered user gets an **API key** (auto-generated on signup) with:

- **Per-day limit** — configurable token/request cap
- **Remaining tokens** — tracked per key
- **Active / deleted** flags — for key lifecycle management

Authenticate analysis requests with:

```http
X-API-Key: <your-api-key>
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, Uvicorn |
| Database | PostgreSQL 17, SQLAlchemy (async) |
| Auth | JWT (account management), API keys (SaaS usage) |
| AI | LangChain + Google Gemini |
| Password hashing | bcrypt |
| Tooling | uv, pytest, Docker Compose |

---

## Project Structure

```
revgapi/
├── main.py
├── docker-compose.yaml
├── pyproject.toml
├── .env.example
└── src/
    ├── config/
    │   ├── agents.py          # Review analysis LangChain pipeline
    │   └── database.py
    ├── core/
    │   ├── file_handler.py
    │   └── jwt_auth.py
    ├── dependencies/
    │   ├── get_user.py        # JWT auth
    │   └── user_api_key.py    # API key auth (SaaS)
    ├── models/
    │   └── users.py           # User + ApiKey models
    ├── routers/
    │   └── User_Routers.py
    ├── schemas/
    │   ├── Output.py          # AgentOutput schema
    │   └── User.py
    ├── services/
    │   └── Users.py
    ├── tests/
    └── media/
```

---

## Getting Started (Self-Hosted)

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- Docker & Docker Compose
- Google API key (Gemini)

### 1. Install

```bash
git clone <repository-url>
cd revgapi
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Google Gemini API key |
| `SECRET_KEY` | JWT signing secret |
| `ALLOWED_DOMAIN` | Public base URL (e.g. `http://localhost:8000`) |
| `POSTGRES_*` | Database credentials |
| `UPLOAD_FOLDER` | Media storage folder (e.g. `media`) |

### 3. Start database

```bash
docker compose up -d
```

### 4. Run the server

```bash
uv run fastapi dev main.py
```

- **API:** http://127.0.0.1:8000  
- **Docs:** http://127.0.0.1:8000/docs  

---

## Authentication

### JWT — account management

Use for signup, login, and profile routes via Swagger **Authorize** (email as `username`).

### API Key — review analysis (SaaS)

Use for programmatic access from your application:

```http
X-API-Key: ari-api-<hex>
```

---

## Testing

```bash
uv run pytest -v
```

---

## Roadmap

- [ ] Expose `/analyze` HTTP endpoint (API key protected)
- [ ] Usage metering & billing integration
- [ ] Webhook delivery for async analysis
- [ ] Batch review analysis endpoint

---

## License

MIT
