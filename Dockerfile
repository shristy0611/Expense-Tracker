# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Install system dependencies for tesseract and build tools
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-jpn \
    libgl1 \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the app
COPY . .

# Add wait-for-it
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Expose port
EXPOSE 5000

# Entrypoint: wait for db, run migrations, then exec passed command (skip in CI if SKIP_DB_WAIT=1)
ENTRYPOINT ["/bin/bash", "-c", "if [ \"$SKIP_DB_WAIT\" != \"1\" ]; then /wait-for-it.sh db:5432 -t 60 -- flask db upgrade; fi && exec \"$@\"", "--"]
# Default command: start Flask server
CMD ["flask", "run", "--host=0.0.0.0"]
