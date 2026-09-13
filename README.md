# InsightTaskLab

Web page that analyzing user reactions (facial expressions, keystroke patterns, mouse movement) while performing programming tasks. Part of a research project studying methods for eliciting user reactions, validated through a user study.

## Structure

```
InsightTaskLab/
├── backend/                 # Django app, API, DB models
│   └── emotion_detection/   # emotion recognition (DeepFace / FER / Py-Feat)
├── sandbox/                 # isolated C/C++ code execution (kept separate for security)
├── frontend/                # UI (code editor, camera/keyboard/mouse capture)
├── pyproject.toml           # root uv workspace (backend + sandbox)
├── uv.lock
├── docker-compose.yaml      # Postgres
├── .env.example             # template for required env vars
└── .pre-commit-config.yaml
```

## Setup

```bash
# 1. install dependencies (workspace: backend + sandbox)
uv sync --all-packages

# 2. create your local env file
cp .env.example .env

# 3. start the database
docker-compose up -d db

# 4. run migrations and start the backend
cd backend
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Admin panel: http://127.0.0.1:8000/admin/

## Code quality

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```
