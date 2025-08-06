FROM python:3.13-slim

WORKDIR /app

RUN pip install uv


COPY pyproject.toml ./
COPY . .


RUN uv pip install --system .


EXPOSE 8000

