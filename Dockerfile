FROM python:3.10 as build

WORKDIR /opt
COPY ["pyproject.toml", "poetry.lock", "midgard_discord", "./"]
RUN python -m venv venv
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root

# FROM python:3.10-slim as release

# COPY --from=build /opt/venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"
# CMD ["midgard-bot"]
