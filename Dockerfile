# Stage 1: Install dependencies and build the project
FROM python:3.10 as builder

WORKDIR /app
COPY ["pyproject.toml", "poetry.lock", "README.md", "./"]
COPY ["midgard_discord", "./midgard_discord"]

RUN pip install --upgrade pip \
  && pip install poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev
RUN poetry build

RUN python -m venv /opt/venv
RUN /opt/venv/bin/pip install /app/dist/*.whl

# Stage 2: Create the final image with a slim Python base image
FROM python:3.10-slim

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

CMD ["midgard-bot"]
