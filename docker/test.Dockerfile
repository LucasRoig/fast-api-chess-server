FROM python:3.9.2

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY poetry.lock pyproject.toml ./

RUN pip install poetry && \
    poetry config virtualenvs.create false --local && \
    poetry install

COPY . ./

CMD alembic upgrade head && pytest
