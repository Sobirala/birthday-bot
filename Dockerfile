FROM pypy:3.9-7.3.9-slim as compiler

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app/

RUN pypy -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pypy -m pip install --upgrade pip

# Install build essentials
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean
RUN pypy -m pip install wheel

# Install pip requirements
COPY requirements.txt /app/requirements.txt
RUN pypy -m pip install -r requirements.txt

FROM pypy:3.9-7.3.9-slim as runner

WORKDIR /app/
COPY --from=compiler /opt/venv /opt/venv

# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden.
CMD ["pypy", "main.py"]
