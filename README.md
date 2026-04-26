# Recipe Manager

A lightweight, self-hosted recipe manager built with FastAPI and React.

## Features

- **Recipe Management** — Create, edit, delete recipes with ingredients, steps, images, and nutrition info
- **Recipe Import** — Import recipes from URLs using [recipe-scrapers](https://github.com/hhursev/recipe-scrapers) with NLP ingredient parsing
- **Recipe Scaling** — Adjust servings and ingredient quantities scale automatically
- **Search & Filter** — Full-text search, filter by tags, categories, favorites, rating, and cook time
- **Tags & Categories** — Organize recipes with hierarchical categories and flat tags
- **Favorites & Ratings** — Bookmark and rate recipes (1–5 stars)
- **Public Sharing** — Share recipe URLs publicly without requiring login
- **Image Upload** — Upload recipe photos with automatic thumbnail generation
- **Auth** — JWT-based authentication with first-run admin setup
- **Responsive** — Works on desktop and mobile

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), SQLite |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query |
| Auth | JWT (access + refresh tokens), bcrypt |
| Deployment | Docker, nginx (reverse proxy) |

## Quick Start

### Docker (Production)

```bash
# Clone the repo
git clone https://github.com/brentonmdunn/recipe-manager-2.git
cd recipe-manager-2

# Bootstrap: generates .env with a random SECRET_KEY, ensures the
# stack_lab-internal network exists, builds images, and starts the stack.
./scripts/deploy.sh
```

Visit `http://localhost:3000` and create your admin account.

Point your Cloudflare Tunnel to `http://localhost:3000`.

To use a different port: `PORT=8080 docker compose up -d`

#### Updating a running deployment

```bash
# Pulls origin/main, rebuilds images, restarts the stack, prunes old images.
./scripts/update.sh

# Or skip the git pull (deploy local changes as-is):
./scripts/update.sh --no-pull
```

### Local Development

**Backend:**

```bash
cd backend
uv sync --group dev
uv run uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

App at http://localhost:5173 (proxies API to backend)

## Architecture

```
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Route handlers
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── repositories/    # Data access layer (repository pattern)
│   │   ├── services/        # Business logic layer
│   │   ├── utils/           # Security, pagination helpers
│   │   ├── config.py        # Settings via pydantic-settings
│   │   ├── database.py      # Async SQLAlchemy setup
│   │   ├── dependencies.py  # FastAPI dependency injection
│   │   └── main.py          # App entry point
│   └── tests/
├── frontend/
│   └── src/
│       ├── api/             # Typed API client
│       ├── components/      # React components
│       ├── contexts/        # Auth context
│       └── pages/           # Route pages
├── docker-compose.yml       # Production deployment
└── docker-compose.dev.yml   # Development (backend only)
```

**Pattern:** Routes → Services → Repositories → Database. Each layer depends on abstractions, injected via FastAPI's `Depends()`.

## API

Interactive API docs available at `/docs` (Swagger UI) when running the backend.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/recipes.db` | Database connection string |
| `SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `UPLOAD_DIR` | `./data/uploads` | Image upload directory |
| `PORT` | `3000` | Host port to expose the app on |

## License

MIT
