FROM python:3.13.5-slim

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

WORKDIR /action

# Install PDM
RUN pip install --upgrade pip && pip install pdm

# Copy pyproject.toml and README.md
COPY pyproject.toml README.md ./

# Convert Poetry pyproject.toml to PDM format (if needed)
RUN pdm import -f poetry pyproject.toml || true

# Export env var to ignore venv creation
ENV PDM_IGNORE_VENV=1

# Now install dependencies system-wide (no venv)
RUN pdm install

# Copy the rest of the code to /action
COPY colorblind_snapshot_analyzer colorblind_snapshot_analyzer

# Set PYTHONPATH so Python can find your package
ENV PYTHONPATH=/action

# Set entrypoint to run your main module
ENTRYPOINT ["python", "-m", "colorblind_snapshot_analyzer.main"]
