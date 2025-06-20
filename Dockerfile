FROM python:3.13.5-slim

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

WORKDIR /action

# Install PDM
RUN pip install --upgrade pip && pip install pdm

# Copy pyproject.toml and README.md
COPY pyproject.toml README.md ./

# Convert Poetry pyproject.toml to PDM format (if needed)
RUN pdm import -f poetry pyproject.toml || true

# Lock dependencies
RUN PDM_IGNORE_VENV=1 pdm lock

# Install only production dependencies (skip dev)
RUN PDM_IGNORE_VENV=1 pdm install --prod

# Copy the rest of the code to /action
COPY colorblind_snapshot_analyzer colorblind_snapshot_analyzer

# Set PYTHONPATH so Python can find your package
ENV PYTHONPATH=/action

# After the PDM install step, get the path to the venv
RUN VENV_PATH=$(pdm info -v) && echo "Using venv at $VENV_PATH"

# Set environment variables so the container uses the venv python and libs by default
ENV VIRTUAL_ENV=$VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# Set entrypoint to run your main module
ENTRYPOINT ["python", "-m", "colorblind_snapshot_analyzer.main"]
