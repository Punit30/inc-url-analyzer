FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container
COPY . /app

# Inter the application dependencies
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application
CMD ["sh", "run-local.sh"]