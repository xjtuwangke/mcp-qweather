FROM python:3.13-slim

WORKDIR /app

RUN uv pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('localhost',8000)); s.close()" || exit 1

EXPOSE 8000

CMD ["uv", "run", "python", "server.py", "--http"]
