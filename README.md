# Expense Tracker API

A Flask-based service to upload and process receipt images, extract transaction data via OCR and RAG+LLM, and store structured records in a database.

## Features

- REST endpoints for health-check and transaction CRUD
- Flask application factory (`app.create_app`)
- SQLAlchemy models for transactions
- RAG+LLM-powered categorization and item inference
- FAISS index for similar receipt retrieval
- Modular agents (OCR, currency conversion, categorization, notifications)
- Unit tests with pytest and CI integration

## Prerequisites

- Python 3.10+
- Tesseract OCR installed (`brew install tesseract` on macOS)
- Dependencies in `requirements.txt`

## Installation

```bash
git clone <repo_url>
cd Expense-Tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and set:

```dotenv
DATABASE_URL=sqlite:///expense_tracker.db
FLASK_ENV=development
GEMINI_API_KEY=<your_gemini_key>
# Optional RAG settings
# RAG_MODEL_NAME=all-MiniLM-L6-v2
# RAG_INDEX_PATH=rag.index
# RAG_TEXTS_PATH=rag_texts.npy
# RAG_K=5
```

## Running

```bash
export FLASK_APP=app
flask run
```

## API Endpoints

- GET `/` — Health check
- GET `/transactions` — List all transactions
- POST `/transactions` — Create a new transaction (JSON payload)

## Testing

Run tests:
```bash
pytest tests --maxfail=1 --disable-warnings --quiet --cov=app --cov=services --cov-report=term-missing
```

## Deployment

- Build and push Docker image (`docker-compose up --build`)
- CI/CD via GitHub Actions
