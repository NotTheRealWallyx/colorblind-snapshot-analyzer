FROM python:3.13.5-slim

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

WORKDIR /action

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir pdm

COPY pyproject.toml README.md ./

RUN PDM_IGNORE_VENV=1 pdm lock

RUN PDM_IGNORE_VENV=1 pdm install --prod

ENV VIRTUAL_ENV=/action/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY colorblind_snapshot_analyzer colorblind_snapshot_analyzer

ENV PYTHONPATH=/action

ENTRYPOINT ["python", "-m", "colorblind_snapshot_analyzer.main"]
