FROM python:3.12 AS builder

RUN apt-get update && apt-get install -y build-essential curl
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh
COPY ./requirements.lock .
RUN /root/.cargo/bin/uv venv /opt/venv && \
    /root/.cargo/bin/uv pip install --no-cache -r requirements.lock

# run stage
FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y locales locales-all
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .

CMD ["python", "-m", "bot.main"]
