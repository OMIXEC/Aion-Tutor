FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install uv for rapid dependency installation
RUN pip install uv

# Copy the pyproject.toml and uv.lock first to cache dependencies
COPY pyproject.toml uv.lock ./

# Install project dependencies
RUN uv pip install --system -e .

# Copy the rest of the application code
COPY . .

# The PORT environment variable is injected by Cloud Run
ENV PORT=8080
EXPOSE 8080

# Single-process ADK backend (all agents run in-process)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--ws", "websockets", "--timeout-keep-alive", "60"]
