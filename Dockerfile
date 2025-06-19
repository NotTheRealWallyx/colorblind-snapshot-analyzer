FROM python:3.11.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set workdir to /action so code is not hidden by /github/workspace mount
WORKDIR /action

# Copy pyproject.toml, poetry.lock, README.md, and the package code
COPY pyproject.toml poetry.lock* README.md ./
COPY colorblind_snapshot_analyzer colorblind_snapshot_analyzer

# Install Python dependencies and project
RUN poetry install --no-interaction
RUN pip install daltonize

# Set PYTHONPATH so Python can find your package
ENV PYTHONPATH=/action

# Set entrypoint to use poetry run
ENTRYPOINT ["poetry", "run", "python", "-m", "colorblind_snapshot_analyzer.main"]
