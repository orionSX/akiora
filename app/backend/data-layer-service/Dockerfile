FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY ../shared/ /shared/

COPY ./data-layer-service/pyproject.toml ./

RUN uv pip install --system .

COPY ./data-layer-service .





EXPOSE 8000

