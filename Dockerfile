FROM python:3.11.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set workdir to /action so code is not hidden by /github/workspace mount
WORKDIR /action

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies
RUN poetry install --no-interaction --no-root
RUN pip install daltonize

# Copy the rest of the code to /action
COPY colorblind_snapshot_analyzer colorblind_snapshot_analyzer

# Set entrypoint
ENTRYPOINT ["python", "-m", "colorblind_snapshot_analyzer.main"]
