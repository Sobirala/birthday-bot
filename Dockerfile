ARG PYTHON=3.11
# build stage
FROM python:${PYTHON}-slim AS builder
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# run stage
FROM python:${PYTHON}-slim
RUN apt-get update && apt-get install -y locales locales-all
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .
CMD ["python", "-m", "bot"]
