FROM python:3.12-slim-bookworm

# Install uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv /usr/bin/

WORKDIR /app

# --- ADDED: Install system dependencies for building C extensions ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
# --------------------------------------------------------------------

# Prevent Python from buffering and writing .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Ensure uv uses the system python
ENV UV_SYSTEM_PYTHON=1

# 1. Copy only the dependency files
COPY pyproject.toml uv.lock ./

# 2. Export to a standard requirements.txt and install
# We use 'bash -c' to ensure the shell handles the redirection correctly
RUN uv export --format requirements-txt > requirements.txt && \
    uv pip install --system -r requirements.txt

# 3. Copy the rest of your app code
COPY . .

EXPOSE 5000

# Use 'python -m' to ensure we hit the right binary
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "app:app"]