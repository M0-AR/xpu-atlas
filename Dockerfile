FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e . --no-deps

COPY data ./data
COPY tests ./tests
COPY docs ./docs
COPY scripts ./scripts
COPY Makefile ./
COPY figures ./figures
COPY results ./results
COPY assets ./assets
COPY preview.html index.html .nojekyll ./

CMD ["make", "all"]
