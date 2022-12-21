ARG PYTHON_VERSION=3.11
# build stage
FROM python:${PYTHON_VERSION}-slim AS builder

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock /bot/

# install dependencies and project into the local packages directory
WORKDIR /bot
RUN mkdir __pypackages__ && pdm install --prod --no-lock --no-editable


# run stage
FROM python:${PYTHON_VERSION}-slim
ARG PYTHON_VERSION

# retrieve packages from build stage
COPY bot/ /bot/
ENV PYTHONPATH=/bot/pkgs
COPY --from=builder /bot/__pypackages__/${PYTHON_VERSION}/lib /bot/pkgs

# set command/entrypoint, adapt to fit your needs
CMD ["python", "-m", "bot"]
