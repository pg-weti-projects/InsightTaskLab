# InsightTaskLab

Web page that analyzing user reactions (facial expressions, keystroke patterns, mouse movement) while performing programming tasks. Part of a research project studying methods for eliciting user reactions, validated through a user study.

## Structure

```
InsightTaskLab/
├── backend/                 # Django app, API, DB models
│   └── emotion_detection/   # emotion recognition (DeepFace / FER / Py-Feat)
├── judge0/                  # Local Judge0 image and persistent configuration
├── frontend/                # UI (code editor, camera/keyboard/mouse capture)
├── pyproject.toml           # root uv workspace (backend + sandbox)
├── uv.lock
├── docker-compose.yaml      # Application, PostgreSQL and Judge0 services
├── .env.example             # template for required env vars
└── .pre-commit-config.yaml
```

## Setup

Install Python dependencies

~~~bash
uv sync --all-packages
~~~

Create the local environment file:

~~~bash
cp .env.example .env
~~~
Adjust the `.env` file if necessary.

Install Node.js 22+

Choose the installation method appropriate for your operating system:

* **Using nvm (Recommended for Linux / macOS / WSL):**
  ~~~bash
  nvm install 22
  nvm use 22
  ~~~
* **macOS (via Homebrew):**
  ~~~bash
  brew install node@22
  # Ensure it's in your PATH (add to ~/.zshrc if needed):
  export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
  ~~~
* **Other systems:** Download the installer directly from [nodejs.org](https://nodejs.org/).

Install frontend dependencies

~~~bash
cd frontend
npm install
cd ..
~~~

Start Docker services

From the project root, start the containers in detached mode:

~~~bash
docker compose up -d
~~~

The application and services will be available at:
* **Frontend:** `http://localhost:5173/`
* **Django Backend:** `http://localhost:8000/`
* **Django Admin:** `http://localhost:8000/admin/`

Verify the application

Open `http://localhost:5173/` in your browser.

## Code quality

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```
