ARG PYTHON=3.12-slim-bookworm
# build stage
FROM python:${PYTHON} AS builder

ENV PATH /opt/venv/bin:$PATH
WORKDIR /opt
RUN python -m venv venv
RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root --only main

# run stage
FROM python:${PYTHON}
RUN apt-get update && apt-get install -y locales locales-all
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .

CMD ["python", "-m", "bot.main"]
