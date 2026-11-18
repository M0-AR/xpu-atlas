FROM python:3.12-slim

LABEL org.opencontainers.image.title="XPU-Atlas" \
      org.opencontainers.image.description="A reproducible evidence atlas of twenty processing-unit paradigms" \
      org.opencontainers.image.source="https://github.com/M0-AR/xpu-atlas" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="0.1.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    PYTHONPATH=/app/src:/app

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
COPY sim ./sim
COPY Makefile ./
COPY figures ./figures
COPY results ./results
COPY assets ./assets
COPY preview.html index.html .nojekyll ./

CMD ["make", "all"]
