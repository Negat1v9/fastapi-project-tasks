FROM python:3.11.4

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    # poetry
    POETRY_VERSION=1.5.1

RUN apt-get update && \
    pip3 install "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY . ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-root
