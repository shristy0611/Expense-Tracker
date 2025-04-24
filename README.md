# Expense Tracker

A Flask-based application to upload, parse, and manage receipts with OCR, pagination, notes, and tags.

## Prerequisites

- Python 3.12
- Docker & Docker Compose (optional)
- Tesseract OCR (+ Japanese language pack)

## Installation & Running Locally

```bash
# Clone
git clone https://github.com/shristy0611/Expense-Tracker.git
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

## Interactive API Docs

You can explore and test the API interactively via Swagger UI:

```text
http://localhost:5000/apidocs/
```

## Postman Collection

Import the provided `postman_collection.json` into Postman for ready-to-use requests and examples.
To regenerate from the OpenAPI spec:

```bash
curl http://localhost:5000/apispec.json -o openapi.json
npx openapi2postmanv2 -s openapi.json -o postman_collection.json
```

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

## How to Contribute

- Fork the repository and create a feature branch.
- Install dependencies and run tests: `pytest`.
- Submit a pull request against `main` for peer review.

## Troubleshooting

- Ensure Tesseract OCR is installed: `tesseract --version`.
- Verify `UPLOAD_FOLDER` path in `.env`.
- For CI failures, check GitHub Actions logs in the repository.
