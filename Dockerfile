FROM ghcr.io/astral-sh/uv:0.12.7-python3.12-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROOFRAG_HOST=0.0.0.0 \
    PROOFRAG_PORT=8000 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --locked --no-dev

COPY data/demo-corpus ./data/demo-corpus
COPY data/evaluation ./data/evaluation
RUN mkdir -p data/uploads data/evaluation-results

EXPOSE 8000

CMD ["uv", "run", "--locked", "--no-sync", "proofrag"]

