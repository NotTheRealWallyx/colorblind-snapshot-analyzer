FROM python:3.13.5-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Set workdir to /action so code is not hidden by /github/workspace mount
WORKDIR /action

# Copy requirements.txt and README.md
COPY requirements.txt README.md ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code to /action
COPY colorblind_snapshot_analyzer colorblind_snapshot_analyzer

# Set PYTHONPATH so Python can find your package
ENV PYTHONPATH=/action

# Set entrypoint to run your main module
ENTRYPOINT ["python", "-m", "colorblind_snapshot_analyzer.main"]
