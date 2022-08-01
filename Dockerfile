# syntax=docker/dockerfile:1

# Temporary image
ARG PYTHON_VERSION=3.10-slim-bullseye
FROM python:${PYTHON_VERSION} as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONNUMBUFFERED 1

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/* \
    && /usr/local/bin/python -m pip install --upgrade pip

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


## Final image

FROM python:${PYTHON_VERSION}

RUN useradd -ms /bin/sh worker
USER worker
WORKDIR /app

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY --from=builder /app/wheels /wheels
COPY --chown=worker:worker --from=builder /app/requirements.txt .

ENV PATH="/home/worker/.local/bin:${PATH}"

RUN pip install --user --no-cache /wheels/*

COPY --chown=worker:worker . .

LABEL org.opencontainers.image.authors="cedric.roger@ville-noumea.nc" \
      maintainer="cedric.roger@ville-noumea.nc" \
      version="0.1.0"


#CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
ENTRYPOINT ["./gunicorn_starter.sh"]

