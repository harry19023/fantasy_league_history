# Fantasy League History

A web application to display statistics and history for fantasy leagues, built with FastAPI and PostgreSQL.

## Features

- Track leagues, teams, players, and matchups
- Historical roster tracking
- Statistics and analytics
- RESTful API

## Tech Stack

- **Backend**: FastAPI (Python 3.14+)
- **Database**: PostgreSQL 15
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## Prerequisites

- Docker and Docker Compose installed
- Python 3.14+ (for local development without Docker)
- uv (Python package installer) - Install from https://github.com/astral-sh/uv

## Getting Started

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd fantasy_league_history
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Start the services:
```bash
docker-compose up --build
```

4. The API will be available at `http://localhost:8000`
5. API documentation will be available at `http://localhost:8000/docs`

### Local Development (Without Docker)

1. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

3. Set up PostgreSQL database and update `.env` with your database URL

4. Run the application:
```bash
uv run uvicorn app.main:app --reload
```

**Note**: Always use `uv run` for Python commands in this project to ensure correct environment and dependencies.

## Project Structure

```
fantasy_league_history/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   └── services/            # Business logic
├── tests/                   # Test files
├── docker/                  # Docker configuration
└── docker-compose.yml       # Docker Compose setup
```

## Database Models

- **League**: League information
- **Team**: Teams within leagues
- **Player**: Player information
- **Matchup**: Weekly matchups between teams
- **Roster**: Historical rosters (team + week + player)

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Development

### Running Tests

```bash
uv run pytest tests/ -v
```

### Code Formatting

```bash
uv run ruff format app/
```

### Linting

```bash
uv run ruff check app/
```

**Note**: All Python commands should be run with `uv run` to ensure the correct environment and dependencies are used.

## CI/CD

GitHub Actions workflow runs on push/PR to main/develop branches:
- Linting (flake8)
- Format checking (black)
- Tests (pytest)

## Next Steps

See `PROJECT_PLAN.md` for detailed development phases and roadmap.

## License

[Add your license here]
