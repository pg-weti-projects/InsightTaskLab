# InsightTaskLab

Web page that analyzing user reactions (facial expressions, keystroke patterns, mouse movement) while performing programming tasks. Part of a research project studying methods for eliciting user reactions, validated through a user study.

## Structure

```
InsightTaskLab/
├── backend/                 # Django app, API, DB models
│   └── emotion_detection/   # emotion recognition (DeepFace / FER / Py-Feat)
├── frontend/                # UI (code editor, camera/keyboard/mouse capture)
├── install_runtime.py       # Piston runtime initialization
├── pyproject.toml           # root uv workspace backend
├── uv.lock
├── Dockerfile               # backend Docker image
├── docker-compose.yaml      # application services
├── .env.example             # template for required env vars
└── .pre-commit-config.yaml
```

## Setup

```bash
# 1. install dependencies (workspace: backend + sandbox)
uv sync --all-packages

# 2. create your local env file
cp .env.example .env

# 3. start the entire project
docker compose up --build
```

Admin panel: http://127.0.0.1:8000/admin/

Piston: http://127.0.0.1:2000/

## Frontend

The frontend is **not** containerized - run it directly with Node for a
faster dev loop (hot reload, devtools) while the backend services run in
Docker as above.

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173/.

The frontend calls the backend at `http://localhost:8000`, so
`docker compose up` must already be running

## Piston and C++ runtime
Available Piston runtimes can be checked with:
curl http://localhost:2000/api/v2/runtimes

To test C++ execution, use the Piston /api/v2/execute endpoint.

For example:
```bash
curl -s http://localhost:2000/api/v2/execute \
  -H 'Content-Type: application/json' \
  -d '{
    "language": "c++",
    "version": "10.2.0",
    "files": [
      {
        "name": "main.cpp",
        "content": "#include <iostream>\nint main() { std::cout << \"Hello World!\\n\"; return 0; }"
      }
    ]
  }'
```

## Code quality

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```
