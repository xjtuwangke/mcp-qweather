FROM python:3.13-slim

WORKDIR /app

RUN uv pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uv", "run", "python", "server.py"]
