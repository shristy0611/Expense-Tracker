# Expense Tracker

A Flask-based application to upload, parse, and manage receipts with OCR, pagination, notes, and tags.

## Prerequisites

- Python 3.12
- Docker & Docker Compose (optional)
- Tesseract OCR (+ Japanese language pack)

## Installation & Running Locally

```bash
# Clone
git clone https://your.repo/Expense-Tracker.git
cd Expense-Tracker

# Virtual env
env/bin/python -m venv venv
source venv/bin/activate

# Install deps
pip install -r requirements.txt

# Run migrations
FLASK_APP=run.py venv/bin/flask db upgrade

# Start the app
venv/bin/flask run --host=0.0.0.0
```

## Docker

```bash
docker-compose up --build
docker-compose down
```

## API Endpoints

- **POST /upload**: Upload receipt image (+optional `notes`, `tags` form fields)
- **GET /receipts**: List receipts with pagination (`page`, `per_page`)
- **GET /receipts/{id}**: Get details of a specific receipt

## Testing

```bash
# Run all tests
env/bin/pytest

# Run performance benchmarks
env/bin/pytest tests/test_perf_bench.py
```

## Performance Benchmark

### `pytest-benchmark`

Benchmarks are in `tests/test_perf_bench.py`, asserting 50 uploads and 50 list requests complete in under 60s.

### `wrk`

Example load test for listing receipts:

```bash
wrk -t2 -c10 -d30s http://localhost:5000/receipts?page=1&per_page=50
```

Example load test for uploading receipts (simple GET example; multipart upload scripting requires custom `wrk` script):

```bash
wrk -t2 -c5 -d30s http://localhost:5000/upload
```
